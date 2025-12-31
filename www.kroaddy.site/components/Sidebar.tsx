// @ts-nocheck
"use client";

import React, { useState, useEffect } from 'react';
import { t, getCurrentLanguage } from '../lib/i18n';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Languages, User, HeadphonesIcon, Building2, Compass, MessageSquare, Phone, MapPin, AlertCircle, AlertTriangle, Shield, Building } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';

interface SidebarProps {
  onToggleChatbot?: () => void;
  showChatbot?: boolean;
  onReset?: () => void;
}

export function Sidebar({ onToggleChatbot, showChatbot = true, onReset }: SidebarProps) {
  const router = useRouter();
  const [isLanguageDialogOpen, setIsLanguageDialogOpen] = useState(false);
  const [isEmergencyDialogOpen, setIsEmergencyDialogOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState<string>('한국어'); // 기본 언어
  const [uiLanguage, setUiLanguage] = useState<string>('한국어');

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

  // 컴포넌트 마운트 시 저장된 언어 불러오기
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedLanguage = localStorage.getItem('selectedLanguage');
      
      // 온보딩 데이터에서 국가 확인
      const onboardingData = localStorage.getItem('onboardingData');
      let nationalityBasedLanguage: string | null = null;
      
      if (onboardingData) {
        try {
          const data = JSON.parse(onboardingData);
          if (data.nationality) {
            nationalityBasedLanguage = getLanguageByNationality(data.nationality);
          }
        } catch (e) {
          console.error('Failed to parse onboarding data:', e);
        }
      }
      
      // 사용자가 명시적으로 언어를 선택했는지 확인
      const languageManuallySelected = localStorage.getItem('languageManuallySelected') === 'true';
      
      // 언어 우선순위:
      // 1. 사용자가 명시적으로 선택한 언어 (저장된 언어)
      // 2. 국가 기반 언어 (온보딩에서만 자동 설정)
      // 3. 기본값
      let languageToUse: string;
      
      if (languageManuallySelected && savedLanguage) {
        // 사용자가 명시적으로 언어를 선택한 경우, 저장된 언어를 우선 사용
        languageToUse = savedLanguage;
        setSelectedLanguage(savedLanguage);
      } else if (nationalityBasedLanguage) {
        // 사용자가 언어를 선택하지 않았고, 국가 기반 언어가 있으면 사용
        languageToUse = nationalityBasedLanguage;
        if (savedLanguage !== nationalityBasedLanguage) {
          localStorage.setItem('selectedLanguage', nationalityBasedLanguage);
        }
        setSelectedLanguage(nationalityBasedLanguage);
      } else if (savedLanguage) {
        // 저장된 언어가 있으면 사용
        languageToUse = savedLanguage;
        setSelectedLanguage(savedLanguage);
      } else {
        // 기본값 설정
        languageToUse = '한국어';
        localStorage.setItem('selectedLanguage', '한국어');
        setSelectedLanguage('한국어');
      }
      
      // UI 언어도 업데이트
      const langCode = getCurrentLanguage();
      const languageNameMap: Record<string, string> = {
        'ko': '한국어',
        'en': 'English',
        'ja': '日本語',
        'zh-CN': '简体中文',
        'zh-TW': '繁體中文',
        'fr': 'Français',
        'de': 'Deutsch',
        'vi': 'Tiếng Việt',
        'it': 'Italiano',
        'ar': 'العربية',
        'id': 'Bahasa Indonesia',
        'th': 'ไทย',
        'mn': 'монгол',
        'pt': 'Português',
        'es': 'Español',
        'uz': 'oʻzbekcha',
        'km': 'ខ្មែរ',
        'ne': 'नेपाली',
      };
      setUiLanguage(languageNameMap[langCode] || languageToUse);
    }

    // 언어 변경 이벤트 리스너
    const handleLanguageChange = () => {
      const langCode = getCurrentLanguage();
      const languageNameMap: Record<string, string> = {
        'ko': '한국어',
        'en': 'English',
        'ja': '日本語',
        'zh-CN': '简体中文',
        'zh-TW': '繁體中文',
      };
      setUiLanguage(languageNameMap[langCode] || '한국어');
    };

    window.addEventListener('languageChanged', handleLanguageChange as EventListener);
    return () => {
      window.removeEventListener('languageChanged', handleLanguageChange as EventListener);
    };
  }, []);

  const menuItems = [
    { icon: User, labelKey: 'sidebar.myPage', path: '/mypage' },
    { icon: HeadphonesIcon, labelKey: 'sidebar.support', path: '/support' },
    { icon: Building2, labelKey: 'sidebar.aboutUs', path: '/about' }
  ];

  const languages = [
    { name: '한국어', native: '한국어', country: 'South Korea' },
    { name: 'English', native: 'English', country: 'United States' },
    { name: '日本語', native: '日本語', country: 'Japan' },
    { name: '简体中文', native: '简体中文', country: 'China' },
    { name: '繁體中文', native: '繁體中文', country: 'Taiwan' },
    { name: 'Français', native: 'Français', country: 'France' },
    { name: 'Deutsch', native: 'Deutsch', country: 'Germany' },
    { name: 'Tiếng Việt', native: 'Tiếng Việt', country: 'Vietnam' },
    { name: 'Italiano', native: 'Italiano', country: 'Italy' },
    { name: 'العربية', native: 'العربية', country: 'Saudi Arabia' },
    { name: 'Bahasa Indonesia', native: 'Bahasa Indonesia', country: 'Indonesia' },
    { name: 'ไทย', native: 'ไทย', country: 'Thailand' },
    { name: 'монгол', native: 'монгол', country: 'Mongolia' },
    { name: 'Português', native: 'Português', country: 'Brazil' },
    { name: 'Español', native: 'Español', country: 'Spain' },
    { name: 'oʻzbekcha', native: 'oʻzbekcha', country: 'Uzbekistan' },
    { name: 'ខ្មែរ', native: 'ខ្មែរ', country: 'Cambodia' },
    { name: 'नेपाली', native: 'नेपाली', country: 'Nepal' },
  ];

  return (
    <div className="w-20 bg-white border-r flex flex-col items-center py-6">
      {/* 로고 */}
      <div className="mb-8">
        <button
          onClick={onReset}
          className="flex flex-col items-center hover:opacity-70 transition-opacity cursor-pointer"
        >
          <div className="w-12 h-12 rounded-xl overflow-hidden bg-white flex items-center justify-center mb-1">
            <Image
              src="/img/logo2.png"
              alt="Kroaddy logo"
              width={48}
              height={48}
              className="object-contain"
              priority
            />
          </div>
          <span className="text-[10px] text-gray-700">roaddy</span>
        </button>
      </div>

      {/* 메뉴 아이템 */}
      <div className="flex-1 flex flex-col gap-6">
        {/* 챗봇 토글 버튼 */}
        {onToggleChatbot && (
          <button
            onClick={onToggleChatbot}
            className={`flex flex-col items-center gap-1 hover:opacity-70 transition-opacity ${showChatbot ? 'opacity-100' : 'opacity-50'
              }`}
          >
            <MessageSquare className="w-5 h-5 text-gray-600" />
            <span className="text-[9px] text-gray-600">{t('sidebar.chat', getCurrentLanguage())}</span>
          </button>
        )}

        {menuItems.map((item, index) => (
          <button
            key={index}
            onClick={() => item.path && router.push(item.path)}
            className="flex flex-col items-center gap-1 hover:opacity-70 transition-opacity"
          >
            <item.icon className="w-5 h-5 text-gray-600" />
            <span className="text-[9px] text-gray-600">{t(item.labelKey, getCurrentLanguage())}</span>
          </button>
        ))}

        {/* Languages 버튼 - About Us 바로 아래 */}
        <button
          onClick={() => setIsLanguageDialogOpen(true)}
          className="flex flex-col items-center gap-1 hover:opacity-70 transition-opacity"
        >
          <Languages className="w-5 h-5 text-gray-600" />
          <span className="text-[9px] text-gray-600">{t('sidebar.languages', getCurrentLanguage())}</span>
        </button>
      </div>

      {/* 응급사항 버튼 */}
      <button
        onClick={() => setIsEmergencyDialogOpen(true)}
        className="mt-auto px-3 py-3 bg-red-500 text-white rounded-xl hover:opacity-90 transition-opacity flex flex-col items-center gap-1"
      >
        <AlertTriangle className="w-5 h-5" />
        <span className="text-[9px]">{t('sidebar.emergency', getCurrentLanguage())}</span>
      </button>

      {/* 언어 선택 다이얼로그 */}
      <Dialog open={isLanguageDialogOpen} onOpenChange={setIsLanguageDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{t('sidebar.language.select', getCurrentLanguage())}</DialogTitle>
          </DialogHeader>
          <div className="grid grid-cols-4 gap-3 mt-4">
            {languages.map((lang, index) => (
              <button
                key={index}
                onClick={() => {
                  setSelectedLanguage(lang.name);
                  // 로컬 스토리지에 선택한 언어 저장
                  if (typeof window !== 'undefined') {
                    localStorage.setItem('selectedLanguage', lang.name);
                    // 사용자가 명시적으로 언어를 선택했음을 표시
                    localStorage.setItem('languageManuallySelected', 'true');
                  }
                  setIsLanguageDialogOpen(false);
                  // 언어 변경 이벤트 발생 (부모 컴포넌트에서 감지 가능)
                  window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang.name } }));
                }}
                className={`text-left p-2 rounded transition-colors text-sm ${selectedLanguage === lang.name
                  ? 'bg-blue-100 border-2 border-blue-500'
                  : 'hover:bg-gray-100'
                  }`}
              >
                <div className="font-medium">{lang.native}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {lang.name} ({lang.country})
                </div>
              </button>
            ))}
          </div>
        </DialogContent>
      </Dialog>

      {/* Emergency 다이얼로그 */}
      <Dialog open={isEmergencyDialogOpen} onOpenChange={setIsEmergencyDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>{t('emergency.title', getCurrentLanguage())}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            {/* Emergency Report */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle className="w-5 h-5 text-red-500" />
                <h3 className="font-semibold text-lg">{t('emergency.report', getCurrentLanguage())}</h3>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    window.location.href = 'tel:112';
                    setIsEmergencyDialogOpen(false);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/70 text-white rounded-lg hover:bg-red-600/70 transition-colors"
                >
                  <Phone className="w-4 h-4" />
                  <span>{t('emergency.tel', getCurrentLanguage())}</span>
                </button>
                <button
                  onClick={() => {
                    // 경로 안내 로직 추가 가능
                    setIsEmergencyDialogOpen(false);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-500/70 text-white rounded-lg hover:bg-blue-600/70 transition-colors"
                >
                  <MapPin className="w-4 h-4" />
                  <span>{t('emergency.routeGuidance', getCurrentLanguage())}</span>
                </button>
              </div>
            </div>

            {/* Police */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <Shield className="w-5 h-5 text-blue-500" />
                <h3 className="font-semibold text-lg">{t('emergency.police', getCurrentLanguage())}</h3>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    window.location.href = 'tel:112';
                    setIsEmergencyDialogOpen(false);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/70 text-white rounded-lg hover:bg-red-600/70 transition-colors"
                >
                  <Phone className="w-4 h-4" />
                  <span>{t('emergency.tel', getCurrentLanguage())}</span>
                </button>
                <button
                  onClick={() => {
                    // 경로 안내 로직 추가 가능
                    setIsEmergencyDialogOpen(false);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-500/70 text-white rounded-lg hover:bg-blue-600/70 transition-colors"
                >
                  <MapPin className="w-4 h-4" />
                  <span>{t('emergency.routeGuidance', getCurrentLanguage())}</span>
                </button>
              </div>
            </div>

            {/* Embassy */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <Building className="w-5 h-5 text-green-500" />
                <h3 className="font-semibold text-lg">{t('emergency.embassy', getCurrentLanguage())}</h3>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    // 대사관 전화번호 로직 추가 가능
                    setIsEmergencyDialogOpen(false);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/70 text-white rounded-lg hover:bg-red-600/70 transition-colors"
                >
                  <Phone className="w-4 h-4" />
                  <span>{t('emergency.tel', getCurrentLanguage())}</span>
                </button>
                <button
                  onClick={() => {
                    // 경로 안내 로직 추가 가능
                    setIsEmergencyDialogOpen(false);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-500/70 text-white rounded-lg hover:bg-blue-600/70 transition-colors"
                >
                  <MapPin className="w-4 h-4" />
                  <span>{t('emergency.routeGuidance', getCurrentLanguage())}</span>
                </button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}