"""데이터베이스 서비스."""
from typing import Sequence, Tuple

import psycopg

from backend.services.embedding import simple_embed


def reset_demo_data(conn: psycopg.Connection) -> None:
    """데모용 문서를 초기화한다."""

    docs = [
        "LangChain은 LLM 애플리케이션을 빠르게 만들 수 있게 도와주는 프레임워크입니다.",
        "pgvector는 Postgres에서 벡터 임베딩을 저장하고 유사도 검색을 할 수 있게 해주는 확장입니다.",
        "RAG 시스템은 검색된 문서를 바탕으로 LLM이 더 정확한 답변을 할 수 있도록 도와줍니다.",
        "이 예제는 LangChain, pgvector, RAG, 대화형 모드를 간단히 시연합니다.",
    ]

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE documents")
        for content in docs:
            emb = simple_embed(content)
            cur.execute(
                "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
                (content, emb),
            )


def search_similar(
    conn: psycopg.Connection, query: str, *, top_k: int = 3
) -> Sequence[Tuple[str, float]]:
    """pgvector를 사용해 유사한 문서를 검색한다."""

    query_emb = simple_embed(query)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT content, embedding <-> %s::vector AS distance
            FROM documents
            ORDER BY embedding <-> %s::vector
            LIMIT %s
            """,
            (query_emb, query_emb, top_k),
        )
        rows = cur.fetchall()
    return [(row[0], float(row[1])) for row in rows]

