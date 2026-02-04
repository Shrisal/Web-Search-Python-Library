import unittest
from unittest.mock import patch, Mock
import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mini_search_engine.engine import SearchEngine

class TestMiniSearchEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SearchEngine()

    @patch('mini_search_engine.engine.requests.Session.get')
    def test_search_google_basic(self, mock_get):
        # Mock Google response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
            <div class="g">
                <h3>Google Result</h3>
                <a href="/url?q=http://google.com/res">Link</a>
                <div class="VwiC3b">Snippet</div>
            </div>
        </body></html>
        """
        mock_get.return_value = mock_response

        # Set limit=1 to avoid looping endlessly with the same mock response
        results = self.engine.search("test", engine="google", limit=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], "google")

        # Verify params
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['q'], "test")

    @patch('mini_search_engine.engine.requests.Session.post')
    def test_search_ddg_basic(self, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html><body>
            <div class="result">
                <a class="result__a" href="//duckduckgo.com/l/?uddg=http://ddg.com/res">DDG Result</a>
                <div class="result__snippet">Snippet</div>
            </div>
        </body></html>
        """
        mock_post.return_value = mock_response

        results = self.engine.search("test", engine="ddg")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], "duckduckgo")
        self.assertEqual(results[0]['link'], "http://ddg.com/res")

    @patch('mini_search_engine.engine.requests.Session.get')
    @patch('mini_search_engine.engine.requests.Session.post')
    def test_fallback_logic(self, mock_post, mock_get):
        # Google fails (blocked)
        mock_google = Mock()
        mock_google.status_code = 200
        mock_google.text = "systems have detected unusual traffic"
        mock_get.return_value = mock_google

        # DDG succeeds
        mock_ddg = Mock()
        mock_ddg.status_code = 200
        mock_ddg.text = """
        <html><body>
            <div class="result">
                <a class="result__a" href="http://res.com">Res</a>
            </div>
        </body></html>
        """
        mock_post.return_value = mock_ddg

        # Request 'auto' (defaults to Google -> DDG)
        results = self.engine.search("test", engine="auto")

        self.assertTrue(mock_get.called)
        self.assertTrue(mock_post.called)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['source'], "duckduckgo")

    @patch('mini_search_engine.engine.requests.Session.get')
    def test_google_pagination_and_limit(self, mock_get):
        # Mock 2 pages
        page1 = Mock()
        page1.status_code = 200
        page1.text = """
        <div class="g"><h3>R1</h3><a href="l1">L</a></div>
        <div class="g"><h3>R2</h3><a href="l2">L</a></div>
        """

        page2 = Mock()
        page2.status_code = 200
        page2.text = """
        <div class="g"><h3>R3</h3><a href="l3">L</a></div>
        """

        mock_get.side_effect = [page1, page2]

        # Limit 3 results
        results = self.engine.search("test", engine="google", limit=3)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], "R1")
        self.assertEqual(results[2]['title'], "R3")

        # Verify calls
        self.assertEqual(mock_get.call_count, 2)
        # Check start params
        args1, kwargs1 = mock_get.call_args_list[0]
        self.assertEqual(kwargs1['params']['start'], 0)
        args2, kwargs2 = mock_get.call_args_list[1]
        self.assertEqual(kwargs2['params']['start'], 10)

if __name__ == '__main__':
    unittest.main()
