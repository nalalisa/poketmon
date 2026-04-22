import tkinter
from tkinter import ttk, messagebox
import urllib.request
import json
import io
import csv
import os
from PIL import Image, ImageTk

# ------------------------------------------------------------------
# 1. 파일에서 모든 포켓몬 이름과 성격 데이터 불러오기
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "..", "data", "pokemon_stats.csv")
NATURE_PATH = os.path.join(BASE_DIR, "..", "data", "natures.json")

korean_to_id = {}
pokemon_names = []

if os.path.exists(CSV_PATH):
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            korean_to_id[row["name_ko"]] = row["pokemon_id"]
            pokemon_names.append(row["name_ko"])

natures_data = {}
nature_names = []

if os.path.exists(NATURE_PATH):
    with open(NATURE_PATH, "r", encoding="utf-8") as f:
        nature_list = json.load(f)
        for n in nature_list:
            natures_data[n["name_ko"]] = {"up": n["increased_stat"], "down": n["decreased_stat"]}
            nature_names.append(n["name_ko"])

stat_api_names = {"HP": "hp", "공격": "attack", "방어": "defense", "특수공격": "special-attack", "특수방어": "special-defense", "스피드": "speed"}
current_base_stats = {"HP": 0, "공격": 0, "방어": 0, "특수공격": 0, "특수방어": 0, "스피드": 0}

iv_inputs = {}
ev_inputs = {}
base_labels = {}
final_labels = {}

# ------------------------------------------------------------------
# 2. 검색 및 API 호출 함수
# ------------------------------------------------------------------
def search_pokemon(*args):
    name = search_combo.get()
    if name not in korean_to_id: return
    pokemon_id = korean_to_id[name]
    
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        stats = data["stats"]
        current_base_stats["HP"] = stats[0]["base_stat"]
        current_base_stats["공격"] = stats[1]["base_stat"]
        current_base_stats["방어"] = stats[2]["base_stat"]
        current_base_stats["특수공격"] = stats[3]["base_stat"]
        current_base_stats["특수방어"] = stats[4]["base_stat"]
        current_base_stats["스피드"] = stats[5]["base_stat"]
        
        for stat in current_base_stats:
            base_labels[stat].config(text=str(current_base_stats[stat]))
        
        image_url = data["sprites"]["other"]["official-artwork"]["front_default"]
        if image_url:
            img_req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            img_data = urllib.request.urlopen(img_req).read()
            img = Image.open(io.BytesIO(img_data)).resize((180, 180))
            photo = ImageTk.PhotoImage(img)
            image_label.config(image=photo, text="")
            image_label.image = photo
            
        title_label.config(text=f"No.{pokemon_id} : {name}")
        calculate_all_stats()
    except: pass

