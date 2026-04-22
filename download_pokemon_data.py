from __future__ import annotations

import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGE_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "pokemon_stats.csv"
NATURES_PATH = DATA_DIR / "natures.json"
TYPE_NAMES_PATH = DATA_DIR / "types.json"

API_ROOT = "https://pokeapi.co/api/v2"
SPECIES_LIST_URL = f"{API_ROOT}/pokemon-species?limit=2000"
NATURE_LIST_URL = f"{API_ROOT}/nature?limit=100"
TYPE_LIST_URL = f"{API_ROOT}/type?limit=100"
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python Pokemon Downloader",
    "Accept": "application/json,image/png,image/*;q=0.8,*/*;q=0.5",
}

STAT_ORDER = [
    ("hp", "hp"),
    ("attack", "attack"),
    ("defense", "defense"),
    ("special-attack", "special_attack"),
    ("special-defense", "special_defense"),
    ("speed", "speed"),
]
POKEDEX_LIMIT = 1025


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def fetch_json(url: str, retries: int = 3, delay: float = 0.5) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers=REQUEST_HEADERS)
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(delay * attempt)
    raise RuntimeError(f"Failed to fetch JSON from {url}: {last_error}") from last_error


def fetch_bytes(url: str, retries: int = 3, delay: float = 0.5) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers=REQUEST_HEADERS)
            with urlopen(request, timeout=30) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt == retries:
                break
            time.sleep(delay * attempt)
    raise RuntimeError(f"Failed to fetch bytes from {url}: {last_error}") from last_error


def localized_name(entries: list[dict[str, Any]], language_code: str) -> str | None:
    for entry in entries:
        language = entry.get("language", {})
        if language.get("name") == language_code:
            return entry.get("name")
    return None


def safe_slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return value.strip("_") or "pokemon"


def load_species_index() -> list[dict[str, Any]]:
    print("Fetching species list...")
    species_list = fetch_json(SPECIES_LIST_URL)
    results = species_list.get("results", [])
    filtered = []
    for item in results:
        match = re.search(r"/pokemon-species/(\d+)/?$", item["url"])
        if not match:
            continue
        species_id = int(match.group(1))
        if species_id <= POKEDEX_LIMIT:
            filtered.append({"species_id": species_id, "url": item["url"]})
    filtered.sort(key=lambda item: item["species_id"])
    print(f"Found {len(filtered)} main-series species.")
    return filtered


def fetch_species_detail(species_entry: dict[str, Any]) -> dict[str, Any]:
    detail = fetch_json(species_entry["url"])
    default_variety = next(
        (item for item in detail.get("varieties", []) if item.get("is_default")),
        None,
    )
    if not default_variety:
        raise RuntimeError(f"No default variety found for species {detail['name']}")

    return {
        "species_id": species_entry["species_id"],
        "species_name_en": detail["name"],
        "species_name_ko": localized_name(detail.get("names", []), "ko") or detail["name"].title(),
        "generation": detail.get("generation", {}).get("name", ""),
        "is_legendary": detail.get("is_legendary", False),
        "is_mythical": detail.get("is_mythical", False),
        "pokemon_url": default_variety["pokemon"]["url"],
    }


def fetch_pokemon_detail(species_detail: dict[str, Any]) -> dict[str, Any]:
    pokemon = fetch_json(species_detail["pokemon_url"])
    stats = {api_name: 0 for api_name, _ in STAT_ORDER}
    for stat in pokemon.get("stats", []):
        stat_name = stat.get("stat", {}).get("name")
        if stat_name in stats:
            stats[stat_name] = stat.get("base_stat", 0)

    official_artwork = (
        pokemon.get("sprites", {})
        .get("other", {})
        .get("official-artwork", {})
        .get("front_default")
    )
    fallback_sprite = pokemon.get("sprites", {}).get("front_default")
    image_url = official_artwork or fallback_sprite

    return {
        **species_detail,
        "pokemon_id": pokemon["id"],
        "height_m": pokemon.get("height", 0) / 10,
        "weight_kg": pokemon.get("weight", 0) / 10,
        "types_en": [item["type"]["name"] for item in pokemon.get("types", [])],
        "stats": stats,
        "image_url": image_url,
    }


