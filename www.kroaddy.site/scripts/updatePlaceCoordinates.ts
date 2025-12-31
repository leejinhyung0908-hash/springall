// scripts/updatePlaceCoordinates.ts
// 카카오맵 Places API를 사용하여 keywordPlaces.ts의 좌표를 업데이트하는 스크립트
// 사용법: 브라우저 콘솔에서 실행하거나 개발 환경에서 사용

import { keywordPlaceMap } from '../lib/keywordPlaces';

declare global {
  interface Window {
    kakao: any;
  }
}

// 카카오맵 Places API로 장소 좌표 조회
const getPlaceCoordinates = (placeName: string): Promise<{ lat: number; lng: number; address: string } | null> => {
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
          address: firstResult.road_address_name || firstResult.address_name || ''
        });
      } else {
        console.warn(`장소 "${placeName}" 검색 실패:`, status);
        resolve(null);
      }
    });
  });
};

// 모든 장소의 좌표 업데이트
export const updateAllPlaceCoordinates = async () => {
  const updatedPlaces: any = {};
  
  for (const [keyword, locations] of Object.entries(keywordPlaceMap)) {
    updatedPlaces[keyword] = [];
    
    for (const location of locations) {
      console.log(`검색 중: ${location.name}...`);
      const coords = await getPlaceCoordinates(location.name);
      
      if (coords) {
        updatedPlaces[keyword].push({
          ...location,
          lat: coords.lat,
          lng: coords.lng,
          address: coords.address || location.address
        });
        console.log(`✓ ${location.name}: ${coords.lat}, ${coords.lng}`);
      } else {
        // 검색 실패 시 기존 좌표 유지
        updatedPlaces[keyword].push(location);
        console.log(`✗ ${location.name}: 검색 실패, 기존 좌표 유지`);
      }
      
      // API 호출 제한을 고려한 딜레이
      await new Promise(resolve => setTimeout(resolve, 200));
    }
  }
  
  return updatedPlaces;
};

