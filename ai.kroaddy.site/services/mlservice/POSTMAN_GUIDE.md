# Postman에서 NLP Emma API 사용 가이드

## 서비스 확인
서비스가 정상적으로 작동하고 있습니다! ✅

## POST 요청: `http://localhost:8080/api/ml/nlp/emma`

### 1. 기본 설정
- **Method**: `POST`
- **URL**: `http://localhost:8080/api/ml/nlp/emma`
- **Headers**: 
  ```
  Content-Type: application/json
  ```

### 2. Body (JSON 형식)

#### 옵션 1: 최소 요청 (모든 기본값 사용)
```json
{}
```

#### 옵션 2: 텍스트 길이 제한
```json
{
  "text_length": 10000
}
```

#### 옵션 3: 전체 옵션 지정
```json
{
  "text_length": null,
  "stopwords": ["Mr.", "Mrs.", "Miss", "Mr", "Mrs", "Dear"],
  "width": 1000,
  "height": 600,
  "background_color": "white",
  "return_image": true
}
```

### 3. 응답 예시
```json
{
  "status": "success",
  "message": "Emma 소설 처리 및 워드클라우드 생성 완료",
  "data": {
    "text_length": 887071,
    "token_count": 192427,
    "proper_noun_count": 1234,
    "stats": {
      "total_tokens": 1234,
      "unique_tokens": 456,
      "most_common": [
        ["Emma", 865],
        ["Knightley", 234],
        ...
      ],
      "max_frequency": "Emma",
      "max_frequency_count": 865
    },
    "wordcloud": {
      "image_base64": "iVBORw0KGgoAAAANS...",
      "format": "png",
      "width": 1000,
      "height": 600
    }
  }
}
```

## 다른 엔드포인트

### GET `/api/ml/nlp/emma/wordcloud`
워드클라우드 이미지를 PNG로 직접 반환
- **Method**: `GET`
- **URL**: `http://localhost:8080/api/ml/nlp/emma/wordcloud`
- **Query Parameters** (선택적):
  - `width=1000`
  - `height=600`
  - `background_color=white`
  - `text_length=10000`

### GET `/api/ml/nlp/emma/stats`
빈도 분포 통계 조회
- **Method**: `GET`
- **URL**: `http://localhost:8080/api/ml/nlp/emma/stats?text_length=10000`

### GET `/api/ml/nlp/emma/text`
Emma 원문 조회
- **Method**: `GET`
- **URL**: `http://localhost:8080/api/ml/nlp/emma/text?length=1000`

## 문제 해결

### 422 Unprocessable Entity 에러
- JSON 형식이 올바른지 확인하세요
- 모든 문자열은 큰따옴표(`"`)로 감싸야 합니다
- 숫자는 따옴표 없이 작성하세요
- `null`은 따옴표 없이 작성하세요

### 올바른 JSON 예시
```json
{
  "text_length": 1000,
  "width": 1000,
  "height": 600,
  "background_color": "white",
  "return_image": true
}
```

### 잘못된 JSON 예시
```json
{
  "text_length": "1000",  // ❌ 숫자는 따옴표 없이
  "width": 1000,
  "height": 600,
  "background_color": 'white',  // ❌ 작은따옴표 사용
  "return_image": "true"  // ❌ boolean은 따옴표 없이
}
```

## 테스트 순서

1. **서비스 상태 확인**
   ```
   GET http://localhost:8080/api/ml/nlp/
   ```

2. **간단한 요청 테스트**
   ```
   POST http://localhost:8080/api/ml/nlp/emma
   Body: {}
   ```

3. **텍스트 길이 제한 테스트**
   ```
   POST http://localhost:8080/api/ml/nlp/emma
   Body: {"text_length": 10000}
   ```

4. **전체 옵션 테스트**
   ```
   POST http://localhost:8080/api/ml/nlp/emma
   Body: {
     "text_length": null,
     "stopwords": ["Mr.", "Mrs."],
     "width": 1000,
     "height": 600,
     "background_color": "white",
     "return_image": true
   }
   ```

