import { NextRequest, NextResponse } from 'next/server';
import { TranslateRequest, TranslateResponse, LanguageCode } from '@/lib/types';

/**
 * 번역 API 라우트
 * 
 * 구현 옵션:
 * 1. Google Translate API (무료 버전 - @vitalets/google-translate-api)
 * 2. Papago API (네이버, 한국어 번역에 최적화)
 * 3. DeepL API (고품질 번역)
 * 
 * 현재는 Google Translate 무료 버전을 사용합니다.
 * 환경 변수에 API 키가 있으면 해당 서비스를 사용합니다.
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

// 언어 코드를 Papago 형식으로 변환
function toPapagoCode(code: LanguageCode): string {
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

/**
 * Google Translate 무료 API 사용
 */
async function translateWithGoogle(
    text: string,
    sourceLang: LanguageCode,
    targetLang: LanguageCode
): Promise<string> {
    try {
        // Google Translate 무료 API 사용
        // 실제 구현 시 @vitalets/google-translate-api 라이브러리 사용 권장
        const source = toGoogleTranslateCode(sourceLang);
        const target = toGoogleTranslateCode(targetLang);

        // 간단한 구현 예시 (실제로는 라이브러리 사용)
        const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=${source}&tl=${target}&dt=t&q=${encodeURIComponent(text)}`;

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Translation failed');
        }

        const data = await response.json();
        return data[0]?.[0]?.[0] || text;
    } catch (error) {
        console.error('Google Translate error:', error);
        throw error;
    }
}

/**
 * Papago API 사용 (네이버)
 * 환경 변수 필요: NAVER_CLIENT_ID, NAVER_CLIENT_SECRET
 */
async function translateWithPapago(
    text: string,
    sourceLang: LanguageCode,
    targetLang: LanguageCode
): Promise<string> {
    const clientId = process.env.NAVER_CLIENT_ID;
    const clientSecret = process.env.NAVER_CLIENT_SECRET;

    if (!clientId || !clientSecret) {
        throw new Error('Papago API credentials not configured');
    }

    try {
        const source = toPapagoCode(sourceLang);
        const target = toPapagoCode(targetLang);

        const response = await fetch('https://openapi.naver.com/v1/papago/n2mt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Naver-Client-Id': clientId,
                'X-Naver-Client-Secret': clientSecret,
            },
            body: JSON.stringify({
                source,
                target,
                text,
            }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(`Papago API error: ${error.errorMessage || response.statusText}`);
        }

        const data = await response.json();
        return data.message.result.translatedText;
    } catch (error) {
        console.error('Papago Translate error:', error);
        throw error;
    }
}

export async function POST(request: NextRequest) {
    try {
        const body: TranslateRequest = await request.json();
        const { text, sourceLang, targetLang } = body;

        if (!text || !sourceLang || !targetLang) {
            return NextResponse.json(
                { error: 'Missing required fields: text, sourceLang, targetLang' },
                { status: 400 }
            );
        }

        // 같은 언어면 번역 불필요
        if (sourceLang === targetLang) {
            return NextResponse.json({
                translatedText: text,
                sourceLang,
                targetLang,
            } as TranslateResponse);
        }

        let translatedText: string;

        // Papago API가 설정되어 있으면 우선 사용 (한국어 번역에 최적화)
        if (process.env.NAVER_CLIENT_ID && process.env.NAVER_CLIENT_SECRET) {
            try {
                translatedText = await translateWithPapago(text, sourceLang, targetLang);
            } catch (error) {
                console.warn('Papago translation failed, falling back to Google:', error);
                translatedText = await translateWithGoogle(text, sourceLang, targetLang);
            }
        } else {
            // 기본적으로 Google Translate 사용
            translatedText = await translateWithGoogle(text, sourceLang, targetLang);
        }

        return NextResponse.json({
            translatedText,
            sourceLang,
            targetLang,
        } as TranslateResponse);
    } catch (error) {
        console.error('Translation API error:', error);
        return NextResponse.json(
            { error: 'Translation failed', message: error instanceof Error ? error.message : 'Unknown error' },
            { status: 500 }
        );
    }
}

