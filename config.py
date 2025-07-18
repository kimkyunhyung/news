import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Optional

class Config:
    """공통 설정 관리 클래스"""
    
    def __init__(self):
        load_dotenv()
        self.setup_logging()
        
        # API 설정
        self.naver_client_id = os.getenv("X-Naver-Client-Id")
        self.naver_client_secret = os.getenv("X-Naver-Client-Secret")
        
        # LLM 설정
        self.llm_model = os.getenv("LLM_MODEL", "llama3.1:8b")
        
        # 날짜 설정
        self.today = datetime.now()
        self.days_back = int(os.getenv("DAYS_BACK", "7"))
        self.from_date = self.today - timedelta(days=self.days_back)
        
        # 뉴스 설정
        self.news_display_count = int(os.getenv("NEWS_DISPLAY_COUNT", "30"))
        self.relevance_threshold = int(os.getenv("RELEVANCE_THRESHOLD", "50"))
        
        # 필터링 설정
        self.skip_domains = [
            "n.news",
            "news.ifm.kr", 
            "www.dnews.co.kr"
        ]
        
        # 요약 설정
        self.summary_model = os.getenv("SUMMARY_MODEL", "gogamza/kobart-summarization")
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "2048"))
        self.summary_max_length = int(os.getenv("SUMMARY_MAX_LENGTH", "128"))
        self.summary_min_length = int(os.getenv("SUMMARY_MIN_LENGTH", "30"))
        
        # 출력 파일 설정
        self.output_file = os.getenv("OUTPUT_FILE", "result.html")
        self.output_nodup_file = os.getenv("OUTPUT_NODUP_FILE", "result_nodup.html")
        
    def setup_logging(self):
        """로깅 설정"""
        log_level = os.getenv("LOG_LEVEL", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='[%(levelname)s] %(asctime)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def validate_api_credentials(self) -> bool:
        """API 자격 증명 검증"""
        if not self.naver_client_id or not self.naver_client_secret:
            logging.error("Naver API 자격 증명이 설정되지 않았습니다.")
            return False
        return True
    
    def get_date_range_str(self) -> str:
        """날짜 범위 문자열 반환"""
        return f"{self.from_date.strftime('%Y.%m.%d')}~{self.today.strftime('%Y.%m.%d')}"
