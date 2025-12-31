"""
RAG 엔진: 검색 + 생성
"""
from langchain_openai import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from app.vector_store import VectorStore
from app.config import LLM_MODEL, OPENAI_API_KEY, TOP_K_RESULTS, SIMILARITY_THRESHOLD
import logging

logger = logging.getLogger(__name__)

class RAGEngine:
    """RAG 엔진 클래스"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm = self._initialize_llm()
        self.qa_chain = self._create_qa_chain()
    
    def _initialize_llm(self):
        """LLM 초기화"""
        try:
            if OPENAI_API_KEY:
                logger.info(f"OpenAI LLM 사용: {LLM_MODEL}")
                return ChatOpenAI(
                    model_name=LLM_MODEL,
                    temperature=0.7,
                    openai_api_key=OPENAI_API_KEY
                )
            else:
                logger.info("HuggingFace LLM 사용 (기본 모델)")
                # HuggingFace 모델 사용 (예: google/flan-t5-base)
                return HuggingFacePipeline.from_model_id(
                    model_id="google/flan-t5-base",
                    task="text2text-generation",
                    model_kwargs={"temperature": 0.7}
                )
        except Exception as e:
            logger.error(f"LLM 초기화 실패: {e}")
            raise
    
    def _create_qa_chain(self):
        """QA 체인 생성"""
        try:
            prompt_template = """다음 컨텍스트를 사용하여 질문에 답변하세요. 
컨텍스트에 답이 없으면 "답을 찾을 수 없습니다"라고 답변하세요.

컨텍스트: {context}

질문: {question}

답변:"""
            
            PROMPT = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            if self.vector_store.vector_store is None:
                logger.warning("벡터 저장소가 비어있어 QA 체인을 생성할 수 없습니다.")
                return None
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.vector_store.as_retriever(
                    search_kwargs={"k": TOP_K_RESULTS}
                ),
                chain_type_kwargs={"prompt": PROMPT},
                return_source_documents=True
            )
            
            logger.info("QA 체인 생성 완료")
            return qa_chain
        
        except Exception as e:
            logger.error(f"QA 체인 생성 실패: {e}")
            return None
    
    def query(self, question: str) -> dict:
        """질문에 대한 답변 생성"""
        try:
            if self.qa_chain is None:
                return {
                    "answer": "벡터 저장소가 비어있습니다. 먼저 문서를 추가해주세요.",
                    "sources": []
                }
            
            result = self.qa_chain({"query": question})
            
            # 소스 문서 정보 추출
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    sources.append({
                        "content": doc.page_content[:200] + "...",  # 처음 200자만
                        "metadata": doc.metadata
                    })
            
            return {
                "answer": result["result"],
                "sources": sources
            }
        
        except Exception as e:
            logger.error(f"질문 처리 실패: {e}")
            return {
                "answer": f"오류가 발생했습니다: {str(e)}",
                "sources": []
            }
    
    def search_only(self, query: str, k: int = None) -> list[dict]:
        """검색만 수행 (생성 없음)"""
        try:
            if k is None:
                k = TOP_K_RESULTS
            
            results = self.vector_store.search_with_score(query, k=k)
            
            formatted_results = []
            for doc, score in results:
                if score >= SIMILARITY_THRESHOLD:  # 유사도 임계값 필터링
                    formatted_results.append({
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": float(score)
                    })
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []

