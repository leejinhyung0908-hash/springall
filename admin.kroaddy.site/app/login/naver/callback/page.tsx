'use client';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function NaverCallbackPage() {
    const router = useRouter();

    useEffect(() => {
        // 백엔드에서 쿠키로 토큰을 설정하고 리다이렉트했으므로
        // 여기서는 대시보드로 이동
        console.log('✅ 네이버 로그인 성공, 대시보드로 이동합니다...');

        // 로그인 성공 로그 기록 (백엔드로 직접 전송)
        import('@/lib/api').then(({ API_BASE_URL }) => {
            fetch(`${API_BASE_URL}/api/log/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include', // 쿠키 포함
                body: JSON.stringify({
                    action: '로그인 성공',
                    url: window.location.href,
                }),
            }).catch(() => { });
        });

        router.replace('/dashboard');
    }, [router]);

    return (
        <div className="flex min-h-screen items-center justify-center">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">네이버 로그인 처리 중...</p>
            </div>
        </div>
    );
}

