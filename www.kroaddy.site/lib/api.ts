import axios from "axios";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080";

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // CORS 쿠키 지원
  headers: {
    "Content-Type": "application/json",
  },
});

// 쿠키 기반 인증으로 변경되어 Authorization 헤더 제거
// 쿠키는 withCredentials: true 설정으로 자동 전송됨
api.interceptors.request.use((config) => {
  // Authorization 헤더 제거 (쿠키로 자동 전송)
  return config;
});

/**
 * 소셜 로그인 URL 가져오기
 * @param {string} provider - 'kakao', 'naver', 'google'
 * @returns {Promise<string>} 인가 URL
 */
export const getSocialLoginUrl = async (provider: string): Promise<string> => {
  const url = `/api/auth/${provider}/login`;

  try {
    console.log(`🔹 ${provider} 로그인 URL 요청: ${API_BASE_URL}${url}`);
    console.log(`🔹 API_BASE_URL: ${API_BASE_URL}`);
    console.log(`🔹 현재 Origin: ${typeof window !== "undefined" ? window.location.origin : "N/A"}`);

    const response = await api.get(url);

    console.log(`✅ ${provider} 인가 URL 받음`);

    if (!response.data.authUrl) {
      throw new Error(`응답에 authUrl이 없습니다. 응답 데이터: ${JSON.stringify(response.data)}`);
    }

    return response.data.authUrl;
  } catch (error) {
    let errorMessage: string;
    let isNetworkError = false;

    if (axios.isAxiosError(error)) {
      if (error.response) {
        // 서버가 응답했지만 오류 상태 코드
        errorMessage = `HTTP ${error.response.status}: ${JSON.stringify(error.response.data) || error.message}`;
        console.error(`   응답 상태: ${error.response.status}`);
        console.error(`   응답 데이터:`, error.response.data);
        console.error(`   응답 헤더:`, error.response.headers);
      } else if (error.request) {
        // 요청은 보냈지만 응답을 받지 못함 (Network Error)
        isNetworkError = true;
        errorMessage = `Network Error: 서버에 연결할 수 없습니다`;
        console.error(`   요청 객체:`, error.request);
        console.error(`   요청 URL: ${error.config?.url || url}`);
        console.error(`   요청 메서드: ${error.config?.method || "GET"}`);
        console.error(`   전체 baseURL: ${error.config?.baseURL || API_BASE_URL}`);
      } else {
        // 요청 설정 중 오류
        errorMessage = `Request Error: ${error.message}`;
        console.error(`   요청 설정 오류:`, error.message);
      }
    } else {
      errorMessage = error instanceof Error ? error.message : String(error);
    }

    console.error(`❌ 소셜 로그인 URL 가져오기 실패 (${provider}):`, errorMessage);
    console.error(`   요청 URL: ${API_BASE_URL}${url}`);
    console.error(`   API_BASE_URL: ${API_BASE_URL}`);
    console.error(`   현재 Origin: ${typeof window !== "undefined" ? window.location.origin : "N/A"}`);
    console.error(`   전체 오류 객체:`, error);

    if (isNetworkError) {
      const detailedMessage =
        `백엔드 서버에 연결할 수 없습니다.\n\n` +
        `확인 사항:\n` +
        `1. 백엔드 서버 실행 확인: ${API_BASE_URL}\n` +
        `   → 브라우저에서 직접 접속 테스트: ${API_BASE_URL}\n` +
        `2. 백엔드 서버 재시작 확인 (CORS 설정 변경 후 필수)\n` +
        `3. CORS 설정 확인:\n` +
        `   - allowedOrigins에 "${typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"}" 포함 여부\n` +
        `   - allowCredentials: true 설정 여부\n` +
        `   - OPTIONS 메서드 허용 여부\n` +
        `4. Security 설정에서 "/api/auth/**" 경로 permitAll() 확인\n` +
        `5. 브라우저 개발자 도구 → Network 탭에서 요청 확인\n` +
        `6. 방화벽/보안 소프트웨어가 차단하지 않는지 확인`;

      throw new Error(detailedMessage);
    }

    throw new Error(errorMessage);
  }
};

/**
 * 소셜 로그인 시작 (인가 URL로 리다이렉트)
 * @param {string} provider - 'kakao', 'naver', 'google'
 */
export const startSocialLogin = async (provider: string): Promise<void> => {
  try {
    const authUrl = await getSocialLoginUrl(provider);
    console.log(`🔹 ${provider} 로그인 페이지로 리다이렉트합니다...`);
    window.location.href = authUrl; // 카카오/네이버/구글 로그인 페이지로 리다이렉트
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    console.error(`❌ 소셜 로그인 시작 실패 (${provider}):`, errorMessage);

    // 사용자에게 더 명확한 오류 메시지 표시
    alert(
      `로그인에 실패했습니다.\n\n` +
      `${errorMessage}\n\n` +
      `확인 사항:\n` +
      `1. 백엔드 서버가 실행 중인지 확인 (${API_BASE_URL})\n` +
      `2. 환경 변수 NEXT_PUBLIC_API_BASE_URL 설정 확인\n` +
      `3. 브라우저 콘솔에서 자세한 오류 확인`
    );
  }
};

export default api;
