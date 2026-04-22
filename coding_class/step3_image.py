import urllib.request
import os

# 이미지를 저장할 'images' 폴더 만들기
os.makedirs("images", exist_ok=True)

# 인터넷에 있는 피카츄 사진 주소
image_url = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png"

# 저장할 파일 이름
file_name = "images/pikachu.png"

print("피카츄 사진 다운로드 시작!")

# 주소에 있는 사진을 예의 바르게 요청해서 내 컴퓨터 파일로 저장하기
req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)

# 저장할 파일을 열고 (wb: 바이너리 쓰기 모드) 다운받은 사진 쓰기
file = open(file_name, "wb")
file.write(response.read())
file.close()

print("다운로드 완료! images 폴더를 확인해 보세요.")
