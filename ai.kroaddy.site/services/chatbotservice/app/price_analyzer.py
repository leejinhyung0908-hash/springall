"""
가격 분석 챗봇 서비스
OpenAI API를 사용한 친절한 한국어 챗봇
"""
from openai import OpenAI
import os
from typing import List, Dict, Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

# 로깅 설정 (먼저 설정)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 루트 디렉토리의 .env 파일 로드
# 프로젝트 루트까지 상위로 이동하여 .env 파일 찾기
current_dir = Path(__file__).parent
root_dir = current_dir
env_loaded = False
for _ in range(5):  # 최대 5단계까지 상위 디렉토리 탐색
    env_file = root_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"✓ .env 파일 로드 완료: {env_file}")
        env_loaded = True
        break
    parent = root_dir.parent
    if parent == root_dir:  # 더 이상 상위 디렉토리가 없으면 중단
        break
    root_dir = parent

if not env_loaded:
    # .env 파일을 찾지 못한 경우 현재 디렉토리와 상위 디렉토리에서 시도
    load_dotenv()  # 기본적으로 현재 디렉토리와 상위 디렉토리에서 .env 찾기
    logger.info("기본 경로에서 .env 파일 로드 시도")

# 클라이언트 생성 (환경변수에서 키 자동 인식)
# API 키가 없으면 None으로 설정하고, 실제 사용 시에만 에러 발생
_openai_api_key = os.getenv("OPENAI_API_KEY")
if _openai_api_key:
    client = OpenAI(api_key=_openai_api_key)
else:
    client = None
    logger.warning("OPENAI_API_KEY가 설정되지 않았습니다. OpenAI API 기능이 작동하지 않을 수 있습니다.")