# ------------------------------------------------------------------
# 3. 실전 능력치 자동 계산 함수 (정답 코드!)
# ------------------------------------------------------------------
def calculate_all_stats(*args):
    if current_base_stats["HP"] == 0: return
        
    try: level = int(level_input.get())
    except: level = 50
        
    nature_info = natures_data.get(nature_combo.get(), {"up": None, "down": None})
    
    def get_multiplier(stat_name_kr):
        api_name = stat_api_names[stat_name_kr]
        if nature_info["up"] == api_name: return 1.1
        elif nature_info["down"] == api_name: return 0.9
        else: return 1.0

    # 1. HP 계산하기
    base_hp = current_base_stats["HP"]
    try:
        # 정답: 화면 빈칸(iv_inputs["HP"])에서 글씨를 가져와서 숫자(int)로 바꿉니다!
        iv_hp = int(iv_inputs["HP"].get())
        ev_hp = int(ev_inputs["HP"].get())
    except ValueError:
        iv_hp, ev_hp = 0, 0
    
    final_hp = int(((base_hp * 2 + iv_hp + (ev_hp // 4)) * level) / 100) + level + 10
    final_labels["HP"].config(text=str(final_hp))
    
    # 2. 나머지 5개 능력치 계산하기
    for stat_name in ["공격", "방어", "특수공격", "특수방어", "스피드"]:
        base = current_base_stats[stat_name]
        try:
            # 정답: 각 이름(stat_name)에 맞는 빈칸에서 글씨를 가져와서 숫자로 바꿉니다!
            iv = int(iv_inputs[stat_name].get())
            ev = int(ev_inputs[stat_name].get())
        except ValueError:
            iv, ev = 0, 0
            
        core = int(((base * 2 + iv + (ev // 4)) * level) / 100) + 5
        multi = get_multiplier(stat_name)
        
        final_val = int(core * multi)
        arrow = "🔺" if multi == 1.1 else "🔻" if multi == 0.9 else ""
        final_labels[stat_name].config(text=f"{final_val} {arrow}")

# ------------------------------------------------------------------
# 4. 도감 화면(GUI) 그리기
# ------------------------------------------------------------------
window = tkinter.Tk()
window.title("10단계 정답! 프로게이머 포켓몬 도감")
window.geometry("450x750")
window.configure(bg="#E3F2FD")

search_frame = tkinter.Frame(window, bg="#E3F2FD")
search_frame.pack(pady=10)
search_combo = ttk.Combobox(search_frame, values=pokemon_names, font=("맑은 고딕", 12), width=12)
search_combo.pack(side="left", padx=5)
search_combo.bind("<Return>", search_pokemon)
if pokemon_names: search_combo.set("망나뇽" if "망나뇽" in pokemon_names else pokemon_names[0])
tkinter.Button(search_frame, text="검색", command=search_pokemon).pack(side="left")

title_label = tkinter.Label(window, text="포켓몬을 검색해 주세요!", font=("맑은 고딕", 16, "bold"), bg="#E3F2FD")
title_label.pack()

image_label = tkinter.Label(window, bg="#E3F2FD")
image_label.pack()

input_frame = tkinter.Frame(window, bg="#E3F2FD")
input_frame.pack(pady=5)
tkinter.Label(input_frame, text="레벨:", bg="#E3F2FD").grid(row=0, column=0)
level_input = tkinter.Entry(input_frame, width=5)
level_input.grid(row=0, column=1)
level_input.insert(0, "50")
level_input.bind("<KeyRelease>", calculate_all_stats)

tkinter.Label(input_frame, text="성격:", bg="#E3F2FD").grid(row=0, column=2, padx=(15,0))
nature_combo = ttk.Combobox(input_frame, values=nature_names, width=8, state="readonly")
nature_combo.grid(row=0, column=3)
if nature_names: nature_combo.set("명랑" if "명랑" in nature_names else nature_names[0])
nature_combo.bind("<<ComboboxSelected>>", calculate_all_stats)

stats_frame = tkinter.Frame(window, bg="#E3F2FD")
stats_frame.pack(pady=15)

headers = ["능력치", "종족값", "재능(IV)", "노력(EV)", "최종"]
for col, text in enumerate(headers):
    tkinter.Label(stats_frame, text=text, font=("맑은 고딕", 10, "bold"), bg="#E3F2FD", width=8).grid(row=0, column=col)

stats_list = ["HP", "공격", "방어", "특수공격", "특수방어", "스피드"]
for row, stat in enumerate(stats_list, start=1):
    tkinter.Label(stats_frame, text=stat, bg="#E3F2FD", font=("맑은 고딕", 10, "bold")).grid(row=row, column=0, pady=5)
    
    base_labels[stat] = tkinter.Label(stats_frame, text="0", bg="#E3F2FD")
    base_labels[stat].grid(row=row, column=1)
    
    iv_inputs[stat] = tkinter.Entry(stats_frame, width=5, justify="center")
    iv_inputs[stat].insert(0, "31")
    iv_inputs[stat].grid(row=row, column=2)
    iv_inputs[stat].bind("<KeyRelease>", calculate_all_stats)
    
    ev_inputs[stat] = tkinter.Entry(stats_frame, width=5, justify="center")
    ev_inputs[stat].insert(0, "0")
    ev_inputs[stat].grid(row=row, column=3)
    ev_inputs[stat].bind("<KeyRelease>", calculate_all_stats)
    
    final_labels[stat] = tkinter.Label(stats_frame, text="0", bg="#E3F2FD", font=("맑은 고딕", 12, "bold"), fg="blue")
    final_labels[stat].grid(row=row, column=4)

search_pokemon()
window.mainloop()