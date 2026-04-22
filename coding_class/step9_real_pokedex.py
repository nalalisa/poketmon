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
pokemon_names = []  # 검색창 자동완성을 위한 리스트

if os.path.exists(CSV_PATH):
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            korean_to_id[row["name_ko"]] = row["pokemon_id"]
            pokemon_names.append(row["name_ko"])
else:
    messagebox.showwarning("경고", "pokemon_stats.csv 파일을 찾을 수 없어요!\n(data 폴더에 파일이 있는지 확인하세요)")

natures_data = {}
nature_names = []

if os.path.exists(NATURE_PATH):
    with open(NATURE_PATH, "r", encoding="utf-8") as f:
        nature_list = json.load(f)
        for n in nature_list:
            natures_data[n["name_ko"]] = {
                "up": n["increased_stat"],
                "down": n["decreased_stat"]
            }
            nature_names.append(n["name_ko"])
else:
    messagebox.showwarning("경고", "natures.json 파일을 찾을 수 없어요!")

# API 스탯 이름 매핑
stat_api_names = {
    "HP": "hp",
    "공격": "attack",
    "방어": "defense",
    "특수공격": "special-attack",
    "특수방어": "special-defense",
    "스피드": "speed"
}

current_base_stats = {
    "HP": 0, "공격": 0, "방어": 0, "특수공격": 0, "특수방어": 0, "스피드": 0
}

# ------------------------------------------------------------------
# 2. 검색 및 API 호출 함수
# ------------------------------------------------------------------
def search_pokemon(*args):
    name = search_combo.get()
    
    if name not in korean_to_id:
        messagebox.showwarning("검색 실패", f"앗! '{name}'은(는) 사전에 없는 이름이에요.")
        return
        
    pokemon_id = korean_to_id[name]
    
    # 인터넷 식당(API)에 주문하기!
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        
        # 종족값 업데이트
        stats = data["stats"]
        current_base_stats["HP"] = stats[0]["base_stat"]
        current_base_stats["공격"] = stats[1]["base_stat"]
        current_base_stats["방어"] = stats[2]["base_stat"]
        current_base_stats["특수공격"] = stats[3]["base_stat"]
        current_base_stats["특수방어"] = stats[4]["base_stat"]
        current_base_stats["스피드"] = stats[5]["base_stat"]
        
        # 이미지 바로 가져오기
        image_url = data["sprites"]["other"]["official-artwork"]["front_default"]
        if image_url:
            img_req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            img_response = urllib.request.urlopen(img_req)
            img_data = img_response.read()
            
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((200, 200))
            photo = ImageTk.PhotoImage(img)
            
            image_label.config(image=photo, text="")
            image_label.image = photo
        else:
            image_label.config(image="", text="이미지 없음")
        
        title_label.config(text=f"No.{pokemon_id} : {name}")
        calculate_all_stats()
        
    except Exception as e:
        messagebox.showerror("에러", f"데이터를 가져오는데 실패했어요!\n{e}")

# ------------------------------------------------------------------
# 3. 실전 능력치 자동 계산 함수 (레벨 + 성격 적용)
# ------------------------------------------------------------------
def calculate_all_stats(*args):
    if current_base_stats["HP"] == 0:
        return
        
    try:
        level = int(level_input.get())
    except:
        level = 50
        level_input.delete(0, 'end')
        level_input.insert(0, "50")
        
    # 선택된 성격 정보 가져오기
    selected_nature = nature_combo.get()
    nature_info = natures_data.get(selected_nature, {"up": None, "down": None})
    
    # 성격 보정치 계산 (올라가는 능력치는 x1.1, 내려가는 능력치는 x0.9)
    def get_multiplier(stat_name_kr):
        api_name = stat_api_names[stat_name_kr]
        if nature_info["up"] == api_name:
            return 1.1
        elif nature_info["down"] == api_name:
            return 0.9
        else:
            return 1.0

    # 진짜 게임 공식 적용 (IV=31, EV=0 기준)
    # HP 계산: ((종족값 * 2 + 31) * 레벨 / 100) + 레벨 + 10
    final_hp = int(((current_base_stats["HP"] * 2 + 31) * level) / 100) + level + 10
    hp_label.config(text=f"❤️ HP: {final_hp}  (종족값: {current_base_stats['HP']})")
    
    # 나머지 계산: (((종족값 * 2 + 31) * 레벨 / 100) + 5) * 성격보정
    def calc_stat(stat_name):
        base = current_base_stats[stat_name]
        val = int(((base * 2 + 31) * level) / 100) + 5
        multi = get_multiplier(stat_name)
        
        # 성격에 따라 화살표 표시
        arrow = "🔺" if multi == 1.1 else "🔻" if multi == 0.9 else ""
        return f"{int(val * multi)} {arrow}"
        
    result_text = (
        f"⚔️ 공격: {calc_stat('공격')}  (종족값: {current_base_stats['공격']})\n"
        f"🛡️ 방어: {calc_stat('방어')}  (종족값: {current_base_stats['방어']})\n"
        f"🔥 특수공격: {calc_stat('특수공격')}  (종족값: {current_base_stats['특수공격']})\n"
        f"✨ 특수방어: {calc_stat('특수방어')}  (종족값: {current_base_stats['특수방어']})\n"
        f"💨 스피드: {calc_stat('스피드')}  (종족값: {current_base_stats['스피드']})"
    )
    stats_label.config(text=result_text)

