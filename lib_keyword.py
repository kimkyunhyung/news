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