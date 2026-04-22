import tkinter
from PIL import Image, ImageTk

window = tkinter.Tk()
window.title("나만의 포켓몬 도감")
window.geometry("400x500")

# 1. 이름 라벨(글씨) 만들어서 붙이기
name_label = tkinter.Label(window, text="피카츄", font=("맑은 고딕", 24, "bold"))
name_label.pack(pady=20) # 창에 붙이기 (위아래 여백 20)

# 2. 사진 불러오기
# PIL 도구를 써서 사진 크기를 가로 200, 세로 200으로 줄이기
image_file = Image.open("images/pikachu.png")
image_file = image_file.resize((200, 200))
photo = ImageTk.PhotoImage(image_file)

# 3. 사진을 담을 라벨 만들어서 붙이기
image_label = tkinter.Label(window, image=photo)
image_label.pack()

window.mainloop()
