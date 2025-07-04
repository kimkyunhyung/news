import unittest
from news_colab import fetch_news, create_post
class TestNewsColab(unittest.TestCase):
    def test_fetch_news(self):
        news_items = fetch_news()
        self.assertGreater(len(news_items), 0)

    def test_create_post(self):
        post_html = create_post([])
        self.assertIsNotNone(post_html)

def main():
    unittest.main()
if __name__ == '__main__':
    main()