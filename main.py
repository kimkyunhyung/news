#!/usr/bin/env python3
"""
뉴스 수집 및 요약 메인 스크립트
사용법: python news_colab.py [검색어]
"""

import sys
import argparse
from config import Config
from news_processor import NewsProcessor

def main():
    """메인 함수"""
    # 명령행 인수 파싱
    parser = argparse.ArgumentParser(description='뉴스 수집 및 요약')
    parser.add_argument('query', nargs='?', default='빈집', help='검색할 키워드 (기본값: 빈집)')
    parser.add_argument('--keyword', help='연관성 평가에 사용할 키워드 (기본값: 검색어 기반 자동 생성)')
    parser.add_argument('--no-dedup', action='store_true', help='중복 제거 건너뛰기')
    args = parser.parse_args()
    
    try:
        # 설정 및 프로세서 초기화
        config = Config()
        processor = NewsProcessor(config)
        
        print(f"뉴스 수집 시작: '{args.query}'")
        print(f"수집 기간: {config.get_date_range_str()}")
        
        # 뉴스 처리
        html_content = processor.process_news(args.query, args.keyword)
        
        # 결과 저장
        output_file = processor.save_html(html_content)
        if output_file:
            print(f"결과 파일 생성: {output_file}")
            
            # 중복 제거 (옵션)
            if not args.no_dedup:
                dedup_file = processor.remove_duplicates_and_save(html_content)
                if dedup_file:
                    print(f"중복 제거 파일 생성: {dedup_file}")
        
        print("작업 완료!")
        
    except KeyboardInterrupt:
        print("\n작업이 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
