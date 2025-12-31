'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Home, MessageSquare, MapPin, User, LogOut, Settings, FileText, Heart, ChevronRight, Building2, Target, Users, Award, Globe, Lightbulb, Rocket } from 'lucide-react';
import { t, getCurrentLanguage } from '@/lib/i18n';
import { LanguageCode } from '@/lib/types';

export default function AboutPage() {
    const router = useRouter();
    const [activeMenu, setActiveMenu] = useState('about');
    const [uiLanguage, setUiLanguage] = useState<LanguageCode>(getCurrentLanguage());

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

    const menuItems = [
        { id: 'home', labelKey: 'mypage.home', icon: Home },
        { id: 'mypage', labelKey: 'mypage.myPage', icon: User }
    ];

    const values = [
        {
            icon: Globe,
            title: '글로벌 연결',
            description: '언어와 문화의 장벽을 넘어 전 세계 여행자들이 한국을 더 쉽게 탐험할 수 있도록 돕습니다.'
        },
        {
            icon: Lightbulb,
            title: '혁신적인 기술',
            description: 'AI와 실시간 번역 기술을 활용하여 차세대 여행 경험을 제공합니다.'
        },
        {
            icon: Users,
            title: '사용자 중심',
            description: '여행자의 니즈를 최우선으로 생각하며, 지속적으로 서비스를 개선합니다.'
        },
        {
            icon: Rocket,
            title: '지속적 성장',
            description: '한국 여행 생태계의 발전을 위해 끊임없이 노력하고 성장합니다.'
        }
    ];

    const milestones = [
        { year: '2024', event: 'Kroaddy 서비스 런칭' },
        { year: '2024', event: '19개 언어 지원 확대' },
        { year: '2024', event: 'AI 여행 가이드 기능 출시' },
        { year: '2024', event: '실시간 번역 서비스 도입' }
    ];

    return (
        <div className="flex h-screen relative overflow-hidden">
            {/* 배경 애니메이션 요소들 */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
                <div className="floating-circle floating-circle-1"></div>
                <div className="floating-circle floating-circle-2"></div>
                <div className="floating-circle floating-circle-3"></div>
            </div>

            {/* 왼쪽 사이드바 */}
            <div className="w-64 bg-white/80 backdrop-blur-md border-r border-gray-200/50 flex flex-col relative z-10 shadow-lg">
                {/* 로고 */}
                <div className="p-6">
                    <div className="bg-gradient-to-r from-red-50 to-blue-50 rounded-lg px-4 py-2 inline-block border border-gray-200/50 shadow-sm">
                        <span className="text-2xl font-bold text-black">Kroaddy</span>
                    </div>
                </div>

                {/* 네비게이션 메뉴 */}
                <nav className="flex-1 px-4">
                    {menuItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = activeMenu === item.id;
                        return (
                            <button
                                key={item.id}
                                onClick={() => {
                                    setActiveMenu(item.id);
                                    if (item.id === 'home') {
                                        router.push('/home');
                                    } else if (item.id === 'mypage') {
                                        router.push('/mypage');
                                    }
                                }}
                                className={`w-full flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-all duration-300 ${isActive
                                    ? 'bg-black text-white shadow-md'
                                    : 'text-gray-700 hover:bg-gray-100/80 hover:text-gray-900'
                                    }`}
                            >
                                <Icon className="w-5 h-5" />
                                <span className="font-medium">{t(item.labelKey, uiLanguage)}</span>
                            </button>
                        );
                    })}
                </nav>
            </div>

            {/* 중앙 메인 콘텐츠 */}
            <div className="flex-1 overflow-auto relative z-10">
                <div className="max-w-4xl mx-auto p-8">
                    {/* 헤더 */}
                    <div className="mb-12">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-purple-200 rounded-full flex items-center justify-center">
                                <Building2 className="w-8 h-8 text-purple-600" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-gray-900">회사 소개</h1>
                                <p className="text-gray-600 mt-1">Kroaddy와 함께 한국 여행의 새로운 경험을 만들어가세요.</p>
                            </div>
                        </div>
                    </div>

                    {/* 회사 소개 섹션 */}
                    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-8 border border-gray-200/50 mb-8">
                        <h2 className="text-2xl font-bold text-gray-900 mb-4">Kroaddy에 오신 것을 환영합니다</h2>
                        <div className="space-y-4 text-gray-700 leading-relaxed">
                            <p>
                                Kroaddy는 AI 기반의 차세대 한국 여행 가이드 플랫폼입니다. 전 세계 여행자들이 언어의 장벽 없이 
                                한국의 아름다움을 탐험할 수 있도록 돕는 것이 우리의 목표입니다.
                            </p>
                            <p>
                                실시간 번역, 맞춤형 여행 경로 추천, 상세한 장소 정보 제공 등 다양한 기능을 통해 
                                여행자들이 더욱 편리하고 즐거운 한국 여행을 경험할 수 있도록 지원합니다.
                            </p>
                            <p>
                                우리는 기술 혁신과 사용자 경험 개선을 통해 한국 여행 생태계의 발전에 기여하고 있으며, 
                                앞으로도 더 많은 여행자들이 한국을 사랑할 수 있도록 노력하겠습니다.
                            </p>
                        </div>
                    </div>

                    {/* 비전 & 미션 */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 backdrop-blur-sm rounded-xl shadow-sm p-8 border border-blue-200/50">
                            <div className="flex items-center gap-3 mb-4">
                                <Target className="w-8 h-8 text-blue-600" />
                                <h3 className="text-xl font-bold text-gray-900">비전</h3>
                            </div>
                            <p className="text-gray-700 leading-relaxed">
                                전 세계 모든 여행자가 언어와 문화의 장벽 없이 한국을 자유롭게 탐험할 수 있는 
                                글로벌 여행 플랫폼이 되는 것입니다.
                            </p>
                        </div>

                        <div className="bg-gradient-to-br from-green-50 to-green-100/50 backdrop-blur-sm rounded-xl shadow-sm p-8 border border-green-200/50">
                            <div className="flex items-center gap-3 mb-4">
                                <Rocket className="w-8 h-8 text-green-600" />
                                <h3 className="text-xl font-bold text-gray-900">미션</h3>
                            </div>
                            <p className="text-gray-700 leading-relaxed">
                                혁신적인 기술과 사용자 중심의 서비스를 통해 한국 여행의 접근성을 높이고, 
                                더 많은 사람들이 한국의 문화와 아름다움을 경험할 수 있도록 돕는 것입니다.
                            </p>
                        </div>
                    </div>

                    {/* 핵심 가치 */}
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6">핵심 가치</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {values.map((value, index) => {
                                const Icon = value.icon;
                                return (
                                    <div
                                        key={index}
                                        className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-6 border border-gray-200/50 hover:shadow-lg transition-all duration-300"
                                    >
                                        <div className="flex items-center gap-4 mb-4">
                                            <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
                                                <Icon className="w-6 h-6 text-blue-600" />
                                            </div>
                                            <h3 className="text-lg font-bold text-gray-900">{value.title}</h3>
                                        </div>
                                        <p className="text-gray-700 leading-relaxed">{value.description}</p>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* 주요 연혁 */}
                    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-8 border border-gray-200/50 mb-8">
                        <div className="flex items-center gap-3 mb-6">
                            <Award className="w-6 h-6 text-gray-700" />
                            <h2 className="text-2xl font-bold text-gray-900">주요 연혁</h2>
                        </div>
                        <div className="space-y-4">
                            {milestones.map((milestone, index) => (
                                <div key={index} className="flex items-center gap-4 pb-4 border-b border-gray-200 last:border-0">
                                    <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                        <span className="text-lg font-bold text-purple-600">{milestone.year}</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-gray-900 font-medium">{milestone.event}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* 팀 소개 */}
                    <div className="bg-gradient-to-br from-gray-50 to-gray-100/50 backdrop-blur-sm rounded-xl shadow-sm p-8 border border-gray-200/50">
                        <div className="flex items-center gap-3 mb-6">
                            <Users className="w-6 h-6 text-gray-700" />
                            <h2 className="text-2xl font-bold text-gray-900">우리 팀</h2>
                        </div>
                        <p className="text-gray-700 leading-relaxed mb-4">
                            Kroaddy는 다양한 배경과 전문성을 가진 팀원들로 구성되어 있습니다. 
                            개발자, 디자이너, 여행 전문가, 언어학자 등 각 분야의 전문가들이 모여 
                            최고의 여행 경험을 제공하기 위해 노력하고 있습니다.
                        </p>
                        <p className="text-gray-700 leading-relaxed">
                            우리는 열정과 혁신 정신으로 매일 더 나은 서비스를 만들기 위해 노력하며, 
                            사용자들의 피드백을 소중히 여기고 지속적으로 개선해나가고 있습니다.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

