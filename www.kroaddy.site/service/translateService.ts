import { LanguageCode, TranslateRequest, TranslateResponse } from '@/lib/types';

/**
 * 언어 코드 매핑 (Sidebar의 언어 목록과 매칭)
 */
export const LANGUAGE_MAP: Record<string, LanguageCode> = {
    '한국어': 'ko',
    'English': 'en',
    '日本語': 'ja',
    '简体中文': 'zh-CN',
    '繁體中文': 'zh-TW',
    'Français': 'fr',
    'Deutsch': 'de',
    'Tiếng Việt': 'vi',
    'Italiano': 'it',
    'العربية': 'ar',
    'Bahasa Indonesia': 'id',
    'ไทย': 'th',
    'монгол': 'mn',
    'Português': 'pt',
    'Español': 'es',
    'oʻzbekcha': 'uz',
    'ខ្មែរ': 'km',
    'नेपाली': 'ne',
};

/**
 * 언어 이름으로 언어 코드 가져오기
 */
export function getLanguageCode(languageName: string): LanguageCode {
    return LANGUAGE_MAP[languageName] || 'en';
}

/**
 * 텍스트의 언어를 자동 감지
 */
export async function detectLanguage(text: string): Promise<LanguageCode> {
    try {
        const response = await fetch('/api/translate/detect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });

        if (!response.ok) {
            throw new Error(`Language detection failed: ${response.statusText}`);
        }

        const data = await response.json();
        return data.detectedLanguage || 'en';
    } catch (error) {
        console.error('Language detection error:', error);
        // 에러 발생 시 기본값 반환
        return 'en';
    }
}

/**
 * 번역 API 호출
 * 
 * 옵션 1: 무료 Google Translate API 사용 (클라이언트 사이드)
 * 옵션 2: Papago API 사용 (네이버, 한국어 번역에 최적화)
 * 옵션 3: 자체 백엔드 API 사용
 */
export async function translateText(
    text: string,
    sourceLang: LanguageCode,
    targetLang: LanguageCode
): Promise<string> {
    // 같은 언어면 번역 불필요
    if (sourceLang === targetLang) {
        return text;
    }

    try {
        const response = await fetch('/api/translate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text,
                sourceLang,
                targetLang,
            } as TranslateRequest),
        });

        if (!response.ok) {
            throw new Error(`Translation failed: ${response.statusText}`);
        }

        const data: TranslateResponse = await response.json();
        return data.translatedText;
    } catch (error) {
        console.error('Translation error:', error);
        // 에러 발생 시 원본 텍스트 반환
        return text;
    }
}

/**
 * 메시지 배열 전체 번역
 */
export async function translateMessages(
    messages: Array<{ content: string }>,
    sourceLang: LanguageCode,
    targetLang: LanguageCode
): Promise<string[]> {
    if (sourceLang === targetLang) {
        return messages.map(m => m.content);
    }

    try {
        // 여러 메시지를 한 번에 번역 (API가 지원하는 경우)
        const texts = messages.map(m => m.content);
        const response = await fetch('/api/translate/batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                texts,
                sourceLang,
                targetLang,
            }),
        });

        if (!response.ok) {
            throw new Error(`Batch translation failed: ${response.statusText}`);
        }

        const data: { translatedTexts: string[] } = await response.json();
        return data.translatedTexts;
    } catch (error) {
        console.error('Batch translation error:', error);
        // 실패 시 개별 번역 시도
        return Promise.all(
            messages.map(m => translateText(m.content, sourceLang, targetLang))
        );
    }
}

