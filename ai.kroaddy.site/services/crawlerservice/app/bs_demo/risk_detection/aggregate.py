from .google import crawl_google_news
from .naver import crawl_naver_news
from .daum import crawl_daum_news
import re

def aggregate_news(keywords):
    """
    3개 뉴스 소스(Google, Naver, Daum)를 합쳐서 반환
    """
    data = []
    try:
        data.extend(crawl_google_news(keywords))
    except Exception as e:
        print(f"Google News 크롤링 오류: {str(e)}")
    
    try:
        data.extend(crawl_naver_news(keywords))
    except Exception as e:
        print(f"Naver News 크롤링 오류: {str(e)}")
    
    try:
        data.extend(crawl_daum_news(keywords))
    except Exception as e:
        print(f"Daum News 크롤링 오류: {str(e)}")
    
    return data

def run_all_crawlers():
    """
    스케줄러에서 실행할 모든 크롤러 함수
    기본 위험 키워드로 뉴스를 수집하고 분석
    """
    default_keywords = ["시위", "폭행", "속보", "테러", "위험", "사고", "범죄"]
    
    try:
        print("스케줄러: 뉴스 크롤링 시작...")
        articles = aggregate_news(default_keywords)
        print(f"스케줄러: {len(articles)}개의 기사를 수집했습니다.")
        
        # 위험 지역 분석
        risk_zones = analyze_risk(articles)
        print(f"스케줄러: {len(risk_zones)}개의 위험 지역을 감지했습니다.")
        
        return {
            "articles_count": len(articles),
            "risk_zones_count": len(risk_zones),
            "risk_zones": risk_zones
        }
    except Exception as e:
        print(f"스케줄러 크롤링 오류: {str(e)}")
        return None

# 한국 주요 도시 및 지역명 리스트
KOREAN_LOCATIONS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "수원", "성남", "고양", "용인", "부천", "안산", "안양", "남양주",
    "화성", "평택", "의정부", "시흥", "김포", "광명", "군포", "오산",
    "구리", "의왕", "하남", "이천", "안성", "포천", "양주", "동두천",
    "과천", "가평", "연천", "여주", "양평", "광주", "춘천", "원주",
    "강릉", "동해", "태백", "속초", "삼척", "홍천", "횡성", "영월",
    "평창", "정선", "철원", "화천", "양구", "인제", "고성", "양양",
    "청주", "충주", "제천", "보은", "옥천", "영동", "증평", "진천",
    "괴산", "음성", "단양", "천안", "공주", "보령", "아산", "서산",
    "논산", "계룡", "당진", "금산", "부여", "서천", "청양", "홍성",
    "예산", "태안", "전주", "군산", "익산", "정읍", "남원", "김제",
    "완주", "진안", "무주", "장수", "임실", "순창", "고창", "부안",
    "목포", "여수", "순천", "나주", "광양", "담양", "곡성", "구례",
    "고흥", "보성", "화순", "장흥", "강진", "해남", "영암", "무안",
    "함평", "영광", "장성", "완도", "진도", "신안", "포항", "경주",
    "김천", "안동", "구미", "영주", "영천", "상주", "문경", "경산",
    "군위", "의성", "청송", "영양", "영덕", "청도", "고령", "성주",
    "칠곡", "예천", "봉화", "울진", "울릉", "창원", "진주", "통영",
    "사천", "김해", "밀양", "거제", "양산", "의령", "함안", "창녕",
    "고성", "남해", "하동", "산청", "함양", "거창", "합천", "제주",
    "서귀포", "강남", "강동", "강북", "강서", "관악", "광진", "구로",
    "금천", "노원", "도봉", "동대문", "동작", "마포", "서대문", "서초",
    "성동", "성북", "송파", "양천", "영등포", "용산", "은평", "종로",
    "중구", "중랑"
]

def extract_location(text):
    """
    텍스트에서 장소를 추출하는 함수 (NLP 기반)
    """
    if not text:
        return "알 수 없음"
    
    found_locations = []
    
    # 주요 도시명 검색
    for location in KOREAN_LOCATIONS:
        # 정확한 단어 매칭 (다른 단어의 일부가 아닌 경우)
        pattern = r'\b' + re.escape(location) + r'\b'
        if re.search(pattern, text):
            found_locations.append(location)
    
    # 중복 제거 및 우선순위 (서울, 부산 등 주요 도시 우선)
    priority_locations = ["서울", "부산", "대구", "인천", "광주", "대전", "울산"]
    for loc in priority_locations:
        if loc in found_locations:
            return loc
    
    # 구/동 단위 추출 (예: 강남구, 홍대입구역 등)
    district_pattern = r'([가-힣]+구|[가-힣]+동|[가-힣]+시|[가-힣]+군|[가-힣]+면|[가-힣]+읍)'
    district_matches = re.findall(district_pattern, text)
    if district_matches:
        return district_matches[0]
    
    # 첫 번째로 찾은 지역 반환
    if found_locations:
        return found_locations[0]
    
    # 특정 패턴 추출 (예: "서울시 강남구", "부산 해운대구" 등)
    location_pattern = r'([가-힣]+(?:시|도|구|군|동|면|읍))'
    matches = re.findall(location_pattern, text)
    if matches:
        return matches[0]
    
    return "알 수 없음"

def analyze_risk(articles):
    """
    뉴스 기사들을 분석하여 위험 지역을 추출
    """
    risk_zones = []
    seen_locations = {}  # 중복 제거를 위한 딕셔너리
    
    for a in articles:
        text = (a.get("title", "") + " " + a.get("description", "")).strip()
        
        if not text:
            continue
        
        location = extract_location(text)
        risk_level = None
        reason = None
        
        # 위험 키워드 분석
        if "시위" in text or "집회" in text or "데모" in text:
            risk_level = "medium"
            reason = "시위/집회 감지"
        elif "폭행" in text or "테러" in text or "폭발" in text or "총격" in text:
            risk_level = "high"
            reason = "폭력 사건"
        elif "사고" in text or "충돌" in text or "화재" in text:
            risk_level = "medium"
            reason = "사고 발생"
        elif "범죄" in text or "강도" in text or "절도" in text:
            risk_level = "medium"
            reason = "범죄 발생"
        elif "위험" in text or "경고" in text or "주의" in text:
            risk_level = "low"
            reason = "위험 경고"
        
        # 위험 레벨이 있는 경우만 추가
        if risk_level:
            # 같은 위치의 위험도를 업데이트 (더 높은 위험도 우선)
            if location in seen_locations:
                existing_risk = seen_locations[location]["risk"]
                risk_order = {"low": 1, "medium": 2, "high": 3}
                if risk_order.get(risk_level, 0) > risk_order.get(existing_risk, 0):
                    seen_locations[location] = {
                        "location": location,
                        "risk": risk_level,
                        "reason": reason,
                        "article_count": seen_locations[location].get("article_count", 0) + 1
                    }
                else:
                    seen_locations[location]["article_count"] = seen_locations[location].get("article_count", 0) + 1
            else:
                seen_locations[location] = {
                    "location": location,
                    "risk": risk_level,
                    "reason": reason,
                    "article_count": 1
                }
    
    # 딕셔너리를 리스트로 변환
    risk_zones = list(seen_locations.values())
    
    # 위험도 순으로 정렬 (high > medium > low)
    risk_order = {"high": 3, "medium": 2, "low": 1}
    risk_zones.sort(key=lambda x: risk_order.get(x["risk"], 0), reverse=True)
    
    return risk_zones

