// components/Onboarding.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

// 온보딩 페이지
export default function Onboarding() {
    const router = useRouter();
    const [step, setStep] = useState(0);
    const [formData, setFormData] = useState({
        gender: '',
        age: '',
        birthYear: '',
        birthMonth: '',
        birthDay: '',
        nationality: '',
        religion: '',
        dietary: '',
    });

    const questions = [
        { key: 'gender', question: 'Please specify your gender.', options: ['Male', 'Female', 'Other / Non-disclosure'] },
        { key: 'age', question: 'Please provide your birth.', type: 'birthday' },
        { key: 'nationality', question: 'Please indicate your place of residence.', options: ['South Korea', 'United States', 'China', 'Japan', 'Vietnam', 'Thailand', 'Philippines', 'India', 'United Kingdom', 'Others'] },
        { key: 'religion', question: 'Please specify your religious affiliation, if any.', options: ['No Religion', 'Christianity', 'Islam', 'Buddhism', 'Others'] },
        { key: 'dietary', question: ' Lastly, please describe your dietary preferences or restrictions.', options: ['Normal', 'Vegetarian(Lacto/Ovo)', 'Vegan', 'Pescetarian', 'Other'] },
    ];

    const current = questions[step];
    const progress = ((step + 1) / questions.length) * 100;

    const handleNext = () => {
        if (step < questions.length - 1) {
            setStep(step + 1);
        } else {
            // 모든 질문 완료 → 로컬 스토리지에 저장 후 홈으로 이동
            console.log('완료된 데이터:', formData);

            // 로컬 스토리지에 온보딩 데이터 저장
            if (typeof window !== 'undefined') {
                localStorage.setItem('onboardingData', JSON.stringify(formData));
                localStorage.setItem('onboardingCompletedAt', new Date().toISOString());
            }

            // TODO: 여기서 온보딩 데이터를 백엔드로 전송
            // API 호출 후 홈으로 이동
            router.replace('/home');
        }
    };

    const handleInput = (value: string) => {
        setFormData({ ...formData, [current.key]: value });
    };

    // 국가에 맞는 기본 언어 매핑
    const getLanguageByNationality = (nationality: string): string => {
        const nationalityToLanguage: Record<string, string> = {
            'South Korea': '한국어',
            'United States': 'English',
            'China': '简体中文',
            'Japan': '日本語',
            'Vietnam': 'Tiếng Việt',
            'Thailand': 'ไทย',
            'Philippines': 'English',
            'India': 'English',
            'United Kingdom': 'English',
            'Others': '한국어',
        };
        return nationalityToLanguage[nationality] || '한국어';
    };

    const handleOptionSelect = (value: string) => {
        handleInput(value);
        
        // 국가 선택 시 해당 국가에 맞는 언어를 localStorage에 저장
        if (current.key === 'nationality') {
            const defaultLanguage = getLanguageByNationality(value);
            if (typeof window !== 'undefined') {
                // 국가 선택 시 항상 해당 국가의 언어로 설정
                localStorage.setItem('selectedLanguage', defaultLanguage);
                // 온보딩에서 자동 설정된 언어임을 표시 (사용자가 명시적으로 선택한 것이 아님)
                localStorage.setItem('languageManuallySelected', 'false');
                // 언어 변경 이벤트 발생
                window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: defaultLanguage } }));
            }
        }
        
        // 옵션 선택 시 자동으로 다음으로 이동
        setTimeout(() => {
            handleNext();
        }, 300);
    };

    return (
        <>
            <style jsx global>{`
                /* Select가 아래로 펼쳐지도록 */
                select {
                    direction: ltr;
                }
                select option {
                    direction: ltr;
                }
                /* 셀렉트가 항상 아래로 펼쳐지도록 보장 */
                select:focus {
                    position: relative;
                    z-index: 10;
                }
                /* 셀렉트 드롭다운 크기 제한 */
                select[size] {
                    max-height: 200px;
                    overflow-y: auto;
                }
            `}</style>
            <div
                className="min-h-screen px-4 py-8 relative"
                style={{
                    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                    backgroundImage: 'url(/hanoks/hanok5.jpg)',
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    backgroundRepeat: 'no-repeat',
                }}
            >
                {/* 배경 오버레이 */}
                <div className="absolute inset-0 bg-black/0 pointer-events-none z-0"></div>
                {/* 중앙 컨텐츠 */}
                <div className="flex min-h-screen items-center justify-center py-8 relative z-10">
                    <div className="w-full max-w-lg sm:max-w-xl md:max-w-2xl px-4 sm:px-6 md:px-8">
                        {/* 모달 스타일 박스 */}
                        <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 md:p-10 opacity-0 animate-fade-in-up border border-gray-100" style={{ overflow: 'visible', minHeight: '400px' }}>
                            {/* 헤더 */}
                            <div className="text-center mb-6 sm:mb-8">
                                <h1 className="text-base sm:text-lg md:text-xl font-semibold tracking-tight mb-4 leading-relaxed" style={{ color: '#0A0A0A', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                                    Improving personalized recommendations
                                </h1>

                                {/* 진행 바 */}
                                <div className="w-full h-1 bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-gray-900 to-gray-700 transition-all duration-300 ease-out rounded-full"
                                        style={{ width: `${progress}%` }}
                                    />
                                </div>
                                <p className="text-xs text-gray-400 mt-2 font-medium">
                                    {step + 1} of {questions.length}
                                </p>
                            </div>

                            {/* 질문 영역 */}
                            <div className="space-y-6 sm:space-y-8">
                                <div className="text-center opacity-0 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                                    <h2 className="text-xl sm:text-2xl md:text-3xl font-medium text-gray-900 whitespace-pre-line leading-relaxed tracking-tight mb-2" style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}>
                                        {current.question}
                                    </h2>
                                </div>

                                {/* 옵션 또는 입력 */}
                                <div className="mt-6 sm:mt-8">
                                    {current.options ? (
                                        current.key === 'nationality' ? (
                                            <div className="max-w-xs mx-auto space-y-3 opacity-0 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                                                <div className="relative" style={{ marginTop: 'auto' }}>
                                                    <select
                                                        value={formData[current.key as keyof typeof formData] || ''}
                                                        onChange={(e) => {
                                                            if (e.target.value) {
                                                                handleOptionSelect(e.target.value);
                                                            }
                                                        }}
                                                        className="w-full px-4 sm:px-5 py-3 sm:py-4 rounded-lg border-2 border-gray-200 bg-white text-gray-700 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 transition-all duration-200 tracking-wide hover:bg-gray-50 hover:border-gray-300 hover:shadow-md appearance-none cursor-pointer"
                                                        style={{
                                                            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                                                            backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E")`,
                                                            backgroundPosition: 'right 0.5rem center',
                                                            backgroundRepeat: 'no-repeat',
                                                            backgroundSize: '1.2em 1.2em',
                                                            paddingRight: '2.5rem'
                                                        }}
                                                    >
                                                        <option value="" disabled>Select your country</option>
                                                        {current.options.map((option) => (
                                                            <option key={option} value={option}>
                                                                {option}
                                                            </option>
                                                        ))}
                                                    </select>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="flex flex-col gap-2 sm:gap-3 items-center">
                                                {current.options.map((option, index) => (
                                                    <button
                                                        key={option}
                                                        onClick={() => handleOptionSelect(option)}
                                                        className={`w-full max-w-xs py-3 sm:py-4 px-4 sm:px-6 rounded-lg text-center font-normal transition-all duration-200 border-2 text-sm sm:text-base tracking-wide transform hover:scale-[1.02] active:scale-[0.98] opacity-0 animate-fade-in-up ${formData[current.key as keyof typeof formData] === option
                                                            ? 'bg-gray-900 text-white shadow-lg border-gray-900 scale-[1.02]'
                                                            : 'bg-white text-gray-700 hover:bg-gray-50 border-gray-200 hover:border-gray-300 hover:shadow-md'
                                                            }`}
                                                        style={{
                                                            fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                                                            animationDelay: `${0.4 + index * 0.1}s`
                                                        }}
                                                    >
                                                        {option}
                                                    </button>
                                                ))}
                                            </div>
                                        )
                                    ) : (
                                        <div className="space-y-3 sm:space-y-4 max-w-xs mx-auto">
                                            {current.type === 'birthday' ? (
                                                <>
                                                    <div className="opacity-0 animate-fade-in-up" style={{ animationDelay: '0.4s', minHeight: '200px' }}>
                                                        <div className="grid grid-cols-3 gap-2 sm:gap-3">
                                                            {/* 연도 */}
                                                            <div className="relative" style={{ overflow: 'visible', minHeight: '180px' }}>
                                                                <select
                                                                    value={formData.birthYear}
                                                                    onChange={(e) => {
                                                                        setFormData({ ...formData, birthYear: e.target.value });
                                                                        if (e.currentTarget) {
                                                                            e.currentTarget.size = 1;
                                                                            e.currentTarget.blur();
                                                                        }
                                                                    }}
                                                                    size={1}
                                                                    className="w-full px-3 sm:px-4 py-3 sm:py-4 rounded-lg border-2 border-gray-200 bg-white text-gray-700 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 transition-all duration-200 hover:bg-gray-50 hover:border-gray-300 hover:shadow-md appearance-none cursor-pointer"
                                                                    style={{
                                                                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                                                                        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E")`,
                                                                        backgroundPosition: 'right 0.4rem center',
                                                                        backgroundRepeat: 'no-repeat',
                                                                        backgroundSize: '1em 1em',
                                                                        paddingRight: '2rem'
                                                                    }}
                                                                    onFocus={(e) => {
                                                                        if (e.currentTarget) {
                                                                            e.currentTarget.size = 6;
                                                                        }
                                                                    }}
                                                                    onBlur={(e) => {
                                                                        const target = e.currentTarget;
                                                                        setTimeout(() => {
                                                                            if (target) {
                                                                                target.size = 1;
                                                                            }
                                                                        }, 150);
                                                                    }}
                                                                >
                                                                    <option value="">YYYY</option>
                                                                    {Array.from({ length: 100 }, (_, i) => {
                                                                        const year = new Date().getFullYear() - i;
                                                                        return (
                                                                            <option key={year} value={year}>
                                                                                {year}
                                                                            </option>
                                                                        );
                                                                    })}
                                                                </select>
                                                            </div>
                                                            {/* 월 */}
                                                            <div className="relative" style={{ overflow: 'visible', minHeight: '180px' }}>
                                                                <select
                                                                    value={formData.birthMonth}
                                                                    onChange={(e) => {
                                                                        setFormData({ ...formData, birthMonth: e.target.value });
                                                                        if (e.currentTarget) {
                                                                            e.currentTarget.size = 1;
                                                                            e.currentTarget.blur();
                                                                        }
                                                                    }}
                                                                    size={1}
                                                                    className="w-full px-3 sm:px-4 py-3 sm:py-4 rounded-lg border-2 border-gray-200 bg-white text-gray-700 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 transition-all duration-200 hover:bg-gray-50 hover:border-gray-300 hover:shadow-md appearance-none cursor-pointer"
                                                                    style={{
                                                                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                                                                        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E")`,
                                                                        backgroundPosition: 'right 0.4rem center',
                                                                        backgroundRepeat: 'no-repeat',
                                                                        backgroundSize: '1em 1em',
                                                                        paddingRight: '2rem'
                                                                    }}
                                                                    onFocus={(e) => {
                                                                        if (e.currentTarget) {
                                                                            e.currentTarget.size = 6;
                                                                        }
                                                                    }}
                                                                    onBlur={(e) => {
                                                                        const target = e.currentTarget;
                                                                        setTimeout(() => {
                                                                            if (target) {
                                                                                target.size = 1;
                                                                            }
                                                                        }, 150);
                                                                    }}
                                                                >
                                                                    <option value="">MM</option>
                                                                    {Array.from({ length: 12 }, (_, i) => {
                                                                        const month = i + 1;
                                                                        return (
                                                                            <option key={month} value={month.toString().padStart(2, '0')}>
                                                                                {month.toString().padStart(2, '0')}
                                                                            </option>
                                                                        );
                                                                    })}
                                                                </select>
                                                            </div>
                                                            {/* 일 */}
                                                            <div className="relative" style={{ overflow: 'visible', minHeight: '180px' }}>
                                                                <select
                                                                    value={formData.birthDay}
                                                                    onChange={(e) => {
                                                                        setFormData({ ...formData, birthDay: e.target.value });
                                                                        if (e.currentTarget) {
                                                                            e.currentTarget.size = 1;
                                                                            e.currentTarget.blur();
                                                                        }
                                                                    }}
                                                                    size={1}
                                                                    className="w-full px-3 sm:px-4 py-3 sm:py-4 rounded-lg border-2 border-gray-200 bg-white text-gray-700 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 transition-all duration-200 hover:bg-gray-50 hover:border-gray-300 hover:shadow-md appearance-none cursor-pointer"
                                                                    style={{
                                                                        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
                                                                        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3E%3Cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3E%3C/svg%3E")`,
                                                                        backgroundPosition: 'right 0.4rem center',
                                                                        backgroundRepeat: 'no-repeat',
                                                                        backgroundSize: '1em 1em',
                                                                        paddingRight: '2rem'
                                                                    }}
                                                                    onFocus={(e) => {
                                                                        if (e.currentTarget) {
                                                                            e.currentTarget.size = 6;
                                                                        }
                                                                    }}
                                                                    onBlur={(e) => {
                                                                        const target = e.currentTarget;
                                                                        setTimeout(() => {
                                                                            if (target) {
                                                                                target.size = 1;
                                                                            }
                                                                        }, 150);
                                                                    }}
                                                                >
                                                                    <option value="">DD</option>
                                                                    {Array.from({ length: 31 }, (_, i) => {
                                                                        const day = i + 1;
                                                                        return (
                                                                            <option key={day} value={day.toString().padStart(2, '0')}>
                                                                                {day.toString().padStart(2, '0')}
                                                                            </option>
                                                                        );
                                                                    })}
                                                                </select>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="opacity-0 animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
                                                        <button
                                                            onClick={() => {
                                                                // 생년월일을 YYYY-MM-DD 형식으로 합쳐서 age 필드에 저장
                                                                if (formData.birthYear && formData.birthMonth && formData.birthDay) {
                                                                    const birthday = `${formData.birthYear}-${formData.birthMonth}-${formData.birthDay}`;
                                                                    setFormData({ ...formData, age: birthday });
                                                                    handleNext();
                                                                }
                                                            }}
                                                            disabled={!formData.birthYear || !formData.birthMonth || !formData.birthDay}
                                                            className="w-full py-3 sm:py-4 px-4 sm:px-6 rounded-lg bg-gray-900 text-white font-normal text-sm sm:text-base shadow-md hover:bg-gray-800 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-900 transition-all duration-200 tracking-wide transform hover:scale-[1.02] active:scale-[0.98]"
                                                            style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}
                                                        >
                                                            Continue →
                                                        </button>
                                                    </div>
                                                </>
                                            ) : (
                                                <>
                                                    <div className="opacity-0 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
                                                        <input
                                                            type="text"
                                                            placeholder={(current as any).placeholder || ''}
                                                            value={formData[current.key as keyof typeof formData]}
                                                            onChange={(e) => {
                                                                handleInput(e.target.value);
                                                            }}
                                                            onKeyDown={(e) => e.key === 'Enter' && formData[current.key as keyof typeof formData] && handleNext()}
                                                            className="w-full px-4 sm:px-5 py-3 sm:py-4 rounded-lg border-2 border-gray-200 bg-white text-gray-700 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-gray-400 transition-all duration-200 tracking-wide hover:bg-gray-50 hover:border-gray-300 hover:shadow-md"
                                                            style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}
                                                            autoFocus
                                                        />
                                                    </div>
                                                    <div className="opacity-0 animate-fade-in-up" style={{ animationDelay: '0.5s' }}>
                                                        <button
                                                            onClick={handleNext}
                                                            disabled={!formData[current.key as keyof typeof formData]}
                                                            className="w-full py-3 sm:py-4 px-4 sm:px-6 rounded-lg bg-gray-900 text-white font-normal text-sm sm:text-base shadow-md hover:bg-gray-800 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-900 transition-all duration-200 tracking-wide transform hover:scale-[1.02] active:scale-[0.98]"
                                                            style={{ fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif' }}
                                                        >
                                                            Continue →
                                                        </button>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}