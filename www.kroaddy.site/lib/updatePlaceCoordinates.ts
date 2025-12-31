// lib/updatePlaceCoordinates.ts
// 카카오맵 Places API를 사용하여 장소의 정확한 좌표를 조회하는 유틸리티
// 이 파일은 개발 시에만 사용하여 좌표를 업데이트하는 용도입니다.

export const updatePlaceCoordinates = async (placeName: string): Promise<{ lat: number; lng: number; address: string } | null> => {
  return new Promise((resolve) => {
    if (!window.kakao?.maps) {
      console.error('Kakao Maps API가 로드되지 않았습니다.');
      resolve(null);
      return;
    }

    const places = new window.kakao.maps.services.Places();
    
    places.keywordSearch(placeName, (data: any, status: any) => {
      if (status === window.kakao.maps.services.Status.OK && data.length > 0) {
        const firstResult = data[0];
        resolve({
          lat: parseFloat(firstResult.y),
          lng: parseFloat(firstResult.x),
          address: firstResult.road_address_name || firstResult.address_name
        });
      } else {
        console.error(`장소 "${placeName}" 검색 실패:`, status);
        resolve(null);
      }
    });
  });
};

