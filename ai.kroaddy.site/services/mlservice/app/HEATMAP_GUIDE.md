# 범죄 히트맵 생성 가이드

## 개요
`crime_processed.csv` 데이터를 기반으로 서울시 구별 범죄 발생 히트맵을 생성하는 스크립트입니다.

## 설치 방법

### 1. 필요한 라이브러리 설치
```bash
pip install matplotlib seaborn
```

또는 requirements.txt를 사용하여 전체 설치:
```bash
pip install -r requirements.txt
```

### 2. 한글 폰트 설정 (Windows)
Windows에서는 기본적으로 'Malgun Gothic' 폰트가 설치되어 있습니다.
다른 OS를 사용하는 경우 스크립트의 폰트 설정을 수정해야 합니다:

**Linux (Ubuntu/Debian):**
```python
plt.rcParams['font.family'] = 'NanumGothic'
```

**macOS:**
```python
plt.rcParams['font.family'] = 'AppleGothic'
```

## 실행 방법

### 방법 1: 직접 실행
```bash
cd ai.kroaddy.site/services/mlservice/app
python create_crime_heatmap.py
```

### 방법 2: Python 모듈로 실행
```bash
cd ai.kroaddy.site/services/mlservice
python -m app.create_crime_heatmap
```

## 출력 결과
- 히트맵 이미지: `app/save/crime_heatmap.png`
- 자치구별 정규화된 범죄 발생 데이터가 히트맵으로 시각화됩니다.

## 스크립트 동작 과정

1. **데이터 로드**: `crime_processed.csv` 파일을 읽습니다.
2. **데이터 집계**: 자치구별로 범죄 발생 건수를 합산합니다.
3. **정규화**: 각 범죄 유형별로 0-1 사이로 정규화합니다.
4. **정렬**: 전체 범죄 합계 기준으로 내림차순 정렬합니다.
5. **히트맵 생성**: 정규화된 데이터를 히트맵으로 시각화합니다.

## 히트맵 특징

- **행 (Y축)**: 서울시 25개 자치구 (전체 범죄 기준 내림차순 정렬)
- **열 (X축)**: 범죄 유형 (강간, 강도, 살인, 절도, 폭력, 범죄)
- **색상**: 보라색-핑크 계열 (어두운 색 = 높은 범죄 발생)
- **값**: 정규화된 범죄 발생 건수 (0.0 ~ 1.0)

## 커스터마이징

### 색상맵 변경
`create_heatmap` 함수에서 `cmap` 파라미터를 변경할 수 있습니다:
- `'magma_r'`: 보라색-핑크 계열 (기본값)
- `'viridis'`: 초록-파랑 계열
- `'plasma'`: 보라-노랑 계열
- `'inferno'`: 검정-노랑 계열

### 그림 크기 조정
`figsize=(10, 14)` 파라미터를 조정하여 크기를 변경할 수 있습니다.

### 저장 경로 변경
`main()` 함수에서 `output_path` 변수를 수정하면 됩니다.

