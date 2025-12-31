from fastapi import FastAPI, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import uvicorn
from app.bs_demo.bugsmusic import crawl_bugsmusic_chart
from app.sel_demo.danawa import crawl_danawa_mats
from app.bs_demo.aggregate import aggregate_news, analyze_risk, run_all_crawlers
from app.bs_demo.hazard_analyzer import analyze_article

# FastAPI 앱 생성
app = FastAPI(title="Feed Service", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Feed 라우터 생성
feed_router = APIRouter()

@feed_router.get("/")
async def root():
    return {"service": "Feed Service", "status": "running"}

@feed_router.get("/bugsmusic")
async def get_bugsmusic_chart():
    """
    Bugs Music 실시간 차트를 크롤링하여 반환
    """
    try:
        results = crawl_bugsmusic_chart()
        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@feed_router.get("/danawa")
async def get_danawa_mats():
    """
    다나와에서 매트 제품을 크롤링하여 반환
    """
    try:
        results = crawl_danawa_mats()
        return {
            "success": True,
            "data": results,
            "count": len(results)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@feed_router.get("/news")
async def get_aggregate_news(keywords: str = Query(..., description="검색 키워드 (쉼표로 구분)")):
    """
    3개 뉴스 소스(Google, Naver, Daum)를 합쳐서 반환
    예: /news?keywords=시위,폭행,속보
    """
    try:
        # 쉼표로 구분된 키워드를 리스트로 변환
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not keyword_list:
            return {
                "success": False,
                "error": "키워드를 입력해주세요."
            }
        
        results = aggregate_news(keyword_list)
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "keywords": keyword_list
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@feed_router.get("/risk")
async def get_risk_zones(keywords: str = Query(..., description="검색 키워드 (쉼표로 구분)")):
    """
    뉴스 기사를 분석하여 위험 지역을 추출
    예: /risk?keywords=시위,폭행,속보,테러,위험
    """
    try:
        # 쉼표로 구분된 키워드를 리스트로 변환
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not keyword_list:
            return {
                "success": False,
                "error": "키워드를 입력해주세요."
            }
        
        # 뉴스 수집
        articles = aggregate_news(keyword_list)
        
        # 위험 지역 분석
        risk_zones = analyze_risk(articles)
        
        return {
            "success": True,
            "articles_count": len(articles),
            "risk_zones": risk_zones,
            "risk_zones_count": len(risk_zones),
            "keywords": keyword_list
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@feed_router.get("/hazard")
async def get_hazard_analysis(keywords: str = Query(..., description="검색 키워드 (쉼표로 구분)")):
    """
    뉴스 기사를 위험도 점수와 위치 정보를 포함하여 상세 분석
    예: /hazard?keywords=시위,폭행,속보,테러,위험
    """
    try:
        # 쉼표로 구분된 키워드를 리스트로 변환
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        if not keyword_list:
            return {
                "success": False,
                "error": "키워드를 입력해주세요."
            }
        
        # 뉴스 수집
        articles = aggregate_news(keyword_list)
        
        # 각 기사 분석 (위험도 점수, 위치, 위도/경도 포함)
        analyzed_articles = []
        for article in articles:
            # source 정보 추가
            if "naver" in article.get("link", "").lower():
                article["source"] = "naver"
            elif "daum" in article.get("link", "").lower():
                article["source"] = "daum"
            elif "google" in article.get("link", "").lower():
                article["source"] = "google"
            else:
                article["source"] = "unknown"
            
            analyzed = analyze_article(article)
            analyzed_articles.append(analyzed)
        
        # 위험도 점수 순으로 정렬
        analyzed_articles.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
        
        return {
            "success": True,
            "articles_count": len(analyzed_articles),
            "analyzed_articles": analyzed_articles,
            "keywords": keyword_list
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 라우터를 앱에 포함
app.include_router(feed_router)

# 스케줄러 설정
scheduler = BackgroundScheduler()
scheduler.add_job(run_all_crawlers, 'interval', minutes=5, id='crawler_job')
scheduler.start()

# 앱 종료 시 스케줄러 종료
@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9003)

