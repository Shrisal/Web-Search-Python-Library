import unittest
from unittest.mock import patch, Mock
import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mini_search_engine.engine import SearchEngine

class TestMiniSearchEngine(unittest.TestCase):

    def setUp(self):
        # We will mock the Crawler.crawl method to avoid real network calls
        # and instead return our local test data structure
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

        # Test 1: Search for "Python"
        # Page A and C have "Python".
        # Page B links to A and C. Page C links to A. Page A links to B.
        # Flow: A <-> B -> C -> A.
        # C has incoming from B. A has incoming from B and C.
        # A should probably have highest PageRank? Or close.

        results = engine.search("python")

        self.assertEqual(len(results), 2)
        titles = [r['title'] for r in results]
        self.assertIn("Page A", titles)
        self.assertIn("Page C", titles)
        self.assertNotIn("Page B", titles) # B talks about Java

    @patch('mini_search_engine.crawler.Crawler.crawl')
    def test_pagerank_ranking(self, mock_crawl):
        # A topology where C is the most important
        # A -> C, B -> C. C -> A.
        data = {
            "A": {"title": "A", "content": "keyword", "links": ["C"]},
            "B": {"title": "B", "content": "keyword", "links": ["C"]},
            "C": {"title": "C", "content": "keyword", "links": ["A"]},
        }
        mock_crawl.return_value = data

        engine = SearchEngine()
        engine.build_db(["A"])

        results = engine.search("keyword")

        # C receives votes from A and B. A receives from C. B receives none.
        # C should be highest ranked.
        self.assertEqual(results[0]['title'], "C")
        self.assertEqual(results[1]['title'], "A")
        self.assertEqual(results[2]['title'], "B")

    @patch('mini_search_engine.crawler.Crawler.crawl')
    def test_empty_crawl(self, mock_crawl):
        """Test robust handling of empty crawl results."""
        mock_crawl.return_value = {}

        engine = SearchEngine()
        engine.build_db(["http://test.com"])

        results = engine.search("python")
        self.assertEqual(len(results), 0)

if __name__ == '__main__':
    unittest.main()
