import logging
import unicodedata
import requests
from datetime import datetime
from newspaper import Article
from typing import List, Dict, Any, Optional
from config import Config

class NewsService:
    """뉴스 수집 및 처리 서비스"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def fetch_news(self, query: str) -> List[Dict[str, Any]]:
        """네이버 뉴스 API를 통해 뉴스 수집"""
        api_url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": self.config.naver_client_id,
            "X-Naver-Client-Secret": self.config.naver_client_secret
        }
        params = {
            "query": query,
            "sort": "date",
            "display": self.config.news_display_count
        }
        
        try:
            resp = requests.get(api_url, headers=headers, params=params)
            resp.raise_for_status()
            items = resp.json().get("items", [])
            
            # 날짜 필터링
            filtered = []
            for item in items:
                try:
                    pub_date = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
                    if pub_date >= self.config.from_date:
                        filtered.append(item)
                except ValueError as e:
                    self.logger.warning(f"날짜 파싱 실패: {item.get('pubDate')} - {e}")
                    continue
            
            self.logger.info(f"총 {len(items)}개 중 {len(filtered)}개 뉴스 수집 완료")
            return filtered
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"뉴스 수집 실패: {e}")
            return []
    
    def extract_article_text(self, url: str) -> str:
        """기사 본문 추출"""
        try:
            article = Article(url, language='ko')
            article.download()
            article.parse()
            
            # 텍스트 정규화
            text = unicodedata.normalize("NFKC", article.text)
            text = text.replace("\x00", "")  # Null 문자 제거
            
            return text.strip()
            
        except Exception as e:
            self.logger.warning(f"본문 추출 실패 ({url}): {e}")
            return ""
    
    def is_valid_link(self, link: str) -> bool:
        """링크 유효성 검사"""
        for skip_domain in self.config.skip_domains:
            if skip_domain in link:
                self.logger.debug(f"링크 스킵: {link} (도메인: {skip_domain})")
                return False
        return True

# 하위 호환성을 위한 함수들
def fetch_news(query: str, user_id: str, password: str, from_date: datetime) -> List[Dict[str, Any]]:
    """하위 호환성을 위한 래퍼 함수"""
    config = Config()
    config.naver_client_id = user_id
    config.naver_client_secret = password
    config.from_date = from_date
    
    service = NewsService(config)
    return service.fetch_news(query)

def extract_article_text(url: str) -> str:
    """하위 호환성을 위한 래퍼 함수"""
    config = Config()
    service = NewsService(config)
    return service.extract_article_text(url)

