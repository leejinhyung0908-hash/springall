// @ts-nocheck
import { NextResponse } from 'next/server';

/**
 * 카카오맵 API 키를 안전하게 제공하는 API Route
 * 서버 사이드에서만 키를 관리하고, 클라이언트에 제공
 */
export async function GET() {
    try {
        // 서버 사이드 환경 변수에서 키 가져오기 (NEXT_PUBLIC_ 접두사 없음)
        const KAKAO_MAP_API_KEY = process.env.KAKAO_MAP_API_KEY;

        if (!KAKAO_MAP_API_KEY) {
            return NextResponse.json(
                { error: '카카오맵 API 키가 설정되지 않았습니다.' },
                { status: 500 }
            );
        }

        // API 키만 반환 (다른 정보는 노출하지 않음)
        return NextResponse.json({ apiKey: KAKAO_MAP_API_KEY });
    } catch (error) {
        console.error('카카오맵 API 키 조회 오류:', error);
        return NextResponse.json(
            { error: '서버 오류가 발생했습니다.' },
            { status: 500 }
        );
    }
}

