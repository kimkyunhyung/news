import os
import logging
from datetime import datetime, timedelta
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from dotenv import load_dotenv
from lib_news import fetch_news, extract_article_text
from lib_keyword import assess_relevance

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
load_dotenv()

# 1. Load environment variables for Naver News API
user_id = os.getenv("X-Naver-Client-Id")
password = os.getenv("X-Naver-Client-Secret")

# 2. 새로운 날짜 정보를 로드합니다.
today = datetime.now()
from_date = today - timedelta(days=7)

# 3. 요약 모델 로딩 - Copilot 추가수정 2025.
tokenizer = AutoTokenizer.from_pretrained("gogamza/kobart-summarization")
model = AutoModelForSeq2SeqLM.from_pretrained("gogamza/kobart-summarization")
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)

# 6. 기사 요약 - 파라미터 조정 2025.06
def summarize_text(text):
    if not text or len(text.strip()) < 64 :
        return "요약할 수 있는 내용이 부족합니다."
    try:
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
    html += f"<h1>📌 빈집 관련 뉴스 요약 ({from_date.strftime('%Y.%m.%d')}~{today.strftime('%Y.%m.%d')})</h1>\n"

    keyword = "빈집(시골이나 도시에 방치되어 사회적으로 문제가 될 수 있는 빈집, slum, ghetto, vacant house)"

    if not articles:
        html += "<p>지난 1주일간 ‘빈집’ 관련 주요 보도는 아직 없습니다.</p>\n"
    else:
        for art in articles:
            link = art.get('link')
            print(link)

        # 7.1 링크 필터링 - 특이케이스 제외, 경인일보 제외2025.06  
            if "n.news" in link or "news.ifm.kr" in link or "www.dnews.co.kr" in link:
                print(link + ":모바일 또는 프록시링크로 본문이 숨겨져 있음.(n.new로 시작 또는 news.ifm.kr)-SKIP")
                continue
            
            title = art.get('title').replace("<b>", "").replace("</b>", "")

            relevance = assess_relevance(keyword, title)
            if relevance < 50:
                logging.info(f"제목 '{title}' 은(는) 연관성({relevance})이 낮음-SKIP")
                continue

            body = extract_article_text(link)
            summary = summarize_text(body)

            html += "<article>\n"
            html += f"<h5><a href='{link}' target='_blank'>{title}</a></h5>\n"
            html += f"<p><strong>요약:</strong> {summary}</p>\n"
            html += "</article><hr>\n"

    html += "<footer>자동 생성된 블로그 포스트입니다.</footer>\n"
    html += "</body></html>"
    return html

# main.
if __name__ == "__main__":
    logging.info("Data Collecting ...")
    news_items = fetch_news("빈집", user_id, password, from_date)
    logging.info(f"Number of Data : {len(news_items)}")
    post_html = create_post(news_items)
    with open("result.html", "w", encoding="utf-8") as f:
        f.write(post_html)
    logging.info("Finish")