"""
벡터 저장소 관리 모듈
"""
from langchain_community.vectorstores import Chroma
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from app.embeddings import EmbeddingGenerator
from app.config import VECTOR_DB_TYPE, VECTOR_DB_PATH, COLLECTION_NAME
import logging
import os

logger = logging.getLogger(__name__)

class VectorStore:
    """벡터 저장소 관리 클래스"""
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """벡터 저장소 초기화"""
        try:
            if VECTOR_DB_TYPE == "chroma":
                persist_directory = os.path.join(VECTOR_DB_PATH, "chroma_db")
                os.makedirs(persist_directory, exist_ok=True)
                
                if os.path.exists(persist_directory) and os.listdir(persist_directory):
                    logger.info(f"기존 ChromaDB 로드: {persist_directory}")
                    return Chroma(
                        persist_directory=persist_directory,
                        embedding_function=self.embedding_generator.embeddings,
                        collection_name=COLLECTION_NAME
                    )
                else:
                    logger.info(f"새 ChromaDB 생성: {persist_directory}")
                    return Chroma(
                        persist_directory=persist_directory,
                        embedding_function=self.embedding_generator.embeddings,
                        collection_name=COLLECTION_NAME
                    )
            
            elif VECTOR_DB_TYPE == "faiss":
                faiss_path = os.path.join(VECTOR_DB_PATH, "faiss_index")
                os.makedirs(faiss_path, exist_ok=True)
                
                if os.path.exists(faiss_path) and os.listdir(faiss_path):
                    logger.info(f"기존 FAISS 인덱스 로드: {faiss_path}")
                    return FAISS.load_local(
                        faiss_path,
                        self.embedding_generator.embeddings,
                        allow_dangerous_deserialization=True
                    )
                else:
                    logger.info(f"새 FAISS 인덱스 생성: {faiss_path}")
                    # 빈 FAISS 인덱스 생성 (문서 추가 후 저장)
                    return None
            
            else:
                raise ValueError(f"지원하지 않는 벡터 DB 타입: {VECTOR_DB_TYPE}")
        
        except Exception as e:
            logger.error(f"벡터 저장소 초기화 실패: {e}")
            raise
    
    def add_documents(self, documents: list[Document]):
        """문서를 벡터 저장소에 추가"""
        try:
            if VECTOR_DB_TYPE == "chroma":
                if self.vector_store is None:
                    self.vector_store = Chroma.from_documents(
                        documents=documents,
                        embedding=self.embedding_generator.embeddings,
                        persist_directory=os.path.join(VECTOR_DB_PATH, "chroma_db"),
                        collection_name=COLLECTION_NAME
                    )
                else:
                    self.vector_store.add_documents(documents)
                    self.vector_store.persist()
                logger.info(f"{len(documents)}개 문서 추가 완료 (ChromaDB)")
            
            elif VECTOR_DB_TYPE == "faiss":
                faiss_path = os.path.join(VECTOR_DB_PATH, "faiss_index")
                
                if self.vector_store is None:
                    self.vector_store = FAISS.from_documents(
                        documents=documents,
                        embedding=self.embedding_generator.embeddings
                    )
                else:
                    # 기존 인덱스에 추가
                    temp_store = FAISS.from_documents(
                        documents=documents,
                        embedding=self.embedding_generator.embeddings
                    )
                    self.vector_store.merge_from(temp_store)
                
                self.vector_store.save_local(faiss_path)
                logger.info(f"{len(documents)}개 문서 추가 완료 (FAISS)")
        
        except Exception as e:
            logger.error(f"문서 추가 실패: {e}")
            raise
    
    def search(self, query: str, k: int = 5) -> list[Document]:
        """쿼리와 유사한 문서 검색"""
        try:
            if self.vector_store is None:
                logger.warning("벡터 저장소가 비어있습니다.")
                return []
            
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(f"검색 결과: {len(results)}개 문서 발견")
            return results
        
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []
    
    def search_with_score(self, query: str, k: int = 5) -> list[tuple[Document, float]]:
        """쿼리와 유사한 문서 검색 (유사도 점수 포함)"""
        try:
            if self.vector_store is None:
                logger.warning("벡터 저장소가 비어있습니다.")
                return []
            
            results = self.vector_store.similarity_search_with_score(query, k=k)
            logger.info(f"검색 결과: {len(results)}개 문서 발견")
            return results
        
        except Exception as e:
            logger.error(f"검색 실패: {e}")
            return []

