import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote

def crawl_daum_news(keywords):
    """
    다음 뉴스를 크롤링하여 반환
    """
    query = " OR ".join(keywords)
    # 다음 뉴스 검색 URL
    url = f"https://search.daum.net/search?w=news&q={quote(query)}&DA=PGD&spacing=0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.daum.net/"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    
    # 다음 뉴스 검색 결과 찾기
    news_list = soup.find_all("div", class_="wrap_cont")
    if not news_list:
        # 다른 선택자 시도
        news_list = soup.find_all("li", class_="item_news")
    
    for item in news_list:
        try:
            # 제목 추출
            title_elem = item.find("a", class_="f_link_b") or item.find("a", class_="tit_main") or item.find("strong") or item.find("a")
            if not title_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            link = title_elem.get("href", "")
            
            # 상대 경로를 절대 경로로 변환
            if link and link.startswith("/"):
                link = "https://search.daum.net" + link
            
            # 날짜 추출
            date_elem = item.find("span", class_="f_nb") or item.find("span", class_="info_news") or item.find("span", class_="date")
            pubDate = date_elem.get_text(strip=True) if date_elem else ""
            
            # 요약 추출 (선택사항)
            desc_elem = item.find("p", class_="desc") or item.find("div", class_="desc")
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            if title:
                articles.append({
                    "title": title,
                    "link": link,
                    "pubDate": pubDate,
                    "description": description
                })
        except Exception as e:
            continue
    
    return articles


if __name__ == "__main__":
    keywords = ["시위", "폭행", "속보", "테러", "위험"]
    data = crawl_daum_news(keywords)
    print(json.dumps(data, ensure_ascii=False, indent=2))

