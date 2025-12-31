"""모델 타입 등록 모듈.

애플리케이션 시작 시 호출하여 모델 타입을 등록합니다.
"""
from backend.llm.factory import get_factory
from backend.llm.implementations.midm_llm import MidmLLM


def register_all_models() -> None:
    """모든 모델 타입을 레지스트리에 등록합니다."""
    factory = get_factory()
    
    # Mi:dm 모델 등록
    factory.register("midm", MidmLLM)
    factory.register("local", MidmLLM)  # 기본 로컬 모델로도 사용 가능
    
    print("[ModelRegistry] 모델 타입 등록 완료: midm, local", flush=True)

