"""헬스 체크 라우터."""
from fastapi import APIRouter
import psycopg

from backend.dependencies import get_global_db_connection
from backend.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """헬스 체크 엔드포인트."""
    db_status = "unknown"
    conn = get_global_db_connection()
    try:
        if conn is None:
            db_status = "disconnected"
        elif conn.closed:
            db_status = "disconnected"
        else:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        print(f"[Health] DB 체크 오류: {e}", flush=True)
        db_status = "error"

    return HealthResponse(status="ok", database=db_status)

