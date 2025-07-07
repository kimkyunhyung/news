import logging
import unicodedata
import requests
from datetime import datetime
from newspaper import Article

# 4. 뉴스 API 호출 - Naver가입 및 API key 입력 2025.06
#def fetch_news(query="빈집", user_id, password):
def fetch_news(query, user_id, password, from_date):
    api_url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": user_id,
        "X-Naver-Client-Secret": password
    }
    params = {
        "query": query,
        "sort": "date",
        "display": 30  # 최대 100까지 가능
    }
    try:
        resp = requests.get(api_url, headers=headers, params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])
        filtered = []
        for item in items:
            pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
            if pub_date >= from_date:
                filtered.append(item)
        return filtered
    except requests.exceptions.RequestException as e:
        logging.error(f"뉴스 수집 실패: {e}")
        return []

# 5. 기사 본문 추출
def extract_article_text(url):

    try:
        article = Article(url, language='ko')
        article.download()
        article.parse()
        
        if ("다세대주택 빈집 털이 40대 구속" in article.title) :
            print("URL:  ",  url)
            print("TITLE:  ",  article.title)
            print("TEXT:  ",   article.text)
            print(article)
#5.1 clean_text(text) - 2025.06 - 삭제하고 return article.text로 변경해도 문제 없음
        article.text = unicodedata.normalize("NFKC", article.text)
        article.text = article.text.replace("\x00", "")  # Null 문자 제거
        return article.text.strip()
    except Exception as e:
        logging.warning(f"본문 추출 실패 ({url}): {e}")
        return ""

