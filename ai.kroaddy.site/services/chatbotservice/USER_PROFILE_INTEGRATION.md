# 사용자 프로필 통합 가이드

## 개요

Onboarding에서 수집한 사용자 개인정보를 챗봇 대화에 포함시켜 개인화된 응답을 제공합니다.

## 수집되는 사용자 정보

Onboarding에서 수집하는 정보:
- `gender`: 성별 (Male, Female, Other / Non-disclosure)
- `age`: 생년월일 (YYYY-MM-DD 형식)
- `nationality`: 국적/거주지
- `religion`: 종교
- `dietary`: 식이 제한 (Normal, Vegetarian, Vegan, Pescetarian, Other)

## 데이터 흐름

1. **Onboarding 완료 시**
   - `localStorage.setItem('onboardingData', JSON.stringify(formData))`
   - 사용자 정보가 브라우저 로컬 스토리지에 저장됨

2. **챗봇 메시지 전송 시**
   - `localStorage.getItem('onboardingData')`로 사용자 정보 읽기
   - API 요청에 `user_profile` 필드로 포함

3. **백엔드 처리**
   - `user_profile`을 받아서 시스템 메시지에 포함
   - OpenAI API 호출 시 개인화된 컨텍스트 제공

## 시스템 메시지 예시

```
너는 친절한 한국에 여행 온 외국인 맞춤형 챗봇이야. 사용자의 질문에 정확하고 도움이 되는 답변을 제공해줘.

사용자 정보:
성별: Female
생년월일: 1995-03-15
국적/거주지: South Korea
종교: Buddhism
식이 제한: Vegetarian

위 사용자 정보를 고려하여 개인화된 답변을 제공해줘.
```

## 예시 응답

사용자가 "고깃집 알려줘"라고 물어보면:
- 일반 응답: "서울에 좋은 고깃집을 추천해드리겠습니다..."
- 개인화된 응답: "식이 제한이 Vegetarian이시군요. 대신 채식 레스토랑이나 비건 식당을 추천해드릴까요? 또는 채식 옵션이 있는 레스토랑도 찾아드릴 수 있습니다."

## 보안 고려사항

1. **개인정보 보호**: 사용자 정보는 OpenAI에 전달되지만, 민감한 정보는 최소화
2. **로컬 스토리지**: 브라우저 로컬 스토리지에 저장되므로 사용자가 삭제 가능
3. **선택적 사용**: 사용자가 원하지 않으면 Onboarding을 건너뛸 수 있음

## 테스트 방법

1. Onboarding 완료
2. 챗봇에 메시지 전송
3. 브라우저 콘솔에서 "사용자 프로필 정보:" 로그 확인
4. 서버 로그에서 시스템 메시지에 사용자 정보가 포함되었는지 확인

