"""
임베딩 생성 모듈
"""
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.config import EMBEDDING_MODEL, OPENAI_API_KEY, HUGGINGFACE_API_KEY
import logging

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """임베딩 생성기"""
    
    def __init__(self):
        self.embeddings = self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """임베딩 모델 초기화"""
        try:
            if OPENAI_API_KEY:
                logger.info(f"OpenAI 임베딩 모델 사용: {EMBEDDING_MODEL}")
                return OpenAIEmbeddings(
                    model=EMBEDDING_MODEL,
                    openai_api_key=OPENAI_API_KEY
                )
            else:
                logger.info("HuggingFace 임베딩 모델 사용 (sentence-transformers)")
                return HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
        except Exception as e:
            logger.error(f"임베딩 모델 초기화 실패: {e}")
            raise
    
    def embed_text(self, text: str) -> list:
        """텍스트를 벡터로 변환"""
        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            logger.error(f"임베딩 생성 실패: {e}")
            raise
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """여러 문서를 벡터로 변환"""
        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            logger.error(f"문서 임베딩 생성 실패: {e}")
            raise

