import ollama

def assess_relevance(keyword: str, sentence: str) -> str:
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
    return response['message']['content']
keyword = " 미래에 문제가 될수 있는 빈집(vacant house) "
sentence = "빈집 방치하는 경우 발생하는 일들"
relevance = assess_relevance(keyword, sentence)
print(f"Relevance between '{keyword}' and '{sentence}': {relevance}")

sentence = "도둑들이 빈집을 털었다" 
relevance = assess_relevance(keyword, sentence)
print(f"Relevance between '{keyword}' and '{sentence}': {relevance}")

sentence = "2루 베이스는 빈집과 같은 상태여서 쉽게 도루할 수 있었다."
relevance = assess_relevance(keyword, sentence)
print(f"Relevance between '{keyword}' and '{sentence}': {relevance}")

