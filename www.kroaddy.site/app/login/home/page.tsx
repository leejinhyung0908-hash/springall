'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginHomeRedirect() {
    const router = useRouter();

    useEffect(() => {
        // /login/home을 /home으로 리다이렉트
        router.replace('/home');
    }, [router]);

    return (
        <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">페이지 이동 중...</p>
            </div>
        </div>
    );
}

