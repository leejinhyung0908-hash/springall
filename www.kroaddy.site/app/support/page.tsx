'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Home, MessageSquare, MapPin, User, LogOut, Settings, FileText, Heart, ChevronRight, HeadphonesIcon, Mail, Phone, Clock, HelpCircle, Send, ChevronDown, ChevronUp, CheckCircle, Clock as ClockIcon } from 'lucide-react';
import { t, getCurrentLanguage } from '@/lib/i18n';
import { LanguageCode } from '@/lib/types';

export default function SupportPage() {
    const router = useRouter();
    const [activeMenu, setActiveMenu] = useState('support');
    const [uiLanguage, setUiLanguage] = useState<LanguageCode>(getCurrentLanguage());
    const [expandedFaq, setExpandedFaq] = useState<number | null>(null);
    const [inquiryForm, setInquiryForm] = useState({
        name: '',
        email: '',
        subject: '',
        message: ''
    });

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
        { id: 'support', labelKey: 'sidebar.support', icon: HeadphonesIcon },
        { id: 'inquiry', label: '내 문의 내역', icon: FileText },
        { id: 'mypage', labelKey: 'mypage.myPage', icon: User }
    ];

    const faqs = [
        {
            id: 1,
            question: 'Kroaddy는 어떤 서비스인가요?',
            answer: 'Kroaddy는 한국 여행을 위한 AI 기반 여행 가이드 서비스입니다. 실시간 번역, 맞춤형 여행 경로 추천, 장소 정보 제공 등 다양한 기능을 제공합니다.'
        },
        {
            id: 2,
            question: '무료로 사용할 수 있나요?',
            answer: '네, Kroaddy의 기본 기능은 무료로 사용하실 수 있습니다. 일부 고급 기능은 프리미엄 플랜에서 제공됩니다.'
        },
        {
            id: 3,
            question: '어떤 언어를 지원하나요?',
            answer: '한국어, 영어, 일본어, 중국어(간체/번체), 프랑스어, 독일어, 베트남어 등 19개 언어를 지원합니다.'
        },
        {
            id: 4,
            question: '오프라인에서도 사용할 수 있나요?',
            answer: '일부 기능은 오프라인에서도 사용 가능하지만, 실시간 번역 및 지도 기능은 인터넷 연결이 필요합니다.'
        },
        {
            id: 5,
            question: '계정을 삭제하려면 어떻게 해야 하나요?',
            answer: '마이페이지 > 계정 설정에서 계정 삭제를 요청하실 수 있습니다. 삭제 요청 후 7일 이내에 처리됩니다.'
        },
        {
            id: 6,
            question: '기술적 문제가 발생했을 때 어떻게 해야 하나요?',
            answer: '이 페이지 하단의 문의하기 폼을 통해 문제를 신고해주시거나, 고객센터 이메일로 직접 문의해주세요.'
        }
    ];

    // 문의 내역 예시 데이터
    const inquiries = [
        {
            id: 1,
            subject: '번역 기능이 작동하지 않습니다',
            message: '실시간 번역 기능을 사용하려고 했는데 작동하지 않습니다. 어떻게 해결할 수 있나요?',
            date: '2024.12.15',
            status: '답변완료',
            reply: '안녕하세요. 번역 기능 문제로 문의해주셔서 감사합니다. 인터넷 연결을 확인해주시고, 페이지를 새로고침해보시기 바랍니다. 문제가 지속되면 고객센터로 연락주세요.'
        },
        {
            id: 2,
            subject: '계정 비밀번호 변경 문의',
            message: '비밀번호를 변경하고 싶은데 방법을 모르겠습니다. 도와주세요.',
            date: '2024.12.10',
            status: '답변완료',
            reply: '비밀번호 변경은 마이페이지 > 계정 설정 > 비밀번호 변경에서 가능합니다. 추가 도움이 필요하시면 연락주세요.'
        },
        {
            id: 3,
            subject: '프리미엄 플랜 가격 문의',
            message: '프리미엄 플랜의 가격과 제공되는 기능에 대해 알고 싶습니다.',
            date: '2024.12.08',
            status: '대기중',
            reply: null
        },
        {
            id: 4,
            subject: '여행 경로 추천 기능 개선 제안',
            message: '여행 경로 추천 기능이 좋은데, 더 많은 옵션을 선택할 수 있으면 좋겠습니다.',
            date: '2024.12.05',
            status: '답변완료',
            reply: '소중한 의견 감사합니다. 추천 기능 개선을 위해 검토 중이며, 곧 업데이트될 예정입니다.'
        }
    ];

    const handleSubmitInquiry = (e: React.FormEvent) => {
        e.preventDefault();
        // 문의 제출 로직 (추후 백엔드 연동)
        alert('문의가 접수되었습니다. 빠른 시일 내에 답변드리겠습니다.');
        setInquiryForm({ name: '', email: '', subject: '', message: '' });
    };

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
                                    // support와 inquiry는 같은 페이지 내에서 전환
                                }}
                                className={`w-full flex items-center gap-3 px-4 py-3 mb-2 rounded-lg transition-all duration-300 ${isActive
                                    ? 'bg-black text-white shadow-md'
                                    : 'text-gray-700 hover:bg-gray-100/80 hover:text-gray-900'
                                    }`}
                            >
                                <Icon className="w-5 h-5" />
                                <span className="font-medium">{item.labelKey ? t(item.labelKey, uiLanguage) : item.label}</span>
                            </button>
                        );
                    })}
                </nav>
            </div>

            {/* 중앙 메인 콘텐츠 */}
            <div className="flex-1 overflow-auto relative z-10">
                <div className="max-w-4xl mx-auto p-8">
                    {activeMenu === 'inquiry' ? (
                        /* 내 문의 내역 페이지 */
                        <>
                            <div className="mb-8">
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-purple-200 rounded-full flex items-center justify-center">
                                        <FileText className="w-8 h-8 text-purple-600" />
                                    </div>
                                    <div>
                                        <h1 className="text-3xl font-bold text-gray-900">내 문의 내역</h1>
                                        <p className="text-gray-600 mt-1">제출하신 문의 내역을 확인하실 수 있습니다.</p>
                                    </div>
                                </div>
                            </div>

                            {/* 문의 내역 목록 */}
                            <div className="space-y-4">
                                {inquiries.length === 0 ? (
                                    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-12 border border-gray-200/50 text-center">
                                        <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                                        <p className="text-gray-500 text-lg">문의 내역이 없습니다.</p>
                                        <p className="text-gray-400 text-sm mt-2">문의하기를 통해 새로운 문의를 제출해보세요.</p>
                                    </div>
                                ) : (
                                    inquiries.map((inquiry) => (
                                        <div
                                            key={inquiry.id}
                                            className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 hover:shadow-lg transition-all duration-300 overflow-hidden"
                                        >
                                            <div className="p-6">
                                                <div className="flex items-start justify-between mb-4">
                                                    <div className="flex-1">
                                                        <div className="flex items-center gap-3 mb-2">
                                                            <h3 className="text-lg font-semibold text-gray-900">{inquiry.subject}</h3>
                                                            <span
                                                                className={`px-3 py-1 rounded-full text-xs font-medium ${
                                                                    inquiry.status === '답변완료'
                                                                        ? 'bg-green-100 text-green-700'
                                                                        : 'bg-yellow-100 text-yellow-700'
                                                                }`}
                                                            >
                                                                {inquiry.status}
                                                            </span>
                                                        </div>
                                                        <p className="text-sm text-gray-500 mb-3">{inquiry.date}</p>
                                                    </div>
                                                    {inquiry.status === '답변완료' ? (
                                                        <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                                                    ) : (
                                                        <ClockIcon className="w-5 h-5 text-yellow-500 flex-shrink-0" />
                                                    )}
                                                </div>

                                                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                                                    <p className="text-sm font-medium text-gray-700 mb-2">문의 내용</p>
                                                    <p className="text-gray-700 leading-relaxed">{inquiry.message}</p>
                                                </div>

                                                {inquiry.reply && (
                                                    <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
                                                        <div className="flex items-center gap-2 mb-2">
                                                            <Mail className="w-4 h-4 text-blue-600" />
                                                            <p className="text-sm font-medium text-blue-900">답변</p>
                                                        </div>
                                                        <p className="text-gray-700 leading-relaxed">{inquiry.reply}</p>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </>
                    ) : (
                        /* 고객센터 메인 페이지 */
                        <>
                            {/* 헤더 */}
                            <div className="mb-8">
                                <div className="flex items-center gap-4 mb-4">
                                    <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-full flex items-center justify-center">
                                        <HeadphonesIcon className="w-8 h-8 text-blue-600" />
                                    </div>
                                    <div>
                                        <h1 className="text-3xl font-bold text-gray-900">고객센터</h1>
                                        <p className="text-gray-600 mt-1">언제든지 문의해주세요. 빠르고 친절하게 도와드리겠습니다.</p>
                                    </div>
                                </div>
                            </div>

                    {/* 연락처 정보 카드 */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-6 border border-gray-200/50">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                                    <Phone className="w-6 h-6 text-blue-600" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900">전화 문의</h3>
                                </div>
                            </div>
                            <p className="text-2xl font-bold text-gray-900 mb-1">1588-0000</p>
                            <p className="text-sm text-gray-500">평일 09:00 - 18:00</p>
                        </div>

                        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-6 border border-gray-200/50">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                    <Mail className="w-6 h-6 text-green-600" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900">이메일 문의</h3>
                                </div>
                            </div>
                            <p className="text-lg font-semibold text-gray-900 mb-1">support@kroaddy.com</p>
                            <p className="text-sm text-gray-500">24시간 접수 가능</p>
                        </div>

                        <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-6 border border-gray-200/50">
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                                    <Clock className="w-6 h-6 text-purple-600" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900">운영 시간</h3>
                                </div>
                            </div>
                            <p className="text-lg font-semibold text-gray-900 mb-1">평일 09:00 - 18:00</p>
                            <p className="text-sm text-gray-500">주말/공휴일 휴무</p>
                        </div>
                    </div>

                    {/* FAQ 섹션 */}
                    <div className="mb-8">
                        <div className="flex items-center gap-3 mb-6">
                            <HelpCircle className="w-6 h-6 text-gray-700" />
                            <h2 className="text-2xl font-bold text-gray-900">자주 묻는 질문 (FAQ)</h2>
                        </div>
                        <div className="space-y-3">
                            {faqs.map((faq) => (
                                <div
                                    key={faq.id}
                                    className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm border border-gray-200/50 overflow-hidden"
                                >
                                    <button
                                        onClick={() => setExpandedFaq(expandedFaq === faq.id ? null : faq.id)}
                                        className="w-full flex items-center justify-between p-6 text-left hover:bg-gray-50/50 transition-colors"
                                    >
                                        <span className="font-semibold text-gray-900 pr-4">{faq.question}</span>
                                        {expandedFaq === faq.id ? (
                                            <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
                                        ) : (
                                            <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                                        )}
                                    </button>
                                    {expandedFaq === faq.id && (
                                        <div className="px-6 pb-6 pt-0">
                                            <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* 문의하기 폼 */}
                    <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-sm p-8 border border-gray-200/50">
                        <div className="flex items-center gap-3 mb-6">
                            <Send className="w-6 h-6 text-gray-700" />
                            <h2 className="text-2xl font-bold text-gray-900">문의하기</h2>
                        </div>
                        <form onSubmit={handleSubmitInquiry} className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">이름</label>
                                    <input
                                        type="text"
                                        value={inquiryForm.name}
                                        onChange={(e) => setInquiryForm({ ...inquiryForm, name: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">이메일</label>
                                    <input
                                        type="email"
                                        value={inquiryForm.email}
                                        onChange={(e) => setInquiryForm({ ...inquiryForm, email: e.target.value })}
                                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        required
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">제목</label>
                                <input
                                    type="text"
                                    value={inquiryForm.subject}
                                    onChange={(e) => setInquiryForm({ ...inquiryForm, subject: e.target.value })}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">문의 내용</label>
                                <textarea
                                    value={inquiryForm.message}
                                    onChange={(e) => setInquiryForm({ ...inquiryForm, message: e.target.value })}
                                    rows={6}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all duration-300 font-semibold shadow-md hover:shadow-lg"
                            >
                                문의 제출하기
                            </button>
                        </form>
                    </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}

