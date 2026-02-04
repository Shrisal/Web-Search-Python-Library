import requests
from bs4 import BeautifulSoup
import logging
import time
import random

# Configure logger
logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def build_db(self, start_urls=None, max_pages=50, max_workers=10, timeout=None):
        """
        Deprecated: This method is no longer needed as the search engine
        now queries the web directly. Kept for compatibility.
        """
        print("Note: build_db() is deprecated and does nothing. The engine searches the live web now.")
        logger.warning("build_db() called but is deprecated.")

    def search(self, query):
        """
        Searches the web for the query. Attempts Google first, then falls back to DuckDuckGo.
        """
        print(f"Searching for: {query}")

        # specific handling for the "google.com" requirement
        results = self._search_google(query)

        if not results:
            print("Google search yielded no results (likely blocked), falling back to DuckDuckGo...")
            results = self._search_duckduckgo(query)

        return results

    def _search_google(self, query):
        url = "https://www.google.com/search"
        params = {"q": query}

        # Try to look like a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            if "systems have detected unusual traffic" in response.text or "recaptcha" in response.text.lower():
                logger.warning("Google blocked the request.")
                return []

            soup = BeautifulSoup(response.text, "lxml")
            results = []

            for g in soup.select("div.g"):
                title_elem = g.select_one("h3")
                link_elem = g.select_one("a")

                if title_elem and link_elem:
                    title = title_elem.get_text()
                    link = link_elem["href"]

                    if "/url?q=" in link:
                        link = link.split("/url?q=")[1].split("&")[0]

                    snippet = "No snippet"
                    snippet_div = g.select_one("div.VwiC3b, div.IsZvec, span.aCOpRe")
                    if snippet_div:
                        snippet = snippet_div.get_text()

                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet,
                        "score": 1.0 # Placeholder score
                    })
            return results

        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return []

    def _search_duckduckgo(self, query):
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
             "Referer": "https://html.duckduckgo.com/"
        }

        try:
            response = self.session.post(url, data=params, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            for result in soup.select(".result"):
                title_elem = result.select_one(".result__a")
                snippet_elem = result.select_one(".result__snippet")

                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem["href"]
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No snippet"

                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet,
                        "score": 1.0
                    })
            return results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return []
