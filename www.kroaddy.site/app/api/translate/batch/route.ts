import { NextRequest, NextResponse } from 'next/server';
import { LanguageCode } from '@/lib/types';

interface BatchTranslateRequest {
    texts: string[];
    sourceLang: LanguageCode;
    targetLang: LanguageCode;
}

interface BatchTranslateResponse {
    translatedTexts: string[];
}

/**
 * 여러 텍스트를 한 번에 번역하는 배치 API
 */
export async function POST(request: NextRequest) {
    try {
        const body: BatchTranslateRequest = await request.json();
        const { texts, sourceLang, targetLang } = body;

        if (!texts || !Array.isArray(texts) || texts.length === 0) {
            return NextResponse.json(
                { error: 'Missing or invalid texts array' },
                { status: 400 }
            );
        }

        if (!sourceLang || !targetLang) {
            return NextResponse.json(
                { error: 'Missing required fields: sourceLang, targetLang' },
                { status: 400 }
            );
        }

        // 같은 언어면 번역 불필요
        if (sourceLang === targetLang) {
            return NextResponse.json({
                translatedTexts: texts,
            } as BatchTranslateResponse);
        }

        // 개별 번역 API를 여러 번 호출
        // (실제 구현 시 배치 API를 지원하는 서비스 사용 권장)
        const translatedTexts = await Promise.all(
            texts.map(async (text) => {
                try {
                    const response = await fetch(`${request.nextUrl.origin}/api/translate`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            text,
                            sourceLang,
                            targetLang,
                        }),
                    });

                    if (!response.ok) {
                        throw new Error(`Translation failed for text: ${text}`);
                    }

                    const data = await response.json();
                    return data.translatedText;
                } catch (error) {
                    console.error(`Error translating text: ${text}`, error);
                    return text; // 에러 시 원본 반환
                }
            })
        );

        return NextResponse.json({
            translatedTexts,
        } as BatchTranslateResponse);
    } catch (error) {
        console.error('Batch translation API error:', error);
        return NextResponse.json(
            { error: 'Batch translation failed', message: error instanceof Error ? error.message : 'Unknown error' },
            { status: 500 }
        );
    }
}

