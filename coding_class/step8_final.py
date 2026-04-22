import tkinter
from PIL import Image, ImageTk

# 피카츄의 진짜 종족값 (기본 능력치)
# 사전(Dictionary) 형태로 예쁘게 담아두었어요!
base_stats = {
    "HP": 35,
    "공격": 55,
    "방어": 40,
    "특수공격": 50,
    "특수방어": 50,
    "스피드": 90
}

def calculate_all_stats():
    # 1. 빈칸에 적힌 레벨 글씨를 진짜 숫자(int)로 바꾸기
    level_text = level_input.get()
    level = int(level_text)
    
    # 2. HP 계산하기 (공식: 종족값 * 2 * 레벨 / 100 + 레벨 + 10)
    final_hp = int((base_stats["HP"] * 2 * level) / 100) + level + 10
    hp_label.config(text=f"❤️ HP: {final_hp}")
    
    # 3. 나머지 5개 능력치 계산하기 (공식: 종족값 * 2 * 레벨 / 100 + 5)
    atk = int((base_stats["공격"] * 2 * level) / 100) + 5
    def_stat = int((base_stats["방어"] * 2 * level) / 100) + 5
    spa = int((base_stats["특수공격"] * 2 * level) / 100) + 5
    spd = int((base_stats["특수방어"] * 2 * level) / 100) + 5
    spe = int((base_stats["스피드"] * 2 * level) / 100) + 5
    
    # 4. 화면 라벨에 계산된 결과 쫘르륵! 업데이트하기
    result_text = f"⚔️ 공격: {atk}\n🛡️ 방어: {def_stat}\n🔥 특수공격: {spa}\n✨ 특수방어: {spd}\n💨 스피드: {spe}"
    stats_label.config(text=result_text)

# --- 여기서부터 도감 화면(GUI) 그리기 시작 ---
window = tkinter.Tk()
window.title("최종 완성! 실전 포켓몬 도감")
window.geometry("350x550")
window.configure(bg="#FFFDE7") # 밝고 예쁜 노란색 배경

# 1. 제목 라벨
title_label = tkinter.Label(window, text="⚡ 피카츄 전력 분석기 ⚡", font=("맑은 고딕", 18, "bold"), bg="#FFFDE7")
title_label.pack(pady=15)

# 2. 피카츄 사진 띄우기 (3단계에서 다운받은 사진)
try:
    img = Image.open("images/pikachu.png")
    img = img.resize((180, 180)) # 사진 크기 조절
    photo = ImageTk.PhotoImage(img)
    image_label = tkinter.Label(window, image=photo, bg="#FFFDE7")
    image_label.pack()
except:
    error_label = tkinter.Label(window, text="(사진이 없습니다. 3단계를 먼저 실행하세요!)", fg="red", bg="#FFFDE7")
    error_label.pack()

# 3. 레벨 입력칸 만들기 (Frame을 써서 글씨와 빈칸을 나란히 묶기)
input_frame = tkinter.Frame(window, bg="#FFFDE7")
input_frame.pack(pady=15)

tkinter.Label(input_frame, text="레벨 입력:", font=("맑은 고딕", 12, "bold"), bg="#FFFDE7").pack(side="left")
level_input = tkinter.Entry(input_frame, font=("맑은 고딕", 12), width=5)
level_input.pack(side="left", padx=5)
level_input.insert(0, "50") # 기본 레벨은 50으로 설정

# 4. 마법의 계산 버튼 만들기
calc_button = tkinter.Button(window, text="전체 능력치 계산하기!", font=("맑은 고딕", 12, "bold"), 
                             command=calculate_all_stats, bg="#FFCC00", fg="black")
calc_button.pack(pady=10)

# 5. 결과를 보여줄 예쁜 라벨 2개 (HP 라벨, 나머지 라벨)
hp_label = tkinter.Label(window, text="❤️ HP: ?", font=("맑은 고딕", 16, "bold"), fg="#E53935", bg="#FFFDE7")
hp_label.pack(pady=5)

stats_label = tkinter.Label(window, text="⚔️ 공격: ?\n🛡️ 방어: ?\n🔥 특수공격: ?\n✨ 특수방어: ?\n💨 스피드: ?", 
                            font=("맑은 고딕", 14), bg="#FFFDE7", justify="left")
stats_label.pack(pady=5)

# 6. 마법 주문! 창이 꺼지지 않게 하기
window.mainloop()
