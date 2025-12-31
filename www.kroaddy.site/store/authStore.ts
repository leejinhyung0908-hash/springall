import { create } from "zustand";

interface AuthState {
  isAuthenticated: boolean;
  setIsAuthenticated: (isAuthenticated: boolean) => void;
  logout: () => void;
}

// 쿠키 기반 인증으로 변경되어 토큰은 더 이상 저장하지 않음
// 인증 상태만 관리 (실제 인증은 백엔드 API로 확인)
export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  setIsAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  logout: () => set({ isAuthenticated: false }),
}));
