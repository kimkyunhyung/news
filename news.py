import requests
from bs4 import BeautifulSoup

def collect_news():
    # 크롤링할 URL
    url = "https://www.google.com/search?q=대성미생물&tbm=nws"

    # 헤더 설정 (User-Agent)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        # 요청 보내기
        response = requests.get(url, headers=headers)
        
        print(f"요청 성공 여부: {response.status_code == 200}")
        print(f"HTTP status code: {response.status_code}")
        
        if response.status_code == 200:
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 뉴스 목록 추출
            news_list = []
            for article in soup.select('div.BNeawe.iBp4i.AP7Wnd'):
                title = None
                link = None
                
                a_tag = article.find('a')
                if a_tag:
                    link = a_tag.get('href')  # get() 메소드를 사용하여 KeyError를 막습니다.
                
                h3_tag = article.find('h3')
                if h3_tag:
                    title = h3_tag.text.strip()
                
                if title and link:
                    news_list.append({'title': title, 'link': link})
            
            return news_list
        else:
            print(f"요청 실패: HTTP status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"요청 오류: {e}")

def summarize_news(news_list):
    # 요약 텍스트 생성
    summary_text = ""
    for news in news_list:
        summary_text += f"{news['title']}\n{news['link']}\n\n"
        print("news = " , news['title'])
    
    return summary_text

# 뉴스 크롤링 함수를 메인에서 호출하여 실행
if __name__ == "__main__":
    news_list = collect_news()
    summary_text = summarize_news(news_list)
    print(summary_text)