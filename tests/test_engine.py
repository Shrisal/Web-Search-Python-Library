import unittest
from unittest.mock import patch, Mock
import os
import sys
import time

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mini_search_engine.engine import SearchEngine
from mini_search_engine.crawler import Crawler

class TestMiniSearchEngine(unittest.TestCase):

    def setUp(self):
        self.mock_crawled_data = {
            "http://test.com/a": {
                "title": "Page A",
                "content": "This is page A. It talks about Python.",
                "links": ["http://test.com/b"]
            },
            "http://test.com/b": {
                "title": "Page B",
                "content": "This is page B. It talks about Java.",
                "links": ["http://test.com/a", "http://test.com/c"]
            },
            "http://test.com/c": {
                "title": "Page C",
                "content": "This is page C. It is very authoritative on Python.",
                "links": ["http://test.com/a"]
            }
        }

    @patch('mini_search_engine.crawler.Crawler.crawl')
    def test_search_engine_logic(self, mock_crawl):
        mock_crawl.return_value = self.mock_crawled_data

        engine = SearchEngine()
        engine.build_db(["http://test.com/a"])

        results = engine.search("python")

        self.assertEqual(len(results), 2)
        titles = [r['title'] for r in results]
        self.assertIn("Page A", titles)
        self.assertIn("Page C", titles)
        self.assertNotIn("Page B", titles)

    @patch('mini_search_engine.crawler.Crawler.crawl')
    def test_pagerank_ranking(self, mock_crawl):
        data = {
            "A": {"title": "A", "content": "keyword", "links": ["C"]},
            "B": {"title": "B", "content": "keyword", "links": ["C"]},
            "C": {"title": "C", "content": "keyword", "links": ["A"]},
        }
        mock_crawl.return_value = data

        engine = SearchEngine()
        engine.build_db(["A"])

        results = engine.search("keyword")

        self.assertEqual(results[0]['title'], "C")
        self.assertEqual(results[1]['title'], "A")
        self.assertEqual(results[2]['title'], "B")

    @patch('mini_search_engine.crawler.Crawler.crawl')
    def test_empty_crawl(self, mock_crawl):
        mock_crawl.return_value = {}

        engine = SearchEngine()
        engine.build_db(["http://test.com"])

        results = engine.search("python")
        self.assertEqual(len(results), 0)

    def test_crawler_timeout_logic(self):
        """Test that _should_stop returns True after timeout."""
        # Create crawler with 1 second timeout
        crawler = Crawler(["http://test.com"], timeout=1)
        crawler.start_time = time.time() - 2 # Simulate 2 seconds passed

        self.assertTrue(crawler._should_stop())

        crawler.start_time = time.time() # Reset
        self.assertFalse(crawler._should_stop())

if __name__ == '__main__':
    unittest.main()
