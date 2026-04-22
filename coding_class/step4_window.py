import tkinter

# 1. 도감이 될 가장 큰 창(윈도우) 만들기
window = tkinter.Tk()

# 2. 창 제목 달아주기
window.title("나만의 포켓몬 도감")

# 3. 창 크기 정하기 (가로 400, 세로 500)
window.geometry("400x500")

# 4. 창 배경색 노란색으로 바꾸기
window.configure(bg="yellow")

# 5. 창을 화면에 계속 띄워두기 (마법의 주문!)
window.mainloop()