# ------------------------------------------------------------------
# 4. 도감 화면(GUI) 그리기
# ------------------------------------------------------------------
window = tkinter.Tk()
window.title("궁극의 진화! 진짜 포켓몬 도감")
window.geometry("450x700")
window.configure(bg="#E8F5E9")

# 검색 창 (자동완성 콤보박스)
search_frame = tkinter.Frame(window, bg="#E8F5E9")
search_frame.pack(pady=15)

tkinter.Label(search_frame, text="포켓몬:", font=("맑은 고딕", 12, "bold"), bg="#E8F5E9").pack(side="left")
search_combo = ttk.Combobox(search_frame, values=pokemon_names, font=("맑은 고딕", 12), width=15)
search_combo.pack(side="left", padx=5)
search_combo.bind("<Return>", search_pokemon) # 엔터 치면 바로 검색
if pokemon_names:
    search_combo.set("피카츄" if "피카츄" in pokemon_names else pokemon_names[0])

search_button = tkinter.Button(search_frame, text="검색 🔍", font=("맑은 고딕", 10, "bold"), command=search_pokemon)
search_button.pack(side="left")

# 이름 라벨
title_label = tkinter.Label(window, text="포켓몬을 검색해 주세요!", font=("맑은 고딕", 18, "bold"), bg="#E8F5E9")
title_label.pack(pady=5)

# 사진 라벨
image_label = tkinter.Label(window, bg="#E8F5E9", text="사진을 불러오는 중...", font=("맑은 고딕", 10))
image_label.pack()

# 레벨과 성격 입력칸
input_frame = tkinter.Frame(window, bg="#E8F5E9")
input_frame.pack(pady=15)

tkinter.Label(input_frame, text="레벨:", font=("맑은 고딕", 12, "bold"), bg="#E8F5E9").grid(row=0, column=0, padx=5)
level_input = tkinter.Entry(input_frame, font=("맑은 고딕", 12), width=5)
level_input.grid(row=0, column=1, padx=5)
level_input.insert(0, "50")
level_input.bind("<KeyRelease>", calculate_all_stats) # 타이핑할 때마다 자동 계산

tkinter.Label(input_frame, text="성격:", font=("맑은 고딕", 12, "bold"), bg="#E8F5E9").grid(row=0, column=2, padx=5)
nature_combo = ttk.Combobox(input_frame, values=nature_names, font=("맑은 고딕", 12), width=10, state="readonly")
nature_combo.grid(row=0, column=3, padx=5)
if nature_names:
    nature_combo.set("고집" if "고집" in nature_names else nature_names[0])
nature_combo.bind("<<ComboboxSelected>>", calculate_all_stats) # 성격 바꾸면 자동 계산

# 결과 라벨
hp_label = tkinter.Label(window, text="❤️ HP: ?", font=("맑은 고딕", 14, "bold"), fg="#D32F2F", bg="#E8F5E9")
hp_label.pack(pady=5)

stats_label = tkinter.Label(window, text="⚔️ 공격: ?\n🛡️ 방어: ?\n🔥 특수공격: ?\n✨ 특수방어: ?\n💨 스피드: ?", 
                            font=("맑은 고딕", 14), bg="#E8F5E9", justify="left")
stats_label.pack(pady=10)

# 앱 시작 시 기본 검색 1회 실행
search_pokemon()

window.mainloop()