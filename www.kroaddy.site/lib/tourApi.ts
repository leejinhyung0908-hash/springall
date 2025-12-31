const SERVICE_KEY = process.env.NEXT_PUBLIC_TOUR_API_ENCODDING_KEY;
const BASE_URL = 'https://apis.data.go.kr/B551011/KorService2';

// 장소명 → contentId 조회
export async function searchContentId(keyword: string) {
    try {
        const url =
            `${BASE_URL}/searchKeyword2` +
            `?serviceKey=${SERVICE_KEY}` +
            `&MobileOS=ETC&MobileApp=TestApp` +
            `&keyword=${encodeURIComponent(keyword)}` +
            `&_type=json`;

        const res = await fetch(url);

        // 429 에러 처리 (Too Many Requests)
        if (res.status === 429) {
            console.warn('Tour API 호출 한도 초과. 잠시 후 다시 시도해주세요.');
            return null;
        }

        // 응답이 JSON인지 확인
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.warn('Tour API 응답이 JSON 형식이 아닙니다.');
            return null;
        }

        const data = await res.json();

        // 에러 응답 확인
        if (data.response?.header?.resultCode !== '0000') {
            const resultMsg = data.response?.header?.resultMsg || '알 수 없는 오류';
            console.warn(`Tour API 오류: ${resultMsg}`);
            return null;
        }

        if (!data.response?.body?.items?.item) return null;

        const item = data.response.body.items.item[0];
        return item.contentid;
    } catch (error) {
        // JSON 파싱 에러 등 처리
        if (error instanceof SyntaxError) {
            console.warn('Tour API 응답 파싱 실패. API 호출 한도 초과일 수 있습니다.');
        } else {
            console.error('Tour API 호출 실패:', error);
        }
        return null;
    }
}

// contentId → 이미지 조회
export async function fetchTourImages(contentId: string) {
    try {
        // subImageYN 제거 → INVALID_REQUEST_PARAMETER_ERROR 해결
        const url =
            `${BASE_URL}/detailImage2` +
            `?serviceKey=${SERVICE_KEY}` +
            `&MobileOS=ETC&MobileApp=TestApp` +
            `&contentId=${contentId}` +
            `&imageYN=Y` +
            `&_type=json`;

        const res = await fetch(url);

        // 429 에러 처리 (Too Many Requests)
        if (res.status === 429) {
            console.warn('Tour API 호출 한도 초과. 잠시 후 다시 시도해주세요.');
            return [];
        }

        // 응답이 JSON인지 확인
        const contentType = res.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.warn('Tour API 응답이 JSON 형식이 아닙니다.');
            return [];
        }

        const data = await res.json();

        // 에러 응답 확인
        if (data.response?.header?.resultCode !== '0000') {
            const resultMsg = data.response?.header?.resultMsg || '알 수 없는 오류';
            console.warn(`Tour API 오류: ${resultMsg}`);
            return [];
        }

        if (!data.response?.body?.items?.item) return [];

        const items = data.response.body.items.item;

        // originimgurl 또는 firstimage2 fallback
        return items.map((img: any) => img.originimgurl || img.smallimageurl || '');
    } catch (error) {
        // JSON 파싱 에러 등 처리
        if (error instanceof SyntaxError) {
            console.warn('Tour API 응답 파싱 실패. API 호출 한도 초과일 수 있습니다.');
        } else {
            console.error('Tour API 호출 실패:', error);
        }
        return [];
    }
}
