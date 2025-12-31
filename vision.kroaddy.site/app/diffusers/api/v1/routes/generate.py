from fastapi import APIRouter, HTTPException
from api.v1.schemas.generate import GenerateRequest, GenerateResponse
from core.limits import get_semaphore
from services.diffusion.txt2img import generate_txt2img
from services.storage.filesystem import save_image_and_meta
from core.config import (
    DEFAULT_WIDTH, DEFAULT_HEIGHT, DEFAULT_STEPS, DEFAULT_GUIDANCE
)
import traceback
import asyncio

# 동시성 제한(세마포어) 걸고 생성 후 저장합니다.

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    try:
        sem = get_semaphore()
        async with sem:
            # 동기 함수를 별도 스레드에서 실행하여 이벤트 루프 블로킹 방지
            image, meta = await asyncio.to_thread(
                generate_txt2img,
                prompt=req.prompt,
                negative_prompt=req.negative_prompt,
                width=req.width or DEFAULT_WIDTH,
                height=req.height or DEFAULT_HEIGHT,
                steps=req.steps or DEFAULT_STEPS,
                guidance_scale=req.guidance_scale if req.guidance_scale is not None else DEFAULT_GUIDANCE,
                seed=req.seed,
            )
            saved = save_image_and_meta(image, meta)
            return saved
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        print(f"❌ 이미지 생성 오류: {error_msg}")
        print(f"📋 상세 오류:\n{error_trace}")
        raise HTTPException(status_code=500, detail=f"이미지 생성 중 오류가 발생했습니다: {error_msg}")