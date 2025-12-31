"""
Chatbot Service Configuration
"""
import os

# OpenAI API Key (환경 변수에서 가져오기)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# API 키가 없으면 경고만 출력 (애플리케이션 시작은 허용)
if not OPENAI_API_KEY:
    import warnings
    warnings.warn("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. OpenAI API 기능이 작동하지 않을 수 있습니다.")

