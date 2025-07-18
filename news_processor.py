import logging
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from config import Config
from lib_news import NewsService
from lib_llm import LLMService

class NewsProcessor:
    """뉴스 수집, 분석, 요약, HTML 생성을 통합 처리하는 클래스"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
        # 서비스 초기화
        self.news_service = NewsService(self.config)
        self.llm_service = LLMService(self.config.llm_model)
        
        # 요약 모델 초기화
        self._init_summarizer()
    
    def _init_summarizer(self):
        """요약 모델 초기화"""
        try:
            self.logger.info("요약 모델 로딩 중...")
            tokenizer = AutoTokenizer.from_pretrained(self.config.summary_model)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.config.summary_model)
            self.summarizer = pipeline("summarization", model=model, tokenizer=tokenizer)
            self.logger.info("요약 모델 로딩 완료")
        except Exception as e:
            self.logger.error(f"요약 모델 로딩 실패: {e}")
            self.summarizer = None
    
    def summarize_text(self, text: str) -> str:
        """텍스트 요약"""
        if not text or len(text.strip()) < 64:
            return "요약할 수 있는 내용이 부족합니다."
        
        if not self.summarizer:
            return "요약 모델이 로드되지 않았습니다."
        
        try:
            # 텍스트 길이 제한
            text = text[:self.config.max_text_length]
            result = self.summarizer(
                text, 
                max_length=self.config.summary_max_length,
                min_length=self.config.summary_min_length,
                do_sample=False
            )
            return result[0]['summary_text']
        except Exception as e:
            self.logger.warning(f"요약 실패: {e}")
            return "요약 실패"
    
    def process_news(self, query: str, keyword: str = None) -> str:
        """뉴스 수집부터 HTML 생성까지 전체 프로세스 실행"""
        if not self.config.validate_api_credentials():
            return "<html><body><h1>API 자격 증명 오류</h1></body></html>"
        
        # 기본 키워드 설정
        if not keyword:
            keyword = f"{query}(시골이나 도시에 방치되어 사회적으로 문제가 될 수 있는 {query}, slum, ghetto, vacant house)"
        
        self.logger.info(f"뉴스 수집 시작: {query}")
        
        # 뉴스 수집
        articles = self.news_service.fetch_news(query)
        
        # HTML 생성
        html = self._create_html(articles, query, keyword)
        
        return html
    
    def _create_html(self, articles: List[Dict[str, Any]], query: str, keyword: str) -> str:
        """HTML 생성"""
        html = self._get_html_header(query)
        
        if not articles:
            html += f"<p>지난 {self.config.days_back}일간 '{query}' 관련 주요 보도는 아직 없습니다.</p>\n"
        else:
            html += self._process_articles(articles, keyword)
        
        html += self._get_html_footer()
        return html
    
    def _get_html_header(self, query: str) -> str:
        """HTML 헤더 생성"""
        return f"""<html>
<head>
    <meta charset='utf-8'>
    <title>{query} 뉴스 요약 – {self.config.today.strftime('%Y-%m-%d')}</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; max-width: 700px; margin: auto; padding: 2em; }}
        h1 {{ color: #333; }}
        article {{ margin-bottom: 2em; }}
        footer {{ color: #777; font-size: 0.9em; }}
        .stats {{ background-color: #f5f5f5; padding: 1em; margin: 1em 0; border-radius: 5px; }}
    </style>
</head>
<body>
<h1>📌 {query} 관련 뉴스 요약 ({self.config.get_date_range_str()})</h1>
"""
    
    def _process_articles(self, articles: List[Dict[str, Any]], keyword: str) -> str:
        """기사들을 처리하여 HTML 생성"""
        html = ""
        processed_count = 0
        skipped_count = 0
        
        for art in articles:
            link = art.get('link')
            
            # 링크 유효성 검사
            if not self.news_service.is_valid_link(link):
                skipped_count += 1
                continue
            
            title = art.get('title', '').replace("<b>", "").replace("</b>", "")
            
            # 연관성 평가
            relevance = self.llm_service.assess_relevance(keyword, title)
            if relevance < self.config.relevance_threshold:
                self.logger.info(f"제목 '{title}' 연관성({relevance}) 낮음 - SKIP")
                skipped_count += 1
                continue
            
            # 본문 추출 및 요약
            body = self.news_service.extract_article_text(link)
            if not body:
                skipped_count += 1
                continue
                
            summary = self.summarize_text(body)
            
            # HTML 추가
            html += f"""<article>
<h5><a href='{link}' target='_blank'>{title}</a></h5>
<p><strong>연관성:</strong> {relevance}%</p>
<p><strong>요약:</strong> {summary}</p>
</article>
<hr>
"""
            processed_count += 1
        
        # 통계 정보 추가
        stats_html = f"""<div class='stats'>
<strong>처리 통계:</strong> 전체 {len(articles)}개 기사 중 {processed_count}개 처리, {skipped_count}개 스킵
</div>
"""
        
        return stats_html + html
    
    def _get_html_footer(self) -> str:
        """HTML 푸터 생성"""
        return """<footer>자동 생성된 뉴스 요약입니다.</footer>
</body>
</html>"""
    
    def save_html(self, html_content: str, filename: str = None) -> str:
        """HTML 파일 저장"""
        if not filename:
            filename = self.config.output_file
            
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            self.logger.info(f"HTML 파일 저장 완료: {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"파일 저장 실패: {e}")
            return ""
    
    def remove_duplicates_and_save(self, html_content: str) -> str:
        """중복 제거 후 파일 저장"""
        try:
            self.logger.info("중복 뉴스 제거 중...")
            deduplicated_html = self.llm_service.remove_duplicates(html_content)
            
            if deduplicated_html and deduplicated_html != html_content:
                filename = self.save_html(deduplicated_html, self.config.output_nodup_file)
                self.logger.info(f"중복 제거된 HTML 파일 저장 완료: {filename}")
                return filename
            else:
                self.logger.info("중복 제거할 내용이 없거나 실패")
                return ""
        except Exception as e:
            self.logger.error(f"중복 제거 실패: {e}")
            return ""
