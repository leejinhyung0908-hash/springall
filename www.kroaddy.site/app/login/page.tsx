'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { handleKakaoLogin, handleNaverLogin, handleGoogleLogin } from '@/service/mainservice';

function LoginContent() {
    const searchParams = useSearchParams();
    const router = useRouter();
    const [loginStatus, setLoginStatus] = useState<{ success: boolean; message: string } | null>(null);

    useEffect(() => {
        const login = searchParams.get('login');
        const message = searchParams.get('message');

        // 쿠키 기반 인증으로 변경되어 URL에 토큰이 오지 않음
        // 백엔드에서 쿠키로 토큰을 설정하고 리다이렉트함

        if (login === 'success') {
            setLoginStatus({ success: true, message: message ? decodeURIComponent(message) : '로그인 성공' });
            // 로그인 성공 메시지 표시 후 /onboarding으로 리다이렉트
            const timer = setTimeout(() => {
                router.replace('/onboarding');
            }, 1500);

            // cleanup 함수로 메모리 누수 방지
            return () => clearTimeout(timer);
        }
    }, [searchParams, router]);


    return (
        <div
            className="min-h-screen px-4 py-8 relative"
            style={{
                backgroundImage: 'url(/hanoks/hanok4.jpg)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
            }}
        >
            {/* 배경 오버레이 */}
            <div className="absolute inset-0 bg-black/90 pointer-events-none z-0"></div>

            {/* 중앙 컨텐츠 */}
            <div className="flex min-h-screen items-center justify-center relative z-10">
                <div className="w-full max-w-lg px-6 sm:px-8">
                    {loginStatus?.success && (
                        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg animate-fade-in">
                            <h2 className="text-green-800 font-bold text-lg mb-2">로그인 성공!</h2>
                            <p className="text-green-700">{loginStatus.message}</p>
                            <p className="text-green-600 text-sm mt-2">곧 홈으로 이동합니다...</p>
                        </div>
                    )}

                    {/* 모달 스타일 박스 */}
                    <div
                        className={`rounded-2xl shadow-xl p-6 sm:p-8 space-y-4 sm:space-y-6 opacity-0 animate-fade-in-up relative overflow-hidden ${loginStatus?.success ? 'opacity-50 pointer-events-none' : ''}`}
                        style={{
                            backgroundImage: 'url(/hanoks/hanok2.jpg)',
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                            backgroundRepeat: 'no-repeat',
                        }}
                    >
                        {/* 배경 오버레이 */}
                        <div className="absolute inset-0 bg-white/0 z-0"></div>

                        {/* 콘텐츠 */}
                        <div className="relative z-10">
                            {/* 중앙 큰 로고 */}
                            <div className="text-center mb-8 space-y-4">
                                <div className="flex justify-center">
                                    <div className="relative logo-container">
                                        <div className="absolute inset-0 animate-pulse-slow blur-3xl opacity-20 bg-gradient-to-r from-red-400 via-blue-400 to-red-400"></div>
                                        <Image
                                            src="/img/logo3.png"
                                            alt="Kroaddy"
                                            width={240}
                                            height={240}
                                            priority
                                            className="w-48 sm:w-56 md:w-64 lg:w-72 h-auto relative animate-float logo-shadow"
                                        />
                                    </div>
                                </div>
                                <h1 className="text-3xl sm:text-4xl md:text-4xl lg:text-4xl font-bold animate-float-subtle" style={{ color: '#FFFFFF' }}>Kroaddy</h1>
                            </div>

                            {/* 안내 문구 */}
                            <div className="flex items-center justify-center mb-8">
                                <div className="flex-1 border-t border-gray-300"></div>
                                <p className="px-4 text-sm sm:text-base text-white font-normal">Log into your account</p>
                                <div className="flex-1 border-t border-gray-300"></div>
                            </div>

                            {/* 소셜 로그인 버튼들 */}
                            <div className="space-y-3">
                                {/* 구글 로그인 */}
                                <button
                                    onClick={handleGoogleLogin}
                                    className="w-full rounded-lg border border-solid border-gray-300 transition-colors flex items-center justify-center gap-4 hover:bg-gray-50 text-sm sm:text-base h-12 px-4 bg-white text-gray-900 font-medium"
                                >
                                    <div className="w-5 h-5 flex-shrink-0 flex items-center justify-center">
                                        <svg width="20" height="20" viewBox="0 0 24 24" className="w-full h-full">
                                            <path
                                                fill="#4285F4"
                                                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                            />
                                            <path
                                                fill="#34A853"
                                                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                            />
                                            <path
                                                fill="#FBBC05"
                                                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                                            />
                                            <path
                                                fill="#EA4335"
                                                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                            />
                                        </svg>
                                    </div>
                                    Continue with Google
                                </button>

                                {/* 카카오 로그인 */}
                                <button
                                    onClick={handleKakaoLogin}
                                    className="w-full rounded-lg border border-solid border-transparent transition-colors flex items-center justify-center gap-4 hover:opacity-90 text-sm sm:text-base h-12 px-4 bg-[#FEE500] text-[#000000] font-medium"
                                >
                                    <div className="w-5 h-5 flex-shrink-0 flex items-center justify-center">
                                        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor" className="w-full h-full">
                                            <path d="M10.5 3.217c4.514 0 8 2.708 8 6.004 0 3.758-4.045 6.184-8 5.892-1.321-.093-1.707-.17-2.101-.23-1.425.814-2.728 2.344-3.232 2.334-.325-.19.811-2.896.533-3.114-.347-.244-3.157-1.329-3.2-4.958 0-3.199 3.486-5.928 8-5.928Z" />
                                        </svg>
                                    </div>
                                    Continue with Kakao
                                </button>

                                {/* 네이버 로그인 */}
                                <button
                                    onClick={handleNaverLogin}
                                    className="w-full rounded-lg border border-solid border-transparent transition-colors flex items-center justify-center gap-4 hover:opacity-90 text-sm sm:text-base h-12 px-4 bg-[#03C75A] text-white font-medium"
                                >
                                    <div className="w-4 h-4 flex-shrink-0 flex items-center justify-center">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="w-full h-full">
                                            <path d="M16.273 12.845L7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845z" />
                                        </svg>
                                    </div>
                                    Continue with Naver
                                </button>
                            </div>

                            {/* 개인정보 처리방침 */}
                            <div className="pt-4">
                                <p className="text-xs text-gray-500 text-center leading-relaxed">
                                    By logging in, you agree to the <a href="#" className="text-blue-600 hover:underline">Privacy Policy</a> and <a href="#" className="text-blue-600 hover:underline">Terms of Service</a>.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function Home() {
    return (
        <Suspense fallback={<div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>}>
            <LoginContent />
        </Suspense>
    );
}

