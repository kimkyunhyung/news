# 뉴스 수집 및 요약 시스템

자동화된 뉴스 수집, 연관성 분석, 요약 및 HTML 생성 시스템입니다.

## 주요 기능

- 네이버 뉴스 API를 통한 뉴스 수집
- LLM을 이용한 키워드 연관성 분석
- 허깅페이스 모델을 이용한 뉴스 요약
- HTML 형태의 결과 생성
- LLM을 이용한 중복 뉴스 제거

## 설치 및 설정

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정
`.env.example` 파일을 `.env`로 복사하고 필요한 값들을 설정하세요:

```bash
cp .env.example .env
```

주요 설정값:
- `X-Naver-Client-Id`: 네이버 개발자센터에서 발급받은 Client ID
- `X-Naver-Client-Secret`: 네이버 개발자센터에서 발급받은 Client Secret
- `LLM_MODEL`: 사용할 LLM 모델 (기본값: llama3.1:8b)

### 3. Ollama 설치 및 모델 다운로드
```bash
# Ollama 설치 후
ollama pull llama3.1:8b
```

## 사용법

### 기본 사용법
```bash
python main.py "빈집"
```

### 고급 사용법
```bash
# 사용자 정의 키워드로 연관성 평가
python main.py "빈집" --keyword "농촌 빈집 문제"

# 중복 제거 건너뛰기
python main.py "빈집" --no-dedup
```

## 프로젝트 구조

- `main.py`: 메인 실행 파일
- `config.py`: 설정 관리 클래스
- `news_processor.py`: 뉴스 처리 통합 클래스
- `lib_news.py`: 뉴스 수집 및 본문 추출
- `lib_llm.py`: LLM 서비스 (연관성 평가, 중복 제거)
- `news_colab.py`: 기존 버전 (하위 호환성 유지)

## 출력 파일

- `result.html`: 수집된 뉴스의 HTML 요약
- `result_nodup.html`: 중복이 제거된 HTML 요약

## 설정 가능한 옵션

환경변수를 통해 다음 값들을 조정할 수 있습니다:

- `DAYS_BACK`: 수집할 뉴스의 기간 (기본값: 7일)
- `NEWS_DISPLAY_COUNT`: 수집할 뉴스 개수 (기본값: 30개)
- `RELEVANCE_THRESHOLD`: 연관성 임계값 (기본값: 50)
- `SUMMARY_MAX_LENGTH`: 요약 최대 길이 (기본값: 128)
- `LOG_LEVEL`: 로그 레벨 (기본값: INFO)

## 이전 버전과의 호환성

기존 코드와의 호환성을 위해 이전 함수들은 래퍼 형태로 유지됩니다:
- `fetch_news()` in `lib_news.py`
- `assess_relevance()` in `lib_llm.py`
- `remove_duplicate_new()` in `lib_llm.py`