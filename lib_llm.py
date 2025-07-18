import ollama
import logging
from typing import Optional, Dict, Any

class LLMService:
    """범용 LLM 서비스 클래스"""
    
    def __init__(self, model: str = 'llama3.1:8b'):
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    def _send_request(self, prompt: str) -> str:
        """LLM에 요청을 보내고 응답을 받는 공통 메서드"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                }],
            )
            return response['message']['content']
        except Exception as e:
            self.logger.error(f"LLM 요청 실패: {e}")
            return ""
    
    def assess_relevance(self, keyword: str, sentence: str) -> int:
        """키워드와 문장 간의 연관성을 0-100으로 평가"""
        prompt = f"""'{keyword}'와 다음 문장 '{sentence}' 간의 연관성을 숫자로 표현하세요.
        설명과정은 생략하고 결과만 0에서 100 사이의 **숫자 하나**만 출력하세요.
        만약 연관성이 없다면 0을 출력하고 연관성이 많다면 100을 출력해
        출력 예시: 75
        예시로 보여준 **숫자 하나** 이외 추론과정이나 설명을 보이면 안돼"""
        
        response = self._send_request(prompt)
        try:
            content = int(response.strip())
            return max(0, min(100, content))  # 0-100 범위로 제한
        except ValueError:
            self.logger.warning(f"연관성 평가 실패 - 응답: {response}")
            return 0
    
    def remove_duplicates(self, html_content: str) -> str:
        """HTML 뉴스 내용에서 중복 제거"""
        prompt = f"""{html_content}는 뉴스 제목과 요약문으로 구성된 뉴스요약 파일(html)입니다.
        일부 뉴스는 중복으로 표현되고 있습니다.
        현재의 html 파일 구조를 유지하고 중복된 뉴스들은 한개만 남기고 삭제해서 html 파일 생성해.
        즉, html의 style은 변경하지 말고, 뉴스제목(클릭시 링크로 이동)과 요약으로 구성된 입력한 html과 동일한 구성이어야 해.
        html을 바로 사용할 예정이므로 삭제한 중복 뉴스목록이나 자동으로 생성되었다는 등의 진행 과정설명 등은 표시하지마."""
        
        response = self._send_request(prompt)
        if response:
            return response
        else:
            self.logger.warning("중복 제거 실패")
            return html_content
    
    def generate_text(self, prompt: str) -> str:
        """범용 텍스트 생성 메서드"""
        return self._send_request(prompt)

# 하위 호환성을 위한 함수들
def assess_relevance(keyword: str, sentence: str) -> int:
    """하위 호환성을 위한 래퍼 함수"""
    service = LLMService()
    return service.assess_relevance(keyword, sentence)

def remove_duplicate_new(news_html: str) -> str:
    """하위 호환성을 위한 래퍼 함수"""
    service = LLMService()
    return service.remove_duplicates(news_html)                