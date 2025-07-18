#!/usr/bin/env python3
"""
리팩토링된 코드의 간단한 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from lib_llm import LLMService
from lib_news import NewsService

def test_config():
    """설정 클래스 테스트"""
    print("=== Config 테스트 ===")
    config = Config()
    print(f"LLM 모델: {config.llm_model}")
    print(f"날짜 범위: {config.get_date_range_str()}")
    print(f"연관성 임계값: {config.relevance_threshold}")
    print()

def test_llm_service():
    """LLM 서비스 테스트"""
    print("=== LLM Service 테스트 ===")
    try:
        llm = LLMService()
        
        # 연관성 평가 테스트
        relevance = llm.assess_relevance("빈집", "농촌 지역의 빈집 문제가 심각하다")
        print(f"연관성 평가 결과: {relevance}")
        
        # 텍스트 생성 테스트
        response = llm.generate_text("안녕하세요를 영어로 번역해주세요.")
        print(f"텍스트 생성 결과: {response[:50]}...")
        
    except Exception as e:
        print(f"LLM 서비스 테스트 실패: {e}")
    print()

def test_news_service():
    """뉴스 서비스 테스트"""
    print("=== News Service 테스트 ===")
    try:
        config = Config()
        if not config.validate_api_credentials():
            print("API 자격 증명이 설정되지 않아 뉴스 서비스 테스트를 건너뜁니다.")
            return
            
        news_service = NewsService(config)
        
        # 링크 유효성 테스트
        valid_link = news_service.is_valid_link("https://news.naver.com/test")
        invalid_link = news_service.is_valid_link("https://n.news.naver.com/test")
        
        print(f"유효한 링크 테스트: {valid_link}")
        print(f"무효한 링크 테스트: {invalid_link}")
        
    except Exception as e:
        print(f"뉴스 서비스 테스트 실패: {e}")
    print()

def main():
    """메인 테스트 함수"""
    print("리팩토링된 뉴스 시스템 테스트를 시작합니다...\n")
    
    test_config()
    test_llm_service()
    test_news_service()
    
    print("테스트 완료!")

if __name__ == "__main__":
    main()
