import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote

def crawl_naver_news(keywords):
    """
    네이버 뉴스를 크롤링하여 반환
    """
    query = " OR ".join(keywords)
    # 네이버 뉴스 검색 URL
    url = f"https://search.naver.com/search.naver?where=news&query={quote(query)}&sm=tab_jum&sort=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.naver.com/"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    articles = []
    
    # 네이버 뉴스 검색 결과 찾기
    news_list = soup.find_all("div", class_="news_wrap") or soup.find_all("li", class_="bx")
    
    for item in news_list:
        try:
            # 제목 추출
            title_elem = item.find("a", class_="news_tit") or item.find("a", class_="title") or item.find("a")
            if not title_elem:
                continue
                
            title = title_elem.get_text(strip=True)
            link = title_elem.get("href", "")
            
            # 네이버 뉴스 링크 정규화
            if link and "naver.com" not in link and link.startswith("http"):
                # 외부 링크는 그대로 사용
                pass
            elif link and not link.startswith("http"):
                link = "https://search.naver.com" + link
            
            # 날짜 추출
            date_elem = item.find("span", class_="info") or item.find("span", class_="date") or item.find("span", class_="press")
            pubDate = date_elem.get_text(strip=True) if date_elem else ""
            
            # 언론사 추출
            press_elem = item.find("span", class_="press") or item.find("a", class_="info press")
            press = press_elem.get_text(strip=True) if press_elem else ""
            
            # 요약 추출
            desc_elem = item.find("div", class_="news_dsc") or item.find("p", class_="dsc") or item.find("div", class_="dsc_wrap")
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            if title:
                articles.append({
                    "title": title,
                    "link": link,
                    "pubDate": pubDate,
                    "press": press,
                    "description": description
                })
        except Exception as e:
            continue
    
    return articles


if __name__ == "__main__":
    keywords = ["시위", "폭행", "속보", "테러", "위험"]
    data = crawl_naver_news(keywords)
    print(json.dumps(data, ensure_ascii=False, indent=2))

