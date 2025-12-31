// @ts-nocheck
import { NextRequest, NextResponse } from 'next/server';

// 환경 변수에서 API URL 가져오기 (Docker 환경에서 설정됨)
const API_BASE_URL = process.env.API_BASE_URL || 'http://discovery:8080';

export async function GET(request: NextRequest) {
    try {
        const searchParams = request.nextUrl.searchParams;
        const type = searchParams.get('type');
        const keyword = searchParams.get('keyword');

        if (!type || !keyword) {
            return NextResponse.json(
                { error: 'type과 keyword 파라미터가 필요합니다.' },
                { status: 400 }
            );
        }

        // Discovery Gateway를 통해 백엔드 API 호출
        const apiUrl = `${API_BASE_URL}/api/search?type=${type}&keyword=${keyword}`;
        console.log('[Next.js API Route] Calling:', apiUrl);
        console.log('[Next.js API Route] API_BASE_URL:', API_BASE_URL);
        
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        console.log('[Next.js API Route] Response status:', response.status);
        console.log('[Next.js API Route] Response ok:', response.ok);

        if (!response.ok) {
            let errorData;
            try {
                errorData = await response.json();
            } catch {
                errorData = await response.text();
            }
            console.error('[Next.js API Route] Error response:', errorData);
            return NextResponse.json(
                { 
                    error: typeof errorData === 'string' ? errorData : (errorData?.error || 'API 요청 실패'),
                    status: response.status,
                    details: errorData
                },
                { status: response.status }
            );
        }

        const data = await response.json();
        return NextResponse.json(data);
    } catch (error) {
        console.error('API Route Error:', error);
        return NextResponse.json(
            { error: '서버 오류가 발생했습니다.', details: error instanceof Error ? error.message : 'Unknown error' },
            { status: 500 }
        );
    }
}

