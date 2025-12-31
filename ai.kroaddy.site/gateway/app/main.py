"""
Agent Service - LLM API 및 SLLM 관리 전용 서비스
Python Gateway에서 Agent 서비스만 분리하여 독립 실행
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from app.agent.main import agent_router

app = FastAPI(title="Agent Service", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (프로덕션에서는 특정 origin만 허용 권장)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# Agent 라우터만 포함
app.include_router(agent_router)

@app.get("/")
async def root():
    return {
        "service": "Agent Service",
        "status": "running",
        "version": "1.0.0",
        "description": "LLM API 및 SLLM 관리 서비스"
    }

@app.get("/health")
async def health():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "Agent Service"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)

