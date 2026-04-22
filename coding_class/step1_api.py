import urllib.request
import json

print("포켓몬 정보를 가져오는 중...")

# 피카츄(25번) 정보가 있는 인터넷 주소
url = "https://pokeapi.co/api/v2/pokemon/25"

# 1. 인터넷 식당에 예의 바르게 인사하며 데이터 가져오기 (User-Agent 추가)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib.request.urlopen(req)
data_bytes = response.read()

# 2. 파이썬이 읽을 수 있는 사전(딕셔너리) 모양으로 바꾸기
pokemon_data = json.loads(data_bytes)

# 3. 필요한 정보만 쏙쏙 뽑아서 출력하기!
print("이름:", pokemon_data["name"])
print("키:", pokemon_data["height"] * 10, "cm")
print("몸무게:", pokemon_data["weight"] / 10, "kg")
