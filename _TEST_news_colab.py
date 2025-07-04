import unicodedata
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from newspaper import Article
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 읽기

user_id = os.getenv("X-Naver-Client-Id")
password = os.getenv("X-Naver-Client-Secret")

# 1. 날짜 계산
today = datetime.now()
week_ago = today - timedelta(days=7)

# 2. 로깅 설정
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# 3. 요약 모델 로딩 - Copilot 추가수정 2025.06
tokenizer = AutoTokenizer.from_pretrained("gogamza/kobart-summarization")
model = AutoModelForSeq2SeqLM.from_pretrained("gogamza/kobart-summarization")
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# 4. 뉴스 API 호출 - Naver가입 및 API key 입력 2025.06
def fetch_news(query="빈집"):
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
            if pub_date >= week_ago:
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

# 6. 기사 요약 - 파라미터 조정 2025.06
def summarize_text(text):
    if not text or len(text.strip()) < 64 :
        return "요약할 수 있는 내용이 부족합니다."
    try:
        #return summarizer(text[:1000], max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        return summarizer(text[:2048], max_length=128, min_length=30, do_sample=False)[0]['summary_text']
    except Exception as e:
        logging.warning(f"요약 실패: {e}")
        return "요약 실패"

# 7. HTML 생성
def create_post(articles):
    html = f"<html><head><meta charset='utf-8'><title>빈집 뉴스 요약 – {today.strftime('%Y-%m-%d')}</title>\n"
    html += """<style>
        body { font-family: sans-serif; line-height: 1.6; max-width: 700px; margin: auto; padding: 2em; }
        h1 { color: #333; }
        article { margin-bottom: 2em; }
        footer { color: #777; font-size: 0.9em; }
    </style></head><body>"""
    html += f"<h1>📌 빈집 관련 뉴스 요약 ({week_ago.strftime('%Y.%m.%d')}~{today.strftime('%Y.%m.%d')})</h1>\n"

    if not articles:
        html += "<p>지난 1주일간 ‘빈집’ 관련 주요 보도는 아직 없습니다.</p>\n"
    else:
        for art in articles:
            title = art.get('title').replace("<b>", "").replace("</b>", "")
            link = art.get('link')
            print(link)
# 7.1 링크 필터링 - 특이케이스 제외, 경인일보 제외2025.06  
            if "n.news" in link or "news.ifm.kr" in link:
                print(link + "는 모바일용 또는 프록시 링크로 본문이 숨겨져 있습니다(n.new 로 시작 필터링), 또는 news.ifm.kr")
                continue
            summary = "요약 실패"
            body = extract_article_text(link)
            summary = summarize_text(body)

            html += "<article>\n"
            html += f"<h5><a href='{link}' target='_blank'>{title}</a></h5>\n"
            html += f"<p><strong>요약:</strong> {summary}</p>\n"
            html += "</article><hr>\n"

    html += "<footer>자동 생성된 블로그 포스트입니다.</footer>\n"
    html += "</body></html>"
    return html

# 8. 실행
if __name__ == "__main__":
    logging.info("📥 뉴스 수집 중...")
    news_items = fetch_news()
    logging.info(f"📑 수집된 기사 수: {len(news_items)}")
    post_html = create_post(news_items)
    with open("news.html", "w", encoding="utf-8") as f:
        f.write(post_html)
    logging.info("생성 완료")