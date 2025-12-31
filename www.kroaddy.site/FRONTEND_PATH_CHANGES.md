# 프론트엔드 경로 변경 사항

## 📋 요약

**결론: 변경할 사항 없음** ✅

현재 `www.kroaddy.site`의 API 경로는 `api.kroaddy.site`의 백엔드 API 엔드포인트와 정확히 일치합니다.

---

## ✅ 현재 정상 동작하는 경로

### 1. 인증 관련 API

| 기능 | 프론트엔드 경로 | 백엔드 경로 | 상태 |
|------|----------------|------------|------|
| 인증 상태 확인 | `GET /api/auth/me` | `GET /api/auth/me` | ✅ 일치 |
| 로그아웃 | `POST /api/auth/logout` | `POST /api/auth/logout` | ✅ 일치 |
| 토큰 갱신 | (미사용) | `POST /api/auth/refresh` | ⚠️ 미사용 |

### 2. 소셜 로그인 API

| 기능 | 프론트엔드 경로 | 백엔드 경로 | 상태 |
|------|----------------|------------|------|
| 카카오 로그인 URL | `GET /api/auth/kakao/login` | `GET /api/auth/kakao/login` | ✅ 일치 |
| 네이버 로그인 URL | `GET /api/auth/naver/login` | `GET /api/auth/naver/login` | ✅ 일치 |
| 구글 로그인 URL | `GET /api/auth/google/login` | `GET /api/auth/google/login` | ✅ 일치 |

### 3. 콜백 경로

| 기능 | 백엔드 리다이렉트 경로 | 프론트엔드 페이지 경로 | 상태 |
|------|---------------------|---------------------|------|
| 카카오 콜백 | `/login/kakao/callback` | `/app/login/kakao/callback/page.tsx` | ✅ 일치 |
| 네이버 콜백 | `/login/naver/callback` | `/app/login/naver/callback/page.tsx` | ✅ 일치 |
| 구글 콜백 | `/login/google/callback` | `/app/login/google/callback/page.tsx` | ✅ 일치 |

### 4. 로그 API

| 기능 | 프론트엔드 경로 | 백엔드 경로 | 상태 |
|------|----------------|------------|------|
| 로그인 로그 기록 | `POST /api/log/login` | `POST /api/log/login` | ✅ 일치 |

---

## 📝 현재 프론트엔드 구현 상태

### 사용 중인 파일

1. **`lib/api.ts`**
   - `getSocialLoginUrl()`: 소셜 로그인 URL 가져오기
   - `startSocialLogin()`: 소셜 로그인 시작
   - ✅ 정상 구현

2. **`service/mainservice.ts`**
   - `handleKakaoLogin()`, `handleNaverLogin()`, `handleGoogleLogin()`
   - ✅ 정상 구현

3. **`app/login/dashboard/page.tsx`**
   - `GET /api/auth/me`: 인증 상태 확인
   - `POST /api/auth/logout`: 로그아웃
   - ✅ 정상 구현

4. **콜백 페이지들**
   - `app/login/kakao/callback/page.tsx`
   - `app/login/naver/callback/page.tsx`
   - `app/login/google/callback/page.tsx`
   - ✅ 정상 구현

---

## ⚠️ 권장 사항 (필수 아님)

### 1. 토큰 갱신 로직 추가

현재 프론트엔드에서 토큰 갱신 API(`POST /api/auth/refresh`)를 사용하지 않고 있습니다.

**권장 구현:**

```typescript
// lib/api.ts에 추가
export const refreshToken = async (): Promise<boolean> => {
  try {
    const response = await api.post('/api/auth/refresh');
    return response.data.success === true;
  } catch (error) {
    console.error('토큰 갱신 실패:', error);
    return false;
  }
};

// API 인터셉터에 추가 (axios)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Access Token 만료 시 Refresh Token으로 갱신 시도
      const refreshed = await refreshToken();
      if (refreshed) {
        // 원래 요청 재시도
        return api.request(error.config);
      } else {
        // Refresh Token도 만료된 경우 로그아웃
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);
```

### 2. 환경 변수 확인

`.env.local` 또는 `.env` 파일에 다음 설정이 있는지 확인:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

프로덕션 환경에서는 실제 백엔드 URL로 변경:

```env
NEXT_PUBLIC_API_BASE_URL=https://api.kroaddy.site
```

---

## 🔍 확인 체크리스트

- [x] API 경로 일치 확인
- [x] 콜백 경로 일치 확인
- [x] 쿠키 기반 인증 설정 확인 (`credentials: 'include'`)
- [x] CORS 설정 확인 (백엔드)
- [ ] 토큰 갱신 로직 추가 (선택사항)
- [ ] 환경 변수 설정 확인

---

## 📚 참고 문서

자세한 API 문서는 `api.kroaddy.site/AUTH_SERVICE_API_DOCUMENTATION.md`를 참고하세요.

