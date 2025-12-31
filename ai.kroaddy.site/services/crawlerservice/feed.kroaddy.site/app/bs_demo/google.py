import requests
from bs4 import BeautifulSoup
import json

def crawl_google_news(keywords):
    query = " OR ".join(keywords)
    rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(rss_url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")

    articles = []
    for item in soup.find_all("item"):
        title = item.title.text
        link = item.link.text
        pubDate = item.pubDate.text

        articles.append({
            "title": title,
            "link": link,
            "pubDate": pubDate
        })

    return articles


if __name__ == "__main__":
    keywords = ["시위", "폭행", "속보", "테러", "위험"]
    data = crawl_google_news(keywords)
    print(json.dumps(data, ensure_ascii=False, indent=2))

