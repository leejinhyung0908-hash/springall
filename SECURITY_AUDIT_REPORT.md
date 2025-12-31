# 보안 점검 보고서

## 📋 점검 일자
2025-12-04

## ✅ 잘 구현된 보안 기능

### 1. 쿠키 기반 인증
- ✅ `httpOnly=true`: JavaScript 접근 차단 (XSS 방지)
- ✅ `SameSite` 설정: CSRF 방지
- ✅ `secure` 옵션: 환경 변수로 제어 가능

### 2. CORS 설정
- ✅ 특정 Origin만 허용 (localhost:3000, 3001, 4000)
- ✅ `allowCredentials: true` 설정
- ✅ Preflight 요청 캐시 시간 설정

### 3. JWT 토큰 관리
- ✅ 토큰 검증 로직 구현
- ✅ Refresh Token 별도 관리
- ✅ 토큰 만료 시간 설정 (24시간 / 7일)

### 4. 환경 변수 관리
- ✅ JWT Secret을 환경 변수로 관리
- ✅ OAuth 클라이언트 정보를 환경 변수로 관리

---

## 🔴 심각한 보안 문제 (즉시 수정 필요)

### 1. JWT 토큰 콘솔 출력 ⚠️ **CRITICAL**
**위치:**
- `service.kroaddy.site/auth-service/src/main/java/site/protoa/api/google/GoogleController.java:124-127`
- `service.kroaddy.site/auth-service/src/main/java/site/protoa/api/kakao/KakaoController.java:106-109`
- `service.kroaddy.site/auth-service/src/main/java/site/protoa/api/naver/NaverController.java:128-131`

**문제:**
```java
System.out.println("JWT Token: " + jwt);
System.out.println("Refresh Token: " + refreshToken);
```

**위험도:** 🔴 **CRITICAL**
- 프로덕션 환경에서 로그 파일에 토큰이 저장됨
- 로그 파일 접근 시 전체 토큰 노출
- 토큰 탈취 시 계정 무단 접근 가능

**권장 조치:**
- 토큰 전체 출력 제거
- 로그 레벨을 DEBUG로 변경하고 프로덕션에서는 비활성화
- 토큰 일부만 마스킹하여 출력 (예: `token.substring(0, 10) + "..."`)

### 2. JWT Secret 기본값 약함 ⚠️ **HIGH**
**위치:**
- `service.kroaddy.site/auth-service/src/main/resources/application.yaml:23`

**문제:**
```yaml
jwt:
  secret: ${JWT_SECRET:default-secret-key-change-in-production-min-32-characters}
```

**위험도:** 🔴 **HIGH**
- 기본값이 예측 가능함
- 환경 변수 미설정 시 약한 Secret 사용

**권장 조치:**
- 프로덕션에서는 반드시 강력한 JWT_SECRET 환경 변수 설정
- 최소 32바이트 이상의 랜덤 문자열 사용
- 기본값 제거 또는 빌드 실패하도록 설정

### 3. 에러 메시지에 상세 정보 노출 ⚠️ **MEDIUM**
**위치:**
- `service.kroaddy.site/auth-service/src/main/java/site/protoa/api/auth/AuthController.java:80`

**문제:**
```java
"message", "서버 오류가 발생했습니다: " + e.getMessage()
```

**위험도:** 🟡 **MEDIUM**
- 스택 트레이스나 내부 오류 정보가 클라이언트에 노출될 수 있음

**권장 조치:**
- 프로덕션에서는 일반적인 오류 메시지만 반환
- 상세 오류는 서버 로그에만 기록

---

## 🟡 중간 수준 보안 문제 (개선 권장)

### 1. CORS 헤더 설정이 너무 관대함
**위치:**
- `api.kroaddy.site/gateway/src/main/java/site/protoa/api/config/CorsConfig.java:30, 36`

**문제:**
```java
corsConfig.setAllowedHeaders(Arrays.asList("*"));
corsConfig.setExposedHeaders(Arrays.asList("*"));
```

**위험도:** 🟡 **MEDIUM**
- 모든 헤더 허용은 불필요한 헤더 노출 가능

**권장 조치:**
- 필요한 헤더만 명시적으로 허용
- 예: `Content-Type`, `Authorization`, `X-Requested-With` 등

### 2. 쿠키 Secure 기본값이 false
**위치:**
- `service.kroaddy.site/auth-service/src/main/resources/application.yaml:32`

**문제:**
```yaml
cookie:
  secure: ${COOKIE_SECURE:false}  # 개발: false, 프로덕션: true (HTTPS 필수)
```

**위험도:** 🟡 **MEDIUM**
- 프로덕션에서 HTTPS 사용 시 `secure=true` 필수

**권장 조치:**
- 프로덕션 환경 변수에서 `COOKIE_SECURE=true` 설정
- 환경별 설정 파일 분리

### 3. Origin 헤더 검증 부족
**위치:**
- `api.kroaddy.site/gateway/src/main/java/site/protoa/api/config/FrontendCallbackUrlFilter.java:29-30`

**문제:**
- Origin/Referer 헤더를 단순히 신뢰
- 헤더 변조 가능

**위험도:** 🟡 **MEDIUM**
- 클라이언트가 Origin 헤더를 변조할 수 있음

**권장 조치:**
- 허용된 Origin 목록과 비교 검증
- Referer보다 Origin 우선 사용

---

## 🟢 낮은 수준 보안 개선 사항

### 1. 로그인 시도 제한 없음
- **권장:** Rate Limiting 추가 (예: 5회 실패 시 일시적 차단)

### 2. 토큰 만료 시간이 길음
- Access Token: 24시간 (권장: 15분~1시간)
- Refresh Token: 7일 (권장: 7일~30일)

### 3. 로그아웃 시 토큰 무효화 없음
- **권장:** 토큰 블랙리스트 관리 (Redis 등)

---

## 📝 권장 조치 사항 우선순위

### 즉시 조치 (프로덕션 배포 전 필수)
1. ✅ JWT 토큰 콘솔 출력 제거 또는 마스킹
2. ✅ JWT_SECRET 환경 변수 강제 설정
3. ✅ 프로덕션에서 COOKIE_SECURE=true 설정

### 단기 조치 (1주일 내)
4. ✅ CORS 헤더 명시적 설정
5. ✅ 에러 메시지 일반화
6. ✅ Origin 헤더 검증 강화

### 중기 조치 (1개월 내)
7. ⚠️ Rate Limiting 구현
8. ⚠️ 토큰 블랙리스트 관리
9. ⚠️ 토큰 만료 시간 조정

---

## 🔐 보안 체크리스트

- [x] 쿠키 httpOnly 설정
- [x] 쿠키 SameSite 설정
- [ ] 쿠키 secure 설정 (프로덕션)
- [x] CORS 특정 Origin 허용
- [ ] CORS 헤더 명시적 설정
- [x] JWT 토큰 검증
- [x] Refresh Token 관리
- [ ] JWT Secret 강제 설정
- [ ] 토큰 로그 출력 제거
- [ ] Rate Limiting
- [ ] 토큰 블랙리스트
- [ ] 에러 메시지 일반화

