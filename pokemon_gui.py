from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from tkinter import StringVar, Tk
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "pokemon_stats.csv"
NATURES_PATH = DATA_DIR / "natures.json"

STAT_FIELDS = [
    ("hp", "HP"),
    ("attack", "공격"),
    ("defense", "방어"),
    ("special_attack", "특수공격"),
    ("special_defense", "특수방어"),
    ("speed", "스피드"),
]
STAT_KEY_TO_API = {
    "hp": "hp",
    "attack": "attack",
    "defense": "defense",
    "special_attack": "special-attack",
    "special_defense": "special-defense",
    "speed": "speed",
}


@dataclass
class PokemonRecord:
    species_id: int
    pokemon_id: int
    name_ko: str
    name_en: str
    generation: str
    is_legendary: bool
    is_mythical: bool
    types_ko: list[str]
    height_m: float
    weight_kg: float
    base_stats: dict[str, int]
    total: int
    image_path: Path | None

    @property
    def display_name(self) -> str:
        return f"{self.species_id:04d} - {self.name_ko} / {self.name_en.title()}"


@dataclass
class Nature:
    name_en: str
    name_ko: str
    increased_stat: str | None
    decreased_stat: str | None

    @property
    def display_name(self) -> str:
        return f"{self.name_ko} ({self.name_en.title()})"

    def multiplier_for(self, stat_key: str) -> float:
        api_name = STAT_KEY_TO_API[stat_key]
        if api_name == self.increased_stat:
            return 1.1
        if api_name == self.decreased_stat:
            return 0.9
        return 1.0


def load_pokemon_data() -> list[PokemonRecord]:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    records: list[PokemonRecord] = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            image_path = BASE_DIR / row["image_file"] if row.get("image_file") else None
            records.append(
                PokemonRecord(
                    species_id=int(row["species_id"]),
                    pokemon_id=int(row["pokemon_id"]),
                    name_ko=row["name_ko"],
                    name_en=row["name_en"],
                    generation=row["generation"],
                    is_legendary=bool(int(row["is_legendary"])),
                    is_mythical=bool(int(row["is_mythical"])),
                    types_ko=[item for item in row["types_ko"].split("|") if item],
                    height_m=float(row["height_m"]),
                    weight_kg=float(row["weight_kg"]),
                    base_stats={
                        "hp": int(row["hp"]),
                        "attack": int(row["attack"]),
                        "defense": int(row["defense"]),
                        "special_attack": int(row["special_attack"]),
                        "special_defense": int(row["special_defense"]),
                        "speed": int(row["speed"]),
                    },
                    total=int(row["total"]),
                    image_path=image_path if image_path and image_path.exists() else None,
                )
            )
    return records


def load_natures() -> list[Nature]:
    if not NATURES_PATH.exists():
        raise FileNotFoundError(f"Nature JSON not found: {NATURES_PATH}")
    with NATURES_PATH.open("r", encoding="utf-8") as json_file:
        payload = json.load(json_file)

    natures = [
        Nature(
            name_en=item["name_en"],
            name_ko=item["name_ko"],
            increased_stat=item.get("increased_stat"),
            decreased_stat=item.get("decreased_stat"),
        )
        for item in payload
    ]
    natures.sort(key=lambda item: item.name_en)
    return natures


