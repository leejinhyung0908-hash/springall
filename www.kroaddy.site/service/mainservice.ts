import { API_BASE_URL, startSocialLogin } from '@/lib/api';

/**
 * 소셜 로그인 핸들러를 생성하는 IIFE (Immediately Invoked Function Expression)
 * 각 핸들러는 이너 함수로 구성되어 공통 로직을 공유합니다.
 */
export const { handleKakaoLogin, handleNaverLogin, handleGoogleLogin } = (() => {
    /**
     * Gateway 로그를 기록하는 공통 함수
     */
    const logLoginAction = async (action: string): Promise<void> => {
        try {
            await fetch(`${API_BASE_URL}/api/log/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include', // 쿠키 포함
                body: JSON.stringify({ action }),
            }).catch(() => { });
        } catch (error) {
            // 로그 기록 실패는 무시
            console.error('로그 기록 실패:', error);
        }
    };

    /**
     * 카카오 로그인 핸들러 (이너 함수)
     */
    const handleKakaoLogin = async (): Promise<void> => {
        try {
            await logLoginAction('Gateway 카카오 연결 시작');
            await startSocialLogin('kakao');
        } catch (error) {
            console.error('카카오 로그인 실패:', error);
        }
    };

    /**
     * 네이버 로그인 핸들러 (이너 함수)
     */
    const handleNaverLogin = async (): Promise<void> => {
        try {
            await logLoginAction('Gateway 네이버 연결 시작');
            await startSocialLogin('naver');
        } catch (error) {
            console.error('네이버 로그인 실패:', error);
        }
    };

    /**
     * 구글 로그인 핸들러 (이너 함수)
     */
    const handleGoogleLogin = async (): Promise<void> => {
        try {
            await logLoginAction('Gateway 구글 연결 시작');
            await startSocialLogin('google');
        } catch (error) {
            console.error('구글 로그인 실패:', error);
        }
    };

    // 핸들러들을 객체로 반환
    return {
        handleKakaoLogin,
        handleNaverLogin,
        handleGoogleLogin,
    };
})();

