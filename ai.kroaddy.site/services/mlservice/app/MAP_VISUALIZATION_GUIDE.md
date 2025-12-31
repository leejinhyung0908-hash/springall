# 범죄-CCTV 상관관계 지도 시각화 가이드

## 개요
`crime_processed.csv`와 `cctv_processed.csv` 데이터를 기반으로 서울시 자치구별 범죄 발생 건수와 CCTV 개수의 상관관계를 지도로 시각화하는 스크립트입니다.

## 설치 방법

### 1. 필요한 라이브러리 설치
```bash
pip install folium matplotlib seaborn
```

또는 requirements.txt를 사용하여 전체 설치:
```bash
pip install -r requirements.txt
```

## 실행 방법

### 방법 1: 직접 실행
```bash
cd ai.kroaddy.site/services/mlservice/app
python create_crime_cctv_map.py
```

### 방법 2: Python 모듈로 실행
```bash
cd ai.kroaddy.site/services/mlservice
python -m app.create_crime_cctv_map
```

## 출력 결과

1. **인터랙티브 지도**: `app/save/crime_cctv_map.html`
   - 브라우저에서 열어서 확인할 수 있는 인터랙티브 지도
   - 각 자치구를 클릭하면 상세 정보 팝업 표시
   - 마커 색상으로 CCTV 충분 여부 표시

2. **상관관계 산점도**: `app/save/crime_cctv_correlation.png`
   - 범죄 발생 건수와 CCTV 개수의 상관관계를 시각화
   - 각 자치구의 위치와 상관계수 표시

## 스크립트 동작 과정

1. **데이터 로드**: 
   - `crime_processed.csv`: 범죄 발생 데이터
   - `cctv_processed.csv`: CCTV 설치 데이터
   - `locations.csv`: 자치구별 위치 좌표

2. **데이터 집계**: 
   - 자치구별로 범죄 발생 건수를 합산
   - CCTV 개수와 병합

3. **상관관계 계산**:
   - CCTV/범죄 비율 계산
   - 정규화된 상관관계 점수 계산
   - 상관계수 계산

4. **지도 시각화**:
   - 각 자치구 위치에 마커 표시
   - 마커 색상: CCTV 충분(녹색), 보통(주황), 부족(빨강)
   - 마커 크기: 범죄 발생 건수에 비례

5. **산점도 생성**:
   - X축: 총 범죄 발생 건수
   - Y축: CCTV 개수
   - 추세선 및 상관계수 표시

## 지도 특징

### 마커 색상 의미
- **녹색**: CCTV가 충분한 지역 (상관관계 점수 > 0.2)
- **주황색**: 보통 지역 (-0.2 ≤ 상관관계 점수 ≤ 0.2)
- **빨강색**: CCTV가 부족한 지역 (상관관계 점수 < -0.2)

### 마커 크기
- 범죄 발생 건수에 비례하여 크기가 결정됩니다
- 범죄가 많을수록 마커가 큽니다

### 팝업 정보
각 마커를 클릭하면 다음 정보가 표시됩니다:
- 총 범죄 발생 건수
- CCTV 개수
- CCTV/범죄 비율
- 상관관계 점수
- 범죄 유형별 상세 정보

## 상관관계 해석

### 상관계수
- **양의 상관관계**: 범죄가 많을수록 CCTV도 많음 (일반적인 정책 반영)
- **음의 상관관계**: 범죄가 많을수록 CCTV가 적음 (정책 개선 필요)
- **0에 가까움**: 상관관계가 약함

### CCTV/범죄 비율
- 높을수록: CCTV가 범죄 대비 충분히 설치됨
- 낮을수록: CCTV가 범죄 대비 부족함

## 커스터마이징

### 지도 스타일 변경
`create_interactive_map` 함수에서 다음을 수정할 수 있습니다:
- `tiles='OpenStreetMap'`: 다른 타일 레이어 사용 가능
  - `'CartoDB positron'`: 밝은 배경
  - `'CartoDB dark_matter'`: 어두운 배경
  - `'Stamen Terrain'`: 지형도

### 색상 기준 변경
`create_interactive_map` 함수에서 색상 기준값을 조정할 수 있습니다:
```python
if correlation_score > 0.2:  # 이 값을 조정
    color = 'green'
```

### 마커 스타일 변경
`CircleMarker` 대신 `Marker`를 사용하거나, 아이콘을 변경할 수 있습니다.

## 문제 해결

### 한글 폰트 문제
Windows에서는 기본적으로 'Malgun Gothic'이 사용됩니다.
다른 OS에서는 matplotlib 폰트 설정을 변경해야 합니다.

### 지도가 표시되지 않음
- 인터넷 연결 확인 (타일 이미지 로드 필요)
- 브라우저에서 HTML 파일 열기

### 데이터 불일치
- 자치구명이 정확히 일치하는지 확인
- CSV 파일의 인코딩 확인 (UTF-8 권장)