class PokemonStatApp:
    def __init__(self, root: Tk, records: list[PokemonRecord], natures: list[Nature]) -> None:
        self.root = root
        self.records = records
        self.natures = natures
        self.records_by_display = {record.display_name: record for record in records}
        self.search_index = self._build_search_index(records)
        self.natures_by_display = {nature.display_name: nature for nature in natures}
        self.image_cache: ImageTk.PhotoImage | None = None

        self.root.title("Pokemon Stat Viewer")
        self.root.geometry("1180x760")
        self.root.minsize(1080, 720)

        self.selected_pokemon = StringVar(value=records[0].display_name if records else "")
        self.selected_nature = StringVar(value=natures[0].display_name if natures else "")
        self.level_var = StringVar(value="50")
        self.search_hint_var = StringVar(value="")
        self.summary_var = StringVar(value="")
        self.ev_total_var = StringVar(value="EV 합계: 0 / 510")
        self.image_status_var = StringVar(value="이미지 없음")

        self.base_stat_vars: dict[str, StringVar] = {}
        self.final_stat_vars: dict[str, StringVar] = {}
        self.nature_stat_vars: dict[str, StringVar] = {}
        self.iv_vars = {key: StringVar(value="31") for key, _ in STAT_FIELDS}
        self.ev_vars = {key: StringVar(value="0") for key, _ in STAT_FIELDS}

        self._build_ui()
        self._bind_events()
        self.update_from_selection()

    @staticmethod
    def _build_search_index(records: list[PokemonRecord]) -> dict[str, PokemonRecord]:
        index: dict[str, PokemonRecord] = {}
        for record in records:
            candidates = {
                record.display_name.lower(),
                record.name_ko.lower(),
                record.name_en.lower(),
                record.name_en.replace("-", " ").lower(),
                f"{record.species_id}",
                f"{record.species_id:04d}",
            }
            for candidate in candidates:
                index[candidate] = record
        return index

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(0, weight=1)

        left = ttk.Frame(frame)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)

        right = ttk.Frame(frame)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)

        info_box = ttk.LabelFrame(left, text="포켓몬 선택", padding=12)
        info_box.grid(row=0, column=0, sticky="ew")
        info_box.columnconfigure(1, weight=1)

        ttk.Label(info_box, text="이름 또는 번호").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.pokemon_combo = ttk.Combobox(
            info_box,
            textvariable=self.selected_pokemon,
            values=[record.display_name for record in self.records],
            state="normal",
        )
        self.pokemon_combo.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(info_box, textvariable=self.search_hint_var, foreground="#555").grid(
            row=1, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        ttk.Label(info_box, text="레벨").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        ttk.Spinbox(info_box, from_=1, to=100, textvariable=self.level_var, width=10).grid(
            row=2, column=1, sticky="w", pady=4
        )

        ttk.Label(info_box, text="성격").grid(row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.nature_combo = ttk.Combobox(
            info_box,
            textvariable=self.selected_nature,
            values=[nature.display_name for nature in self.natures],
            state="readonly",
        )
        self.nature_combo.grid(row=3, column=1, sticky="ew", pady=4)

        ttk.Label(info_box, textvariable=self.summary_var, justify="left").grid(
            row=4, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        iv_box = ttk.LabelFrame(left, text="IV / EV 입력", padding=12)
        iv_box.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        for column in range(4):
            iv_box.columnconfigure(column, weight=1)

        ttk.Label(iv_box, text="능력치").grid(row=0, column=0, sticky="w")
        ttk.Label(iv_box, text="종족값").grid(row=0, column=1, sticky="w")
        ttk.Label(iv_box, text="IV").grid(row=0, column=2, sticky="w")
        ttk.Label(iv_box, text="EV").grid(row=0, column=3, sticky="w")

        for row_index, (stat_key, label) in enumerate(STAT_FIELDS, start=1):
            self.base_stat_vars[stat_key] = StringVar(value="-")
            self.final_stat_vars[stat_key] = StringVar(value="-")
            self.nature_stat_vars[stat_key] = StringVar(value="-")

            ttk.Label(iv_box, text=label).grid(row=row_index, column=0, sticky="w", pady=3)
            ttk.Label(iv_box, textvariable=self.base_stat_vars[stat_key]).grid(
                row=row_index, column=1, sticky="w", pady=3
            )
            ttk.Spinbox(iv_box, from_=0, to=31, textvariable=self.iv_vars[stat_key], width=10).grid(
                row=row_index, column=2, sticky="w", pady=3
            )
            ttk.Spinbox(iv_box, from_=0, to=252, increment=4, textvariable=self.ev_vars[stat_key], width=10).grid(
                row=row_index, column=3, sticky="w", pady=3
            )

        control_row = ttk.Frame(iv_box)
        control_row.grid(row=len(STAT_FIELDS) + 1, column=0, columnspan=4, sticky="ew", pady=(10, 0))
        ttk.Button(control_row, text="IV 31 / EV 0", command=self.reset_iv_ev).pack(side="left")
        ttk.Label(control_row, textvariable=self.ev_total_var).pack(side="right")

        result_box = ttk.LabelFrame(left, text="계산 결과", padding=12)
        result_box.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        for column in range(3):
            result_box.columnconfigure(column, weight=1)
        ttk.Label(result_box, text="능력치").grid(row=0, column=0, sticky="w")
        ttk.Label(result_box, text="성격 보정").grid(row=0, column=1, sticky="w")
        ttk.Label(result_box, text="최종 값").grid(row=0, column=2, sticky="w")

        for row_index, (stat_key, label) in enumerate(STAT_FIELDS, start=1):
            ttk.Label(result_box, text=label).grid(row=row_index, column=0, sticky="w", pady=3)
            ttk.Label(result_box, textvariable=self.nature_stat_vars[stat_key]).grid(
                row=row_index, column=1, sticky="w", pady=3
            )
            ttk.Label(result_box, textvariable=self.final_stat_vars[stat_key], font=("Segoe UI", 11, "bold")).grid(
                row=row_index, column=2, sticky="w", pady=3
            )

        image_box = ttk.LabelFrame(right, text="포켓몬 이미지", padding=12)
        image_box.grid(row=0, column=0, sticky="nsew")
        image_box.columnconfigure(0, weight=1)
        image_box.rowconfigure(0, weight=1)

        self.image_label = ttk.Label(image_box, anchor="center")
        self.image_label.grid(row=0, column=0, sticky="nsew")
        ttk.Label(image_box, textvariable=self.image_status_var).grid(row=1, column=0, sticky="ew", pady=(8, 0))

    def _bind_events(self) -> None:
        self.pokemon_combo.bind("<<ComboboxSelected>>", lambda _event: self.update_from_selection())
        self.pokemon_combo.bind("<Return>", lambda _event: self.update_from_selection())
        self.pokemon_combo.bind("<FocusOut>", lambda _event: self.update_from_selection())
        self.nature_combo.bind("<<ComboboxSelected>>", lambda _event: self.recalculate())

        for variable in [self.level_var, *self.iv_vars.values(), *self.ev_vars.values()]:
            variable.trace_add("write", lambda *_args: self.recalculate())

    def find_record(self, raw_value: str) -> PokemonRecord | None:
        value = raw_value.strip().lower()
        if not value:
            return None
        if raw_value in self.records_by_display:
            return self.records_by_display[raw_value]
        return self.search_index.get(value)

    def current_nature(self) -> Nature:
        selected = self.selected_nature.get()
        return self.natures_by_display[selected]

    def reset_iv_ev(self) -> None:
        for variable in self.iv_vars.values():
            variable.set("31")
        for variable in self.ev_vars.values():
            variable.set("0")

    def parse_bounded_int(self, value: str, minimum: int, maximum: int, fallback: int) -> int:
        try:
            parsed = int(value)
        except ValueError:
            return fallback
        return max(minimum, min(maximum, parsed))

    def update_from_selection(self) -> None:
        record = self.find_record(self.selected_pokemon.get())
        if record is None:
            self.search_hint_var.set("이름, 영문명, 도감 번호로 검색할 수 있습니다.")
            return

        self.selected_pokemon.set(record.display_name)
        self.search_hint_var.set(f"검색 인식: {record.name_ko} / {record.name_en.title()}")
        self.summary_var.set(
            "\n".join(
                [
                    f"타입: {' / '.join(record.types_ko)}",
                    f"키: {record.height_m:.1f} m    몸무게: {record.weight_kg:.1f} kg",
                    f"분류: {record.generation}    전설: {'예' if record.is_legendary else '아니오'}    환상: {'예' if record.is_mythical else '아니오'}",
                ]
            )
        )
        self.update_image(record)
        self.recalculate()

    def update_image(self, record: PokemonRecord) -> None:
        if not record.image_path or not record.image_path.exists():
            self.image_label.configure(image="", text="이미지 파일이 없습니다.")
            self.image_cache = None
            self.image_status_var.set("이미지 없음")
            return

        image = Image.open(record.image_path).convert("RGBA")
        image.thumbnail((360, 360))
        self.image_cache = ImageTk.PhotoImage(image)
        self.image_label.configure(image=self.image_cache, text="")
        self.image_status_var.set(str(record.image_path.relative_to(BASE_DIR)))

    def recalculate(self) -> None:
        record = self.find_record(self.selected_pokemon.get())
        if record is None:
            for stat_key, _label in STAT_FIELDS:
                self.base_stat_vars[stat_key].set("-")
                self.final_stat_vars[stat_key].set("-")
                self.nature_stat_vars[stat_key].set("-")
            return

        level = self.parse_bounded_int(self.level_var.get(), 1, 100, 50)
        if str(level) != self.level_var.get():
            self.level_var.set(str(level))

        nature = self.current_nature()

        total_ev = 0
        for stat_key, _label in STAT_FIELDS:
            base = record.base_stats[stat_key]
            iv = self.parse_bounded_int(self.iv_vars[stat_key].get(), 0, 31, 31)
            ev = self.parse_bounded_int(self.ev_vars[stat_key].get(), 0, 252, 0)

            if self.iv_vars[stat_key].get() != str(iv):
                self.iv_vars[stat_key].set(str(iv))
            if self.ev_vars[stat_key].get() != str(ev):
                self.ev_vars[stat_key].set(str(ev))

            total_ev += ev
            self.base_stat_vars[stat_key].set(str(base))

            nature_multiplier = nature.multiplier_for(stat_key)
            self.nature_stat_vars[stat_key].set(f"x{nature_multiplier:.1f}")
            self.final_stat_vars[stat_key].set(str(self.calculate_stat(stat_key, base, iv, ev, level, nature_multiplier)))

        if total_ev > 510:
            self.ev_total_var.set(f"EV 합계: {total_ev} / 510  (초과)")
        else:
            self.ev_total_var.set(f"EV 합계: {total_ev} / 510")

    @staticmethod
    def calculate_stat(stat_key: str, base: int, iv: int, ev: int, level: int, nature_multiplier: float) -> int:
        core_value = ((2 * base + iv + (ev // 4)) * level) // 100
        if stat_key == "hp":
            if base == 1:
                return 1
            return core_value + level + 10
        return int((core_value + 5) * nature_multiplier)


def main() -> None:
    try:
        records = load_pokemon_data()
        natures = load_natures()
    except FileNotFoundError as exc:
        messagebox.showerror("파일 없음", f"{exc}\n\n먼저 download_pokemon_data.py 를 실행해주세요.")
        return

    root = Tk()
    app = PokemonStatApp(root, records, natures)
    if not app.records or not app.natures:
        messagebox.showerror("데이터 오류", "로드된 포켓몬 또는 성격 데이터가 없습니다.")
        return
    root.mainloop()


if __name__ == "__main__":
    main()
