import tkinter

def click_button():
    # 버튼을 눌렀을 때 실행될 행동!
    # 라벨의 글씨를 '라이츄'로 바꿉니다.
    info_label.config(text="진화! 라이츄!!", fg="red")

window = tkinter.Tk()
window.geometry("300x200")

# 정보를 보여줄 라벨
info_label = tkinter.Label(window, text="피카츄", font=("맑은 고딕", 20))
info_label.pack(pady=30)

# 클릭할 수 있는 진화 버튼 만들기
# command 에 아까 만든 click_button 행동을 연결합니다.
evolve_button = tkinter.Button(window, text="진화의 돌 사용하기", command=click_button)
evolve_button.pack()

window.mainloop()
