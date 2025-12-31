'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, User, Edit2 } from 'lucide-react';
import Image from 'next/image';
import { t, getCurrentLanguage } from '@/lib/i18n';
import { LanguageCode } from '@/lib/types';

interface OnboardingData {
    gender: string;
    age: string;
    nationality: string;
    religion: string;
    dietary: string;
}

export default function ProfilePage() {
    const router = useRouter();
    const [onboardingData, setOnboardingData] = useState<OnboardingData | null>(null);
    const [completedAt, setCompletedAt] = useState<string | null>(null);
    const [uiLanguage, setUiLanguage] = useState<LanguageCode>(getCurrentLanguage());
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    // 언어 변경 감지
    useEffect(() => {
        const handleLanguageChange = () => {
            setUiLanguage(getCurrentLanguage());
        };

        window.addEventListener('languageChanged', handleLanguageChange as EventListener);
        return () => {
            window.removeEventListener('languageChanged', handleLanguageChange as EventListener);
        };
    }, []);

    useEffect(() => {
        // 로컬 스토리지에서 온보딩 데이터 불러오기
        if (typeof window !== 'undefined') {
            const savedData = localStorage.getItem('onboardingData');
            const savedDate = localStorage.getItem('onboardingCompletedAt');
            const authStatus = localStorage.getItem('authStatus');

            if (savedData) {
                try {
                    setOnboardingData(JSON.parse(savedData));
                } catch (error) {
                    console.error('Failed to parse onboarding data:', error);
                }
            }

            if (savedDate) {
                setCompletedAt(savedDate);
            }

            // 인증 상태 확인 (인증 완료 시 'completed'로 저장)
            if (authStatus === 'completed') {
                setIsAuthenticated(true);
            }
        }
    }, []);

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const infoItems = [
        { labelKey: 'profile.gender', key: 'gender', value: onboardingData?.gender || t('profile.notEntered', uiLanguage) },
        { labelKey: 'profile.age', key: 'age', value: onboardingData?.age || t('profile.notEntered', uiLanguage) },
        { labelKey: 'profile.nationality', key: 'nationality', value: onboardingData?.nationality || t('profile.notEntered', uiLanguage) },
        { labelKey: 'profile.religion', key: 'religion', value: onboardingData?.religion || t('profile.notEntered', uiLanguage) },
        { labelKey: 'profile.dietary', key: 'dietary', value: onboardingData?.dietary || t('profile.notEntered', uiLanguage) },
    ];

    return (
        <div
            className="min-h-screen"
            style={{
                backgroundImage: 'url(/img/paper2.png)',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
            }}
        >
            <div className="max-w-4xl mx-auto px-4 py-8">
                {/* 헤더 */}
                <div className="mb-8">
                    <button
                        onClick={() => router.back()}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors mb-6"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        <span>{t('profile.back', uiLanguage)}</span>
                    </button>

                    <div className="bg-white rounded-2xl shadow-xl p-8">
                        {/* 프로필 헤더 */}
                        <div className="flex items-center justify-between mb-8">
                            <div className="flex items-center gap-6">
                                <div className="w-24 h-24 bg-gray-200 rounded-full flex items-center justify-center">
                                    <User className="w-12 h-12 text-gray-400" />
                                </div>
                                <div>
                                    <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('profile.manageInfo', uiLanguage)}</h1>
                                    {completedAt && (
                                        <p className="text-sm text-gray-500">
                                            {t('profile.infoDate', uiLanguage)} {formatDate(completedAt)}
                                        </p>
                                    )}
                                </div>
                            </div>
                            <button className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2">
                                <Edit2 className="w-4 h-4" />
                                <span>{t('profile.edit', uiLanguage)}</span>
                            </button>
                        </div>

                        {/* 정보 카드 */}
                        <div className="space-y-4">
                            {infoItems.map((item) => (
                                <div
                                    key={item.key}
                                    className="bg-gray-50 rounded-xl p-6 hover:bg-gray-100 transition-colors"
                                >
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="text-sm text-gray-500 mb-1">{t(item.labelKey, uiLanguage)}</p>
                                            <p className="text-lg font-semibold text-gray-900">
                                                {item.value}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* 데이터가 없을 때 */}
                        {!onboardingData && (
                            <div className="text-center py-12">
                                <p className="text-gray-500 mb-4">{t('profile.noData', uiLanguage)}</p>
                                <button
                                    onClick={() => router.push('/onboarding')}
                                    className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
                                >
                                    {t('profile.goToEnter', uiLanguage)}
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* 백엔드 연동 안내 - 인증 완료 시에만 표시 */}
                {isAuthenticated && (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
                        <h3 className="text-lg font-semibold text-blue-900 mb-2">{t('profile.backendGuide', uiLanguage)}</h3>
                        <p className="text-sm text-blue-800 mb-4">
                            {t('profile.backendGuideDesc', uiLanguage)}
                        </p>
                        <ul className="text-sm text-blue-700 space-y-2 list-disc list-inside">
                            <li>{t('profile.backendGuideItem1', uiLanguage)}</li>
                            <li>{t('profile.backendGuideItem2', uiLanguage)}</li>
                            <li>{t('profile.backendGuideItem3', uiLanguage)}</li>
                            <li>{t('profile.backendGuideItem4', uiLanguage)}</li>
                        </ul>
                    </div>
                )}
            </div>
        </div>
    );
}

