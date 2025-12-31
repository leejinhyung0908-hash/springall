import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { action, url, tokenLength } = body;

        const timestamp = new Date().toLocaleString('ko-KR');
        console.log('\n' + '='.repeat(60));
        console.log(`[${timestamp}] 🔹 ${action}`);
        console.log(`URL: ${url || 'N/A'}`);
        if (tokenLength) console.log(`Token Length: ${tokenLength}`);
        console.log('='.repeat(60) + '\n');

        return NextResponse.json({ success: true, message: '로그가 기록되었습니다.' });
    } catch (error) {
        console.error('❌ 로그인 로그 기록 실패:', error);
        return NextResponse.json({ success: false, error: '로그 기록 실패' }, { status: 500 });
    }
}

