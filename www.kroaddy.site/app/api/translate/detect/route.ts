import { NextRequest, NextResponse } from 'next/server';
import { LanguageCode } from '@/lib/types';

/**
 * 언어 감지 API
 * 입력된 텍스트의 언어를 자동으로 감지합니다.
 */

// 언어 코드를 Google Translate 형식으로 변환
function toGoogleTranslateCode(code: LanguageCode): string {
    const codeMap: Record<LanguageCode, string> = {
        'ko': 'ko',
        'en': 'en',
        'ja': 'ja',
        'zh-CN': 'zh-CN',
        'zh-TW': 'zh-TW',
        'fr': 'fr',
        'de': 'de',
        'vi': 'vi',
        'it': 'it',
        'ar': 'ar',
        'id': 'id',
        'th': 'th',
        'mn': 'mn',
        'pt': 'pt',
        'es': 'es',
        'uz': 'uz',
        'km': 'km',
        'ne': 'ne',
    };
    return codeMap[code] || 'en';
}

// Google Translate 언어 코드를 LanguageCode로 변환
function fromGoogleTranslateCode(code: string): LanguageCode {
    const codeMap: Record<string, LanguageCode> = {
        'ko': 'ko',
        'en': 'en',
        'ja': 'ja',
        'zh-CN': 'zh-CN',
        'zh-TW': 'zh-TW',
        'fr': 'fr',
        'de': 'de',
        'vi': 'vi',
        'it': 'it',
        'ar': 'ar',
        'id': 'id',
        'th': 'th',
        'mn': 'mn',
        'pt': 'pt',
        'es': 'es',
        'uz': 'uz',
        'km': 'km',
        'ne': 'ne',
    };
    return codeMap[code] || 'en';
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { text } = body;

        if (!text || typeof text !== 'string') {
            return NextResponse.json(
                { error: 'Missing or invalid text field' },
                { status: 400 }
            );
        }

        // Google Translate 언어 감지 API 사용
        try {
            // 언어 감지 전용 API 사용 (번역 없이 감지만)
            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q=${encodeURIComponent(text)}`;

            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Language detection failed');
            }

            const data = await response.json();
            // Google Translate 응답 구조: [[[번역된텍스트]], 감지된언어코드, 신뢰도, ...]
            // data[2]에 감지된 언어 코드가 있음
            let detectedLang = 'en';

            if (Array.isArray(data) && data.length > 2) {
                detectedLang = data[2] || 'en';
            } else if (Array.isArray(data) && data.length > 0) {
                // 대체 방법: 첫 번째 요소가 문자열인 경우
                detectedLang = typeof data[0] === 'string' ? data[0] : 'en';
            }

            const languageCode = fromGoogleTranslateCode(detectedLang);

            return NextResponse.json({
                detectedLanguage: languageCode,
                confidence: 1.0, // Google Translate는 confidence를 제공하지 않음
            });
        } catch (error) {
            console.error('Language detection error:', error);
            // 기본값으로 영어 반환
            return NextResponse.json({
                detectedLanguage: 'en' as LanguageCode,
                confidence: 0.5,
            });
        }
    } catch (error) {
        console.error('Language detection API error:', error);
        return NextResponse.json(
            { error: 'Language detection failed', message: error instanceof Error ? error.message : 'Unknown error' },
            { status: 500 }
        );
    }
}