class PriceAnalyzerChatbot:
    """가격 분석 챗봇 클래스"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 2000):
        """
        챗봇 초기화
        
        Args:
            model: 사용할 모델 (기본값: gpt-3.5-turbo)
            temperature: 창의성 조절 (0.0 ~ 2.0, 기본값: 0.7)
            max_tokens: 응답 길이 제한 (기본값: 300)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_message = "너는 친절한 한국을 여행 온 외국인 맞춤형 한국어 챗봇이야. 사용자의 질문에 정확하고 도움이 되는 답변을 제공해줘."
        
    def chat(self, user_message: str, conversation_history: Optional[List[Dict[str, str]]] = None, user_profile: Optional[Dict[str, str]] = None, context_info: Optional[Dict] = None) -> str:
        """
        챗봇과 대화
        
        Args:
            user_message: 사용자 메시지
            conversation_history: 대화 이력 (선택사항)
            user_profile: 사용자 프로필 정보 (선택사항)
            context_info: 현재 위치 및 날씨 정보 (선택사항)
        
        Returns:
            챗봇의 응답 메시지
        """
        try:
            # 시스템 메시지 구성 (사용자 프로필, 위치, 날씨 정보 포함)
            system_message = self.system_message
            context_parts = []
            
            # 사용자 프로필 정보 추가
            if user_profile:
                profile_parts = []
                
                if user_profile.get('gender'):
                    profile_parts.append(f"성별: {user_profile['gender']}")
                
                if user_profile.get('age'):
                    profile_parts.append(f"생년월일: {user_profile['age']}")
                
                if user_profile.get('nationality'):
                    profile_parts.append(f"국적/거주지: {user_profile['nationality']}")
                
                if user_profile.get('religion'):
                    profile_parts.append(f"종교: {user_profile['religion']}")
                
                if user_profile.get('dietary'):
                    profile_parts.append(f"식이 제한: {user_profile['dietary']}")
                
                if profile_parts:
                    context_parts.append("사용자 정보:")
                    context_parts.extend(profile_parts)
            
            # 현재 위치 정보 추가
            if context_info and context_info.get('location'):
                location = context_info['location']
                context_parts.append(f"\n현재 위치: 위도 {location.get('lat', 'N/A')}, 경도 {location.get('lng', 'N/A')}")
            
            # 날씨 정보 추가
            if context_info and context_info.get('weather'):
                weather = context_info['weather']
                weather_text = f"현재 날씨: {weather.get('city', '알 수 없음')} 지역, {weather.get('temp', 'N/A')}°C, {weather.get('description', '')}"
                context_parts.append(weather_text)
            
            # 컨텍스트 정보가 있으면 시스템 메시지에 추가
            if context_parts:
                context_text = "\n".join(context_parts)
                system_message = f"{self.system_message}\n\n{context_text}\n\n위 정보들을 종합적으로 고려하여 개인화되고 상황에 맞는 답변을 제공해줘."
            
            # 메시지 구성
            messages = [
                {"role": "system", "content": system_message}
            ]
            
            # 대화 이력이 있으면 추가
            if conversation_history:
                # 대화 이력이 리스트인지 확인하고, 각 메시지의 형식 검증
                if isinstance(conversation_history, list):
                    for msg in conversation_history:
                        if isinstance(msg, dict) and "role" in msg and "content" in msg:
                            # role이 'system'이 아닌 경우만 추가 (system 메시지는 이미 있음)
                            if msg["role"] != "system":
                                messages.append({
                                    "role": msg["role"],
                                    "content": str(msg["content"])
                                })
                        else:
                            logger.warning(f"잘못된 대화 이력 형식: {msg}")
                else:
                    logger.warning(f"대화 이력이 리스트가 아닙니다: {type(conversation_history)}")
            
            logger.info(f"전송할 메시지 개수: {len(messages)}")
            
            # 사용자 메시지 추가
            messages.append({"role": "user", "content": user_message})
            
            # 클라이언트 확인
            if client is None:
                error_msg = "OPENAI_API_KEY가 설정되지 않았습니다. 환경 변수를 확인해주세요."
                logger.error(error_msg)
                return "죄송합니다. OpenAI API 키가 설정되지 않아 응답을 생성할 수 없습니다."
            
            # 챗봇 호출
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # 응답 추출
            bot_response = response.choices[0].message.content
            
            # 응답이 잘렸는지 확인
            if response.choices[0].finish_reason == "length":
                logger.warning(f"응답이 max_tokens({self.max_tokens})로 인해 잘렸습니다.")
                bot_response += "\n\n(응답이 길어서 일부가 잘렸을 수 있습니다.)"
            
            logger.info(f"사용자: {user_message[:100]}...")
            logger.info(f"챗봇 응답 길이: {len(bot_response)} 문자")
            logger.info(f"응답 완료 이유: {response.choices[0].finish_reason}")
            
            return bot_response
            
        except Exception as e:
            error_str = str(e)
            logger.error(f"챗봇 호출 실패: {e}", exc_info=True)
            
            # OpenAI API 키 오류 처리
            if "invalid_api_key" in error_str.lower() or "incorrect api key" in error_str.lower() or "401" in error_str:
                return "죄송합니다. OpenAI API 키 설정에 문제가 있습니다. 관리자에게 문의해주세요."
            
            # Rate limit 오류 처리
            if "rate limit" in error_str.lower() or "429" in error_str:
                return "죄송합니다. 요청이 너무 많습니다. 잠시 후 다시 시도해주세요."
            
            # 기타 오류는 간단한 메시지로
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    
    def analyze_price(self, product_name: str, price: Optional[float] = None, context: Optional[str] = None) -> str:
        """
        가격 분석 요청
        
        Args:
            product_name: 상품명
            price: 가격 (선택사항)
            context: 추가 컨텍스트 (선택사항)
        
        Returns:
            가격 분석 결과
        """
        # 가격 정보가 있으면 포함
        if price:
            message = f"{product_name}의 가격이 {price:,}원인데, 이 가격이 적정한지 분석해줘."
        else:
            message = f"{product_name}의 가격을 분석해줘."
        
        # 추가 컨텍스트가 있으면 포함
        if context:
            message += f"\n추가 정보: {context}"
        
        # 시스템 메시지를 가격 분석 전문가로 변경
        original_system = self.system_message
        self.system_message = "너는 가격 분석 전문가야. 상품의 가격을 시장 가격, 경쟁사 가격, 가성비 등을 고려하여 분석해줘."
        
        try:
            response = self.chat(message)
            return response
        finally:
            # 원래 시스템 메시지로 복원
            self.system_message = original_system


# 전역 챗봇 인스턴스
chatbot = PriceAnalyzerChatbot()


def simple_chat(user_message: str) -> str:
    """
    간단한 챗봇 호출 함수
    
    Args:
        user_message: 사용자 메시지
    
    Returns:
        챗봇 응답
    """
    return chatbot.chat(user_message)


def analyze_price(product_name: str, price: Optional[float] = None, context: Optional[str] = None) -> str:
    """
    가격 분석 함수
    
    Args:
        product_name: 상품명
        price: 가격 (선택사항)
        context: 추가 컨텍스트 (선택사항)
    
    Returns:
        가격 분석 결과
    """
    return chatbot.analyze_price(product_name, price, context)


# 테스트 코드
if __name__ == "__main__":
    # 기본 챗봇 테스트
    print("=== 기본 챗봇 테스트 ===")
    response = simple_chat("안녕, 오늘 날씨 어때?")
    print(f"응답: {response}\n")
    
    # 가격 분석 테스트
    print("=== 가격 분석 테스트 ===")
    analysis = analyze_price("아이폰 15", 1200000, "최신 스마트폰, 애플 제품")
    print(f"분석 결과: {analysis}\n")
    
    # 대화 이력 테스트
    print("=== 대화 이력 테스트 ===")
    history = [
        {"role": "user", "content": "안녕하세요"},
        {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
    ]
    response = chatbot.chat("제 이름은 홍길동이에요", conversation_history=history)
    print(f"응답: {response}")

