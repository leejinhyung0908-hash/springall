// lib/kakao.ts
export function loadKakaoSDK(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (typeof window === 'undefined') return reject('no window');
      if ((window as any).kakao) return resolve();
  
      const script = document.createElement('script');
      script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${process.env.NEXT_PUBLIC_KAKAO_MAP_API_KEY}&libraries=services,clusterer`;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Kakao SDK load error'));
      document.head.appendChild(script);
    });
  }
  