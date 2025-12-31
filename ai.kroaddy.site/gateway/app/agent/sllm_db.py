"""
SLLM (Small Language Model) 로컬 DB 모듈
로컬에서 실행되는 경량 LLM 모델 관리
"""
import os
import sqlite3
import json
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SLLMDB:
    """SLLM 로컬 데이터베이스 관리"""
    
    def __init__(self, db_path: str = "./agent/sllm.db"):
        """
        SLLM DB 초기화
        
        Args:
            db_path: SQLite DB 파일 경로
        """
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """DB 디렉토리 생성"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    def _init_database(self):
        """데이터베이스 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 모델 정보 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                model_type TEXT NOT NULL,
                model_path TEXT NOT NULL,
                config TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 대화 기록 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                model_response TEXT NOT NULL,
                model_name TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 모델 캐시 테이블
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt_hash TEXT UNIQUE NOT NULL,
                response TEXT NOT NULL,
                model_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"SLLM DB 초기화 완료: {self.db_path}")
    
    def register_model(
        self,
        name: str,
        model_type: str,
        model_path: str,
        config: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        모델 등록
        
        Args:
            name: 모델 이름
            model_type: 모델 타입 (예: "llama", "mistral", "phi")
            model_path: 모델 파일 경로
            config: 모델 설정 딕셔너리
        
        Returns:
            모델 ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO models (name, model_type, model_path, config, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name,
                model_type,
                model_path,
                json.dumps(config) if config else None,
                datetime.now().isoformat()
            ))
            
            model_id = cursor.lastrowid
            conn.commit()
            logger.info(f"모델 등록 완료: {name} (ID: {model_id})")
            return model_id
        except Exception as e:
            conn.rollback()
            logger.error(f"모델 등록 실패: {e}")
            raise
        finally:
            conn.close()
    
    def get_model(self, name: str) -> Optional[Dict[str, Any]]:
        """모델 정보 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM models WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "model_type": row[2],
                "model_path": row[3],
                "config": json.loads(row[4]) if row[4] else None,
                "created_at": row[5],
                "updated_at": row[6]
            }
        return None
    
    def list_models(self) -> List[Dict[str, Any]]:
        """등록된 모든 모델 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM models ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "model_type": row[2],
                "model_path": row[3],
                "config": json.loads(row[4]) if row[4] else None,
                "created_at": row[5],
                "updated_at": row[6]
            }
            for row in rows
        ]
    
    def save_conversation(
        self,
        session_id: str,
        user_message: str,
        model_response: str,
        model_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """대화 기록 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO conversations (session_id, user_message, model_response, model_name, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                user_message,
                model_response,
                model_name,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            logger.debug(f"대화 기록 저장: session_id={session_id}")
        except Exception as e:
            conn.rollback()
            logger.error(f"대화 기록 저장 실패: {e}")
            raise
        finally:
            conn.close()
    
    def get_conversations(
        self,
        session_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """대화 기록 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute("""
                SELECT * FROM conversations
                WHERE session_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (session_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM conversations
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "session_id": row[1],
                "user_message": row[2],
                "model_response": row[3],
                "model_name": row[4],
                "metadata": json.loads(row[5]) if row[5] else None,
                "created_at": row[6]
            }
            for row in rows
        ]
    
    def cache_response(
        self,
        prompt_hash: str,
        response: str,
        model_name: Optional[str] = None
    ):
        """응답 캐시 저장"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO model_cache (prompt_hash, response, model_name)
                VALUES (?, ?, ?)
            """, (prompt_hash, response, model_name))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"캐시 저장 실패: {e}")
            raise
        finally:
            conn.close()
    
    def get_cached_response(self, prompt_hash: str) -> Optional[str]:
        """캐시된 응답 조회"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT response FROM model_cache WHERE prompt_hash = ?", (prompt_hash,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None

