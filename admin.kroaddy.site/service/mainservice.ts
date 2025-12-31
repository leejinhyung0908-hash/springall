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

/**
 * 소셜 로그인 핸들러를 생성하는 팩토리 함수 (IIFE 패턴)
 * 컴포넌트에서 setter를 주입받아 상태 관리와 분리
 */
export const createSocialLoginHandlers = (() => {
    // IIFE 내부: 공통 설정 및 변수 (private 스코프)
    const gatewayUrl = API_BASE_URL;

    /**
     * 공통 로그인 처리 로직 (private 헬퍼 함수)
     */
    async function handleLogin(
        provider: 'google' | 'kakao' | 'naver',
        setIsLoading: (loading: boolean) => void,
        setError: (error: string) => void
    ) {
        try {
            setIsLoading(true);
            setError('');
            await startSocialLogin(provider);
        } catch (error) {
            console.error(`${provider} 로그인 실패:`, error);
            setError(`${provider} 로그인에 실패했습니다.`);
        } finally {
            setIsLoading(false);
        }
    }

    /**
     * 이메일/비밀번호 로그인 처리 로직 (private 헬퍼 함수)
     */
    async function handleEmailLogin(
        email: string,
        password: string,
        setIsLoading: (loading: boolean) => void,
        setError: (error: string) => void,
        onSuccess: () => void
    ) {
        try {
            setIsLoading(true);
            setError('');

            const response = await fetch(`${gatewayUrl}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                onSuccess();
            } else {
                const data = await response.json();
                setError(data.message || '로그인에 실패했습니다.');
            }
        } catch (err) {
            setError('서버 연결에 실패했습니다.');
        } finally {
            setIsLoading(false);
        }
    }

    // 팩토리 함수 반환 (public API)
    return (
        setIsGoogleLoading: (loading: boolean) => void,
        setIsKakaoLoading: (loading: boolean) => void,
        setIsNaverLoading: (loading: boolean) => void,
        setIsLoading: (loading: boolean) => void,
        setError: (error: string) => void
    ) => {
        // 핸들러 함수들 (이너 함수)
        function handleGoogleLogin() {
            handleLogin('google', setIsGoogleLoading, setError);
        }

        function handleKakaoLogin() {
            handleLogin('kakao', setIsKakaoLoading, setError);
        }

        function handleNaverLogin() {
            handleLogin('naver', setIsNaverLoading, setError);
        }

        function handleEmailPasswordLogin(email: string, password: string, onSuccess: () => void) {
            handleEmailLogin(email, password, setIsLoading, setError, onSuccess);
        }

        // 핸들러들을 객체로 반환
        return {
            handleGoogleLogin,
            handleKakaoLogin,
            handleNaverLogin,
            handleEmailPasswordLogin,
        };
    };
})();
