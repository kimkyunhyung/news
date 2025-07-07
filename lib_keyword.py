import ollama

def assess_relevance(keyword: str, sentence: str) -> int:
    prompt = f"'{keyword}' 와 다음 문장 ' {sentence} ' 간의 연관성을 숫자로 표현하세요.\
        설명과정은 생략하고 결과만 0 에서 100 사이의 **숫자 하나** 만 출력세요. \
        만약 연관성이 없다면 0을 출력하고 연관성이 많다면 100을 출력해 \
        출력 예시 : 75 \
        예시로 보여준 **숫자 하나** 이외 추론과정이나 설명을 보이면 안돼"
    response = ollama.chat(
        model='llama3.1:8b',
        messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    )
    # response['message']['content']의 타입을 점검하고 int로 변환
    try:
        content = int(response['message']['content'])
        return content
    except ValueError:
        print("오류 메시지:", response['message']['content'], "는 정수 값이 아닙니다... SKIP")
        return 0
    
def remove_duplicate_new(news_html) -> str:
    prompt = f"아래는 뉴스 제목과 요약문으로 구성된 뉴스요약 파일(html)입니다. 일부 뉴스는 중복으로 표현되고 있습니다. \
               문서를 전체적으로 확인하고 유사한 내용이 중복된 경우는 해당 뉴스를 삭제하고 뉴스요약 파일(html)을 재구성해줘 \
               문서의 구조는 유지하고 중복된 뉴스의 경우 제목과 요약이 가장 잘 정리된 뉴스 하나만 남겨야 해\
               즉, html의 style 은 변경하지 말고, 원래의 뉴스처럼 link 정보도 가지고 있어야 해.\
                                            \n\n      {news_html}"   
    response = ollama.chat(
        model='llama3.1:8b',
        messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ],
    )
    try:
        content = response['message']['content']
        return content
    except ValueError:
        print("오류 메시지:", response['message']['content'], "중복제거 패는 정수 값이 아닙니다... SKIP")
        return ""                