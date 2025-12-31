// components/MarkerTooltip.tsx
import { Location } from "../lib/types";

/**
 * 마커 hover 시 표시할 tooltip HTML 생성
 */
export const createMarkerTooltipContent = (location: Location, imageUrl?: string | null) => {
  const displayImageUrl = imageUrl || location.imageUrl || '/img/logo3.png';

  return `
    <div class="marker-tooltip">
      <div class="marker-tooltip-image-wrapper">
        <div class="marker-tooltip-image">
          <img 
            src="${displayImageUrl}" 
            alt="${location.name}"
            onerror="this.src='/img/logo3.png'"
          />
          <div class="marker-tooltip-image-overlay"></div>
        </div>
        <div class="marker-tooltip-arrow"></div>
      </div>
      <div class="marker-tooltip-content">
        <div class="marker-tooltip-header">
          <div class="marker-tooltip-name">${location.name}</div>
          ${location.category ? `
            <div class="marker-tooltip-category">
              <span class="marker-tooltip-category-badge ${location.category.includes('음식') || location.category.includes('식당') || location.category.includes('레스토랑') || location.category.includes('카페') ? 'marker-tooltip-category-restaurant' : ''}">${location.category}</span>
            </div>
          ` : ''}
        </div>
        <div class="marker-tooltip-address">
          <svg class="marker-tooltip-icon" width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7 7.5C7.55228 7.5 8 7.05228 8 6.5C8 5.94772 7.55228 5.5 7 5.5C6.44772 5.5 6 5.94772 6 6.5C6 7.05228 6.44772 7.5 7 7.5Z" fill="currentColor"/>
            <path fill-rule="evenodd" clip-rule="evenodd" d="M7 0C3.68629 0 1 2.68629 1 6C1 9 7 14 7 14C7 14 13 9 13 6C13 2.68629 10.3137 0 7 0ZM7 8C5.89543 8 5 7.10457 5 6C5 4.89543 5.89543 4 7 4C8.10457 4 9 4.89543 9 6C9 7.10457 8.10457 8 7 8Z" fill="currentColor"/>
          </svg>
          <span class="marker-tooltip-address-text">${location.address || '주소 정보 없음'}</span>
        </div>
      </div>
    </div>
  `;
};

