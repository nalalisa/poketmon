# Pokemon Data GUI

`PokeAPI` 기반으로 포켓몬 종족값 CSV와 공식 일러스트를 내려받고, `tkinter` GUI에서 실제 능력치 계산식을 적용해 결과를 보여주는 예제입니다.

## 실행 순서

```powershell
python download_pokemon_data.py
python pokemon_gui.py
```

## 생성 파일

- `data/pokemon_stats.csv`: 포켓몬 종족값 CSV
- `data/natures.json`: 성격 보정 데이터
- `data/types.json`: 타입 한글명 매핑
- `data/images/*.png`: 포켓몬 공식 이미지

## GUI 기능

- 포켓몬 이름, 영문명, 전국도감 번호 검색
- 레벨, 성격, IV, EV 입력
- 실제 포켓몬 능력치 계산식으로 최종 스탯 계산
- 로컬에 저장된 포켓몬 이미지 표시
