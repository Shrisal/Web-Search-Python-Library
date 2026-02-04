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
    def test_search_google_success(self, mock_get):
        # Mock Google response
        mock_response = Mock()
        mock_response.status_code = 200
        # Minimal HTML that resembles Google structure
        mock_response.text = """
        <html><body>
            <div class="g">
                <h3>Test Result</h3>
                <a href="/url?q=http://example.com&amp;sa=U">Link</a>
                <div class="VwiC3b">Test Snippet</div>
            </div>
        </body></html>
        """
        mock_get.return_value = mock_response

        results = self.engine.search("test")

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Test Result")
        self.assertEqual(results[0]['link'], "http://example.com")
        self.assertEqual(results[0]['snippet'], "Test Snippet")

    @patch('mini_search_engine.engine.requests.Session.get')
    @patch('mini_search_engine.engine.requests.Session.post')
    def test_search_fallback_ddg(self, mock_post, mock_get):
        # mock_post (1st arg) -> bottom decorator (Session.post)
        # mock_get (2nd arg) -> top decorator (Session.get)

        # Mock Google (GET)
        mock_google_response = Mock()
        mock_google_response.status_code = 200
        mock_google_response.text = "systems have detected unusual traffic"
        mock_get.return_value = mock_google_response

        # Mock DDG (POST)
        mock_ddg_response = Mock()
        mock_ddg_response.status_code = 200
        mock_ddg_response.text = """
        <html><body>
            <div class="result">
                <a class="result__a" href="http://ddg.example.com">DDG Result</a>
                <div class="result__snippet">DDG Snippet</div>
            </div>
        </body></html>
        """
        mock_post.return_value = mock_ddg_response

        results = self.engine.search("test")

        # Should use DDG
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "DDG Result")
        self.assertEqual(results[0]['link'], "http://ddg.example.com")

    def test_build_db_deprecated(self):
        # Just ensure it doesn't crash
        self.engine.build_db()

if __name__ == '__main__':
    unittest.main()
