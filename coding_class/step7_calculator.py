import tkinter

def calculate_hp():
    # 1. 입력칸에 적힌 레벨(글씨)을 가져와서 숫자(int)로 바꾸기
    level_text = level_input.get()
    level = int(level_text)
    
    # 2. HP 계산하기 (피카츄 기본 HP는 35라고 가정)
    base_hp = 35
    
    # 아주 단순화한 포켓몬 HP 계산 공식!
    # (기본 체력 * 2 * 레벨 / 100) + 레벨 + 10
    final_hp = int((base_hp * 2 * level) / 100) + level + 10
    
    # 3. 계산 결과를 화면에 보여주기
    result_label.config(text=f"현재 HP는 {final_hp} 입니다!")

window = tkinter.Tk()
window.geometry("300x250")

tkinter.Label(window, text="레벨업 계산기", font=("맑은 고딕", 16)).pack(pady=10)

# 레벨을 입력할 수 있는 빈칸(Entry) 만들기
level_input = tkinter.Entry(window, font=("맑은 고딕", 14), width=10)
level_input.pack(pady=10)
level_input.insert(0, "50") # 처음에 숫자 50을 미리 적어둠

# 계산 버튼 만들기
calc_button = tkinter.Button(window, text="HP 계산하기", command=calculate_hp)
calc_button.pack(pady=10)

# 결과를 보여줄 라벨 만들기
result_label = tkinter.Label(window, text="HP: ?", font=("맑은 고딕", 14), fg="blue")
result_label.pack(pady=10)

window.mainloop()
