# 동시성 1개 제한(세마포어)입니다.

import asyncio
from .config import MAX_CONCURRENCY

_semaphore = asyncio.Semaphore(MAX_CONCURRENCY)

def get_semaphore() -> asyncio.Semaphore:
    return _semaphore