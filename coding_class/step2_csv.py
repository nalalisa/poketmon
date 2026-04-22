import csv

# 저장할 포켓몬 데이터 만들기 (리스트 안의 리스트)
pokemon_list = [
    ["번호", "이름", "HP", "공격력"],
    [25, "피카츄", 35, 55],
    [1, "이상해씨", 45, 49],
    [4, "파이리", 39, 52],
    [7, "꼬부기", 44, 48]
]

# 'my_pokemon.csv'라는 이름으로 파일 열기 (쓰기 모드 'w')
file = open("my_pokemon.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(file)

# 데이터를 파일에 쓰기
writer.writerows(pokemon_list)

# 다 썼으면 파일 닫기
file.close()

print("포켓몬 도감(CSV) 저장 완료!")
