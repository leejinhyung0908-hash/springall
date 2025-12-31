'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { API_BASE_URL } from '@/lib/api';

export default function Dashboard() {
    const router = useRouter();
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        // 백엔드 API로 인증 상태 확인 (쿠키 자동 전송)
        fetch(`${API_BASE_URL}/api/auth/me`, {
            credentials: 'include', // 쿠키 포함
        })
            .then(async (res) => {
                if (res.ok) {
                    setIsAuthenticated(true);
                    const userData = await res.json();
                    if (userData) setUser(userData);
                } else {
                    setIsAuthenticated(false);
                    router.push('/');
                }
            })
            .catch(() => {
                setIsAuthenticated(false);
                router.push('/');
            })
            .finally(() => {
                setLoading(false);
            });
    }, [router]);

    const handleLogout = async () => {
        // 백엔드 로그아웃 API 호출 (쿠키 삭제)
        try {
            await fetch(`${API_BASE_URL}/api/auth/logout`, {
                method: 'POST',
                credentials: 'include', // 쿠키 포함
            });
        } catch (error) {
            console.error('로그아웃 실패:', error);
        }

        router.push('/');
    };

    if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold text-gray-900">대시보드</h1>
                    <button onClick={handleLogout} className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">로그아웃</button>
                </div>

                <div className="space-y-4">
                    <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                        <p className="text-green-800 font-semibold">✓ 로그인 성공</p>
                        <p className="text-green-600 text-sm mt-1">Gateway를 통해 로그인이 완료되었습니다.</p>
                    </div>

                    {user && (
                        <div className="p-4 bg-gray-50 rounded-lg">
                            <h2 className="text-xl font-semibold mb-2">사용자 정보</h2>
                            <pre className="text-sm overflow-auto">{JSON.stringify(user, null, 2)}</pre>
                        </div>
                    )}

                    <div className="p-4 bg-blue-50 rounded-lg">
                        <h2 className="text-xl font-semibold mb-2">인증 정보</h2>
                        <p className="text-sm text-gray-600">쿠키 기반 인증이 활성화되어 있습니다.</p>
                        <p className="text-sm text-gray-500 mt-1">토큰은 HttpOnly 쿠키로 안전하게 저장됩니다.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

