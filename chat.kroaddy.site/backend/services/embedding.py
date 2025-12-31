"""임베딩 서비스."""
from typing import List

from backend.config import settings


def simple_embed(text: str, *, dim: int | None = None) -> List[float]:
    """OpenAI 없이도 동작하는 매우 단순한 해시 기반 임베딩.

    - 단어들을 해싱해서 dim 차원의 벡터에 누적
    - 실서비스용이 아니라, **pgvector 벡터 검색 파이프라인을 데모**하기 위한 용도
    """
    if dim is None:
        dim = settings.EMBED_DIM

    tokens = text.lower().split()
    vec = [0.0] * dim
    for tok in tokens:
        h = hash(tok)
        idx = abs(h) % dim
        vec[idx] += 1.0
    # L2 정규화(0 division 방지)
    norm = sum(v * v for v in vec) ** 0.5 or 1.0
    return [v / norm for v in vec]

