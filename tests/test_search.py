import unittest
from unittest.mock import patch, Mock
import os
import sys

# Add the parent directory to the path so we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_lib.search import google_search, _parse_results

class TestGoogleSearch(unittest.TestCase):

    def setUp(self):
        # Read the mock HTML data
        with open(os.path.join(os.path.dirname(__file__), 'mock_data.html'), 'r') as f:
            self.mock_html = f.read()

    def test_parsing_logic(self):
        """Test that the internal parser correctly extracts data from HTML."""
        results = _parse_results(self.mock_html)

        self.assertEqual(len(results), 3)

        # Check first result (Standard)
        self.assertEqual(results[0]['title'], "Welcome to Python.org")
        self.assertEqual(results[0]['link'], "https://www.python.org/")
        self.assertIn("official home of the Python", results[0]['snippet'])

        # Check second result (No snippet)
        self.assertEqual(results[1]['title'], "Python (programming language) - Wikipedia")
        self.assertEqual(results[1]['link'], "https://en.wikipedia.org/wiki/Python_(programming_language)")
        self.assertEqual(results[1]['snippet'], "")

        # Check third result (Alternative snippet class)
        self.assertEqual(results[2]['title'], "Python Tutorial - W3Schools")
        self.assertEqual(results[2]['link'], "https://www.w3schools.com/python/")
        self.assertIn("popular programming language", results[2]['snippet'])

    @patch('google_search_lib.search.requests.Session')
    def test_google_search_success(self, mock_session_cls):
        """Test the main function with mocked requests."""
        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.cookies = {}
        mock_session_cls.return_value = mock_session_instance

        # Responses: Homepage + Search
        homepage_resp = Mock()
        homepage_resp.status_code = 200

        search_resp = Mock()
        search_resp.status_code = 200
        search_resp.text = self.mock_html

        mock_session_instance.get.side_effect = [homepage_resp, search_resp]

        results = google_search("test query", num_results=3)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], "Welcome to Python.org")

    @patch('google_search_lib.search.requests.Session')
    def test_google_search_pagination(self, mock_session_cls):
        """Test that pagination works."""
        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.cookies = {}
        mock_session_cls.return_value = mock_session_instance

        page1_html = """
        <html><body>
            <div class="g"><h3>Title 1</h3><a href="link1"></a><div class="VwiC3b">Snippet 1</div></div>
            <div class="g"><h3>Title 2</h3><a href="link2"></a><div class="VwiC3b">Snippet 2</div></div>
        </body></html>
        """

        page2_html = """
        <html><body>
            <div class="g"><h3>Title 3</h3><a href="link3"></a><div class="VwiC3b">Snippet 3</div></div>
            <div class="g"><h3>Title 4</h3><a href="link4"></a><div class="VwiC3b">Snippet 4</div></div>
        </body></html>
        """

        homepage_resp = Mock(status_code=200)
        p1_resp = Mock(status_code=200, text=page1_html)
        p2_resp = Mock(status_code=200, text=page2_html)

        mock_session_instance.get.side_effect = [homepage_resp, p1_resp, p2_resp]

        results = google_search("pagination test", num_results=3)

        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], "Title 1")
        self.assertEqual(results[2]['title'], "Title 3")

    @patch('google_search_lib.search.requests.Session')
    def test_google_search_429(self, mock_session_cls):
        """Test handling of 429 Too Many Requests."""
        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.cookies = {}
        mock_session_cls.return_value = mock_session_instance

        # Homepage ok, then 429 forever
        homepage_resp = Mock(status_code=200)
        bad_resp = Mock(status_code=429)

        # return homepage once, then bad_resp repeatedly
        mock_session_instance.get.side_effect = [homepage_resp] + [bad_resp]*10

        results = google_search("test", num_results=5)

        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