def fetch_natures() -> list[dict[str, Any]]:
    print("Fetching nature data...")
    nature_index = fetch_json(NATURE_LIST_URL)
    nature_urls = [item["url"] for item in nature_index.get("results", [])]
    natures: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_json, url) for url in nature_urls]
        for future in as_completed(futures):
            detail = future.result()
            natures.append(
                {
                    "name_en": detail["name"],
                    "name_ko": localized_name(detail.get("names", []), "ko") or detail["name"].title(),
                    "increased_stat": (detail.get("increased_stat") or {}).get("name"),
                    "decreased_stat": (detail.get("decreased_stat") or {}).get("name"),
                }
            )
    natures.sort(key=lambda item: item["name_en"])
    return natures


def fetch_type_names() -> dict[str, str]:
    print("Fetching localized type names...")
    type_index = fetch_json(TYPE_LIST_URL)
    type_urls = [item["url"] for item in type_index.get("results", [])]
    mapping: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_json, url) for url in type_urls]
        for future in as_completed(futures):
            detail = future.result()
            english_name = detail["name"]
            if english_name == "unknown":
                continue
            mapping[english_name] = localized_name(detail.get("names", []), "ko") or english_name.title()
    return dict(sorted(mapping.items()))


def build_rows(type_names: dict[str, str]) -> list[dict[str, Any]]:
    species_index = load_species_index()
    print("Fetching per-species data from PokeAPI...")
    species_details: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_species_detail, entry) for entry in species_index]
        for index, future in enumerate(as_completed(futures), start=1):
            species_details.append(future.result())
            if index % 50 == 0:
                print(f"  species details: {index}/{len(species_index)}")

    species_details.sort(key=lambda item: item["species_id"])

    pokemon_rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_pokemon_detail, detail) for detail in species_details]
        for index, future in enumerate(as_completed(futures), start=1):
            pokemon_rows.append(future.result())
            if index % 50 == 0:
                print(f"  pokemon details: {index}/{len(species_details)}")

    pokemon_rows.sort(key=lambda item: item["species_id"])

    rows: list[dict[str, Any]] = []
    for item in pokemon_rows:
        stat_values = item["stats"]
        image_file = ""
        if item["image_url"]:
            filename = f"{item['species_id']:04d}_{safe_slug(item['species_name_en'])}.png"
            image_file = str((IMAGE_DIR / filename).relative_to(BASE_DIR))

        rows.append(
            {
                "species_id": item["species_id"],
                "pokemon_id": item["pokemon_id"],
                "name_ko": item["species_name_ko"],
                "name_en": item["species_name_en"],
                "generation": item["generation"],
                "is_legendary": int(item["is_legendary"]),
                "is_mythical": int(item["is_mythical"]),
                "types_en": "|".join(item["types_en"]),
                "types_ko": "|".join(type_names.get(type_name, type_name.title()) for type_name in item["types_en"]),
                "height_m": f"{item['height_m']:.1f}",
                "weight_kg": f"{item['weight_kg']:.1f}",
                "hp": stat_values["hp"],
                "attack": stat_values["attack"],
                "defense": stat_values["defense"],
                "special_attack": stat_values["special-attack"],
                "special_defense": stat_values["special-defense"],
                "speed": stat_values["speed"],
                "total": sum(stat_values.values()),
                "image_file": image_file,
                "image_url": item["image_url"] or "",
            }
        )

    return rows


def write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "species_id",
        "pokemon_id",
        "name_ko",
        "name_en",
        "generation",
        "is_legendary",
        "is_mythical",
        "types_en",
        "types_ko",
        "height_m",
        "weight_kg",
        "hp",
        "attack",
        "defense",
        "special_attack",
        "special_defense",
        "speed",
        "total",
        "image_file",
        "image_url",
    ]
    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote CSV: {CSV_PATH}")


def write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)
    print(f"Wrote JSON: {path}")


def download_image(row: dict[str, Any]) -> None:
    image_url = row.get("image_url")
    image_file = row.get("image_file")
    if not image_url or not image_file:
        return
    output_path = BASE_DIR / image_file
    if output_path.exists():
        return
    output_path.write_bytes(fetch_bytes(image_url))


def download_images(rows: list[dict[str, Any]]) -> None:
    print("Downloading artwork images...")
    completed = 0
    total = len(rows)
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(download_image, row) for row in rows]
        for future in as_completed(futures):
            future.result()
            completed += 1
            if completed % 50 == 0:
                print(f"  images: {completed}/{total}")


def main() -> int:
    ensure_dirs()
    type_names = fetch_type_names()
    natures = fetch_natures()
    rows = build_rows(type_names)
    write_json(TYPE_NAMES_PATH, type_names)
    write_json(NATURES_PATH, natures)
    write_csv(rows)
    download_images(rows)
    print("All done.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.", file=sys.stderr)
        raise SystemExit(130)
