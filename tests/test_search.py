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
        """Test that the internal parser correctly extracts data from HTML (gbv=1 style)."""
        results = _parse_results(self.mock_html)

        self.assertEqual(len(results), 2)

        # Check first result (Standard)
        self.assertEqual(results[0]['title'], "Welcome to Python.org")
        self.assertEqual(results[0]['link'], "https://www.python.org/")
        self.assertIn("official home of the Python", results[0]['snippet'])

        # Check second result
        self.assertEqual(results[1]['title'], "Python (programming language) - Wikipedia")
        self.assertEqual(results[1]['link'], "https://en.wikipedia.org/wiki/Python_(programming_language)")

    @patch('google_search_lib.search.requests.Session')
    def test_google_search_success(self, mock_session_cls):
        """Test the main function with mocked requests."""
        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        # cookies needs to be a Mock with .set() and .get()
        mock_session_instance.cookies = Mock()
        mock_session_instance.cookies.get.return_value = None # simulate no cookies initially

        mock_session_cls.return_value = mock_session_instance

        homepage_resp = Mock(status_code=200)
        search_resp = Mock(status_code=200, text=self.mock_html)

        mock_session_instance.get.side_effect = [homepage_resp, search_resp]

        results = google_search("test query", num_results=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], "Welcome to Python.org")

    @patch('google_search_lib.search.requests.Session')
    def test_google_search_pagination(self, mock_session_cls):
        """Test that pagination works (gbv=1 style)."""
        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.cookies = Mock()
        mock_session_instance.cookies.get.return_value = None
        mock_session_cls.return_value = mock_session_instance

        page1_html = """
        <html><body>
            <div class="g"><h3><a href="/url?q=link1">Title 1</a></h3><div class="s">Snippet 1</div></div>
            <div class="g"><h3><a href="/url?q=link2">Title 2</a></h3><div class="s">Snippet 2</div></div>
        </body></html>
        """

        page2_html = """
        <html><body>
            <div class="g"><h3><a href="/url?q=link3">Title 3</a></h3><div class="s">Snippet 3</div></div>
            <div class="g"><h3><a href="/url?q=link4">Title 4</a></h3><div class="s">Snippet 4</div></div>
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
        mock_session_instance.cookies = Mock()
        mock_session_instance.cookies.get.return_value = None
        mock_session_cls.return_value = mock_session_instance

        homepage_resp = Mock(status_code=200)
        bad_resp = Mock(status_code=429)

        mock_session_instance.get.side_effect = [homepage_resp] + [bad_resp]*10

        results = google_search("test", num_results=5)

        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
