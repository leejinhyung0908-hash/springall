import requests
from bs4 import BeautifulSoup
import json
import re

def crawl_bugsmusic_chart():
    """
    Bugs Music 실시간 차트를 크롤링하여 title, artist, album 정보를 추출
    """
    url = "https://music.bugs.co.kr/chart/track/realtime/total?wl_ref=M_contents_03_01"
    
    # User-Agent 헤더 추가 (일부 사이트에서 봇 차단 방지)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://music.bugs.co.kr/'
    }
    
    # HTML 가져오기
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # HTTP 에러 체크
    
    # BeautifulSoup으로 HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 결과를 저장할 리스트
    chart_data = []
    
    # 방법 1: CHARTrealtime div 안의 table 찾기
    chart_div = soup.find('div', id='CHARTrealtime')
    if chart_div:
        table = chart_div.find('table', class_=re.compile(r'list.*trackList.*byChart'))
        if table:
            tbody = table.find('tbody')
            rows = tbody.find_all('tr') if tbody else table.find_all('tr')
            
            for row in rows:
                try:
                    # title, artist, album 클래스를 가진 요소 찾기
                    title_elem = row.find(class_=re.compile(r'title'))
                    artist_elem = row.find(class_=re.compile(r'artist'))
                    album_elem = row.find(class_=re.compile(r'album'))
                    
                    # 데이터 추출
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    artist = artist_elem.get_text(strip=True) if artist_elem else ""
                    album = album_elem.get_text(strip=True) if album_elem else ""
                    
                    # 제목에서 불필요한 텍스트 제거 (예: "재생", "담기" 등)
                    if title:
                        title = re.sub(r'\s*재생\s*|\s*담기\s*', '', title)
                    
                    # 데이터가 있는 경우만 추가
                    if title or artist or album:
                        chart_data.append({
                            "title": title,
                            "artist": artist,
                            "album": album
                        })
                except Exception as e:
                    continue
    
    # 방법 2: 다른 선택자로 시도 (데이터가 없을 경우)
    if not chart_data:
        # trackList 클래스를 가진 모든 요소 찾기
        track_lists = soup.find_all(class_=re.compile(r'trackList|track.*list', re.I))
        for track_list in track_lists:
            rows = track_list.find_all('tr')
            for row in rows:
                try:
                    # 다양한 방법으로 제목, 아티스트, 앨범 찾기
                    title_elem = (row.find(class_=re.compile(r'title')) or 
                                 row.find('p', class_=re.compile(r'title')) or
                                 row.find('a', class_=re.compile(r'title')))
                    artist_elem = (row.find(class_=re.compile(r'artist')) or
                                  row.find('p', class_=re.compile(r'artist')) or
                                  row.find('a', class_=re.compile(r'artist')))
                    album_elem = (row.find(class_=re.compile(r'album')) or
                                 row.find('p', class_=re.compile(r'album')) or
                                 row.find('a', class_=re.compile(r'album')))
                    
                    title = title_elem.get_text(strip=True) if title_elem else ""
                    artist = artist_elem.get_text(strip=True) if artist_elem else ""
                    album = album_elem.get_text(strip=True) if album_elem else ""
                    
                    if title or artist or album:
                        chart_data.append({
                            "title": title,
                            "artist": artist,
                            "album": album
                        })
                except:
                    continue
    
    # 방법 3: script 태그에서 JSON 데이터 찾기 (동적 로딩된 데이터)
    if not chart_data:
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('chart' in script.string.lower() or 'track' in script.string.lower()):
                # JSON 데이터 패턴 찾기
                json_match = re.search(r'\{.*"title".*"artist".*\}', script.string, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        if isinstance(data, list):
                            chart_data.extend(data)
                        elif isinstance(data, dict) and 'data' in data:
                            chart_data.extend(data['data'])
                    except:
                        pass
    
    return chart_data

if __name__ == "__main__":
    # 크롤링 실행
    results = crawl_bugsmusic_chart()
    
    # JSON 형태로 터미널에 출력
    print(json.dumps(results, ensure_ascii=False, indent=2))

