import re
from collections import Counter

# 1️⃣ 위험 키워드 설정 (가중치 포함)
RISK_KEYWORDS = {
    "시위": 0.6,
    "폭행": 0.7,
    "범죄": 0.8,
    "속보": 0.4,
    "사고": 0.5,
    "테러": 0.9,
    "폭발": 0.9,
    "총격": 0.9,
    "집회": 0.5,
    "데모": 0.5,
    "충돌": 0.5,
    "화재": 0.6,
    "강도": 0.7,
    "절도": 0.6,
    "위험": 0.3,
    "경고": 0.3,
    "주의": 0.2
}

# 2️⃣ 한국 지명 DB (간단 예시, 실제로는 전체 지명 DB 사용)
LOCATIONS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "수원", "성남", "고양", "용인", "부천", "안산", "안양", "남양주",
    "화성", "평택", "의정부", "시흥", "김포", "광명", "군포", "오산",
    "구리", "의왕", "하남", "이천", "안성", "포천", "양주", "동두천",
    "과천", "가평", "연천", "여주", "양평", "춘천", "원주",
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
    "남해", "하동", "산청", "함양", "거창", "합천", "제주",
    "서귀포", "강남구", "해운대구", "종로구", "마포구", "서초구",
    "송파구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구",
    "금천구", "노원구", "도봉구", "동대문구", "동작구", "서대문구",
    "성동구", "성북구", "양천구", "영등포구", "용산구", "은평구", "중구", "중랑구"
]

# 3️⃣ 위치별 위도/경도 매핑
LOCATION_LATLNG = {
    "서울": (37.5665, 126.9780),
    "부산": (35.1796, 129.0756),
    "대구": (35.8714, 128.6014),
    "인천": (37.4563, 126.7052),
    "광주": (35.1595, 126.8526),
    "대전": (36.3504, 127.3845),
    "울산": (35.5384, 129.3114),
    "세종": (36.4800, 127.2890),
    "강남구": (37.4979, 127.0276),
    "해운대구": (35.1631, 129.1633),
    "종로구": (37.5730, 126.9794),
    "마포구": (37.5663, 126.9019),
    "서초구": (37.4837, 127.0324),
    "송파구": (37.5145, 127.1058),
    "강동구": (37.5301, 127.1238),
    "강북구": (37.6398, 127.0256),
    "강서구": (37.5509, 126.8495),
    "관악구": (37.4784, 126.9516),
    "광진구": (37.5385, 127.0826),
    "구로구": (37.4954, 126.8874),
    "금천구": (37.4519, 126.9020),
    "노원구": (37.6542, 127.0568),
    "도봉구": (37.6688, 127.0471),
    "동대문구": (37.5744, 127.0396),
    "동작구": (37.5124, 126.9393),
    "서대문구": (37.5791, 126.9368),
    "성동구": (37.5633, 127.0366),
    "성북구": (37.5894, 127.0167),
    "양천구": (37.5170, 126.8663),
    "영등포구": (37.5264, 126.8962),
    "용산구": (37.5326, 126.9907),
    "은평구": (37.6027, 126.9291),
    "중구": (37.5640, 126.9979),
    "중랑구": (37.6064, 127.0926)
}

# 3️⃣ 위험도 계산 함수
def calculate_risk_score(article_text):
    """
    기사 텍스트에서 위험도 점수를 계산
    """
    if not article_text:
        return 0.0, []
    
    score = 0.0
    detected_keywords = []
    
    for keyword, weight in RISK_KEYWORDS.items():
        if keyword in article_text:
            score += weight
            detected_keywords.append(keyword)
    
    # 키워드 겹치면 보정 (최대 1.0)
    score = min(score, 1.0)
    
    return score, detected_keywords

# 4️⃣ 위치 추출 함수 (지명 매칭 기반)
def extract_location(article_text):
    """
    기사 텍스트에서 위치를 추출
    """
    if not article_text:
        return None
    
    detected_locations = []
    
    # 구체적인 위치부터 검색 (구 단위)
    for loc in sorted(LOCATIONS, key=len, reverse=True):
        # 정확한 단어 매칭
        pattern = r'\b' + re.escape(loc) + r'\b'
        if re.search(pattern, article_text):
            detected_locations.append(loc)
    
    # 가장 구체적/마지막 위치 우선
    if detected_locations:
        # 구 단위가 있으면 우선
        for loc in detected_locations:
            if "구" in loc:
                return loc
        return detected_locations[-1]
    
    return None

# 5️⃣ 전체 분석 함수
def analyze_article(article):
    """
    article: dict with keys 'title', 'content' (or 'description'), 'link', 'pub_date' (or 'pubDate'), 'source'
    """
    title = article.get("title", "")
    content = article.get("content", "") or article.get("description", "")
    text = (title + " " + content).strip()
    
    # 위험도 계산
    risk_score, keywords = calculate_risk_score(text)
    
    # 위치 추출
    location = extract_location(text)
    
    # 위도/경도 매핑
    lat, lng = None, None
    if location:
        lat, lng = LOCATION_LATLNG.get(location, (None, None))
    
    return {
        "title": title,
        "link": article.get("link", ""),
        "pub_date": article.get("pub_date") or article.get("pubDate", ""),
        "risk_score": round(risk_score, 2),
        "location": location,
        "lat": lat,
        "lng": lng,
        "source": article.get("source", ""),
        "keywords": keywords
    }

# 6️⃣ 테스트용 예시
if __name__ == "__main__":
    sample_article = {
        "title": "서울 강남구에서 외국인 대상 폭행 사건 발생",
        "content": "오늘 오후 3시 강남구에서 외국인 대상 폭행 사건이 발생했습니다. 경찰 조사 중...",
        "link": "https://news.example.com/article/123",
        "pub_date": "2025-11-27 18:00",
        "source": "naver"
    }
    
    result = analyze_article(sample_article)
    print(result)

