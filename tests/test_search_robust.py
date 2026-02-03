import unittest
from unittest.mock import patch, Mock
import os
import sys

# Add the parent directory to the path so we can import the library
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from google_search_lib.search import google_search, GoogleSearchSession

class TestGoogleSearchRobustness(unittest.TestCase):

    def setUp(self):
        # Basic mock HTML for successful parsing
        self.mock_html = """
        <html><body>
            <div class="g">
                <h3>Test Title</h3>
                <a href="http://example.com"></a>
                <div class="VwiC3b">Test Snippet</div>
            </div>
        </body></html>
        """

    @patch('google_search_lib.search.requests.Session')
    def test_proxies_passed(self, mock_session_cls):
        """Test that proxies are correctly passed to the session."""
        mock_session_instance = Mock()
        mock_session_instance.proxies = {} # simulate proxies dict
        mock_session_instance.headers = {}
        mock_session_instance.cookies = Mock() # Updated to Mock
        mock_session_cls.return_value = mock_session_instance

        # Setup mock return for ensure_cookies (get homepage) and search (get search)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.mock_html

        mock_session_instance.get.return_value = mock_response

        proxies = {"http": "http://10.10.1.10:3128", "https": "http://10.10.1.10:1080"}

        google_search("test", num_results=1, proxies=proxies)

        # Verify proxies were updated in the session
        self.assertEqual(mock_session_instance.proxies, proxies)

    @patch('google_search_lib.search.time.sleep')
    @patch('google_search_lib.search.requests.Session')
    def test_retry_logic_success(self, mock_session_cls, mock_sleep):
        """Test that it retries on failure and eventually succeeds."""
        mock_session_instance = Mock()
        mock_session_instance.headers = {}
        mock_session_instance.cookies = Mock() # Updated to Mock
        mock_session_instance.cookies.get.return_value = None
        mock_session_cls.return_value = mock_session_instance

        # Responses:
        # 1. Homepage (for ensure_cookies) -> 200 OK
        # 2. Search -> 500 Error
        # 3. Search -> 500 Error
        # 4. Search -> 200 OK (Success)

        homepage_response = Mock()
        homepage_response.status_code = 200

        bad_response = Mock()
        bad_response.status_code = 500

        good_response = Mock()
        good_response.status_code = 200
        good_response.text = self.mock_html

        # We need to set side_effect on the instance.get method
        mock_session_instance.get.side_effect = [homepage_response, bad_response, bad_response, good_response]

        results = google_search("test", num_results=1, retry_count=3)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Test Title")

        # Expected calls: 1 homepage + 1 failed + 1 failed + 1 success = 4 calls
        self.assertEqual(mock_session_instance.get.call_count, 4)

if __name__ == '__main__':
    unittest.main()
