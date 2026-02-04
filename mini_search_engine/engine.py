import requests
from bs4 import BeautifulSoup
import logging
import time
import random
import urllib.parse

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

    def search(self, query, engine="auto", limit=10, safe="moderate", time_range=None):
        """
        Searches the web for the query with extensive control.

        Args:
            query (str): The search query.
            engine (str): 'google', 'ddg', or 'auto'. Defaults to 'auto'.
                          If the specified engine fails, it will attempt the other one.
            limit (int): Approximate number of results to return. Defaults to 10.
            safe (str): Safe search level. 'strict', 'moderate', or 'off'.
                        Defaults to 'moderate'.
            time_range (str): 'd' (day), 'w' (week), 'm' (month), 'y' (year).
                              Defaults to None (any time).

        Returns:
            list: A list of result dictionaries.
        """
        print(f"Searching for: '{query}' (Engine: {engine}, Limit: {limit}, Safe: {safe}, Time: {time_range})")

        # Determine execution order
        engines_to_try = []
        if engine.lower() == 'google':
            engines_to_try = ['google', 'ddg']
        elif engine.lower() == 'ddg' or engine.lower() == 'duckduckgo':
            engines_to_try = ['ddg', 'google']
        else:
            engines_to_try = ['google', 'ddg'] # Default preference

        for eng in engines_to_try:
            results = []
            if eng == 'google':
                results = self._search_google(query, limit, safe, time_range)
            elif eng == 'ddg':
                results = self._search_duckduckgo(query, limit, safe, time_range)

            if results:
                return results[:limit]

            print(f"{eng.capitalize()} returned no results or failed. Trying next available engine...")

        print("All engines failed to return results.")
        return []

    def _search_google(self, query, limit, safe, time_range):
        base_url = "https://www.google.com/search"
        results = []
        start = 0

        # Map parameters
        params = {
            "q": query,
            "hl": "en"
        }

        # Safe Search
        if safe == 'strict':
            params['safe'] = 'active'
        elif safe == 'off':
            params['safe'] = 'images' # 'off' isn't explicitly 'off' in url, but omitting often defaults to moderate. 'images' is a trick or just omit.
            # Actually, omitting 'safe' is usually moderate. explicit 'safe=active' is strict.
            # To turn OFF, sometimes 'safe=off' works or 'safe=undefined'.
            # We'll just omit it for 'off' and 'moderate', and use 'active' for strict.
            if 'safe' in params: del params['safe']

        # Time Range
        if time_range:
            # Map d, w, m, y to qdr:d, qdr:w, etc.
            tr_map = {'d': 'd', 'w': 'w', 'm': 'm', 'y': 'y'}
            if time_range in tr_map:
                params['tbs'] = f"qdr:{tr_map[time_range]}"

        while len(results) < limit:
            # Use a copy of params to avoid mutation issues in mocks/retries
            current_params = params.copy()
            current_params['start'] = start

            try:
                # Add random delay if paging
                if start > 0:
                    time.sleep(random.uniform(1.0, 2.5))

                response = self.session.get(base_url, params=current_params, timeout=10)
                response.raise_for_status()

                if "systems have detected unusual traffic" in response.text or "recaptcha" in response.text.lower():
                    logger.warning("Google blocked the request.")
                    break

                soup = BeautifulSoup(response.text, "lxml")
                current_page_results = []

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

                        res = {
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "score": 1.0,
                            "source": "google"
                        }
                        current_page_results.append(res)
                        results.append(res)

                        if len(results) >= limit:
                            break

                if not current_page_results:
                    # No more results on this page
                    break

                start += 10

            except Exception as e:
                logger.error(f"Google search failed: {e}")
                break

        return results

    def _search_duckduckgo(self, query, limit, safe, time_range):
        url = "https://html.duckduckgo.com/html/"
        results = []

        # Initial Params
        data = {
            "q": query,
            "kl": "us-en" # Default region
        }

        # Safe Search
        # kp: -2 (strict), -1 (off), 1 (moderate)?
        # Checking online: kp=-2 is strict, kp=-1 is off. kp=1 is moderate.
        if safe == 'strict':
            data['kp'] = '-2'
        elif safe == 'off':
            data['kp'] = '-1'
        else:
            data['kp'] = '1' # moderate

        # Time Range
        if time_range:
            tr_map = {'d': 'd', 'w': 'w', 'm': 'm', 'y': 'y'}
            if time_range in tr_map:
                data['df'] = tr_map[time_range]

        while len(results) < limit:
            try:
                # Add random delay if paging
                if len(results) > 0:
                    time.sleep(random.uniform(0.5, 1.5))

                response = self.session.post(url, data=data, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                current_page_results = []

                # Parse Results
                for result in soup.select(".result"):
                    if "result--ad" in result.get("class", []):
                        continue

                    title_elem = result.select_one(".result__a")
                    snippet_elem = result.select_one(".result__snippet")

                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        raw_link = title_elem["href"]
                        link = raw_link

                        # Decode DDG redirection
                        if "uddg=" in raw_link:
                            try:
                                parsed = urllib.parse.urlparse(raw_link)
                                qs = urllib.parse.parse_qs(parsed.query)
                                if 'uddg' in qs:
                                    link = qs['uddg'][0]
                            except Exception:
                                pass

                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else "No snippet"

                        res = {
                            "title": title,
                            "link": link,
                            "snippet": snippet,
                            "score": 1.0,
                            "source": "duckduckgo"
                        }
                        current_page_results.append(res)
                        results.append(res)

                        if len(results) >= limit:
                            break

                if not current_page_results:
                    break

                # Check for limit
                if len(results) >= limit:
                    break

                # Pagination: Find the "Next" form
                # Usually a form with action="/html/" and input value="Next"
                next_form = None
                for form in soup.select("form[action='/html/']"):
                    if form.select_one("input[value='Next']"):
                        next_form = form
                        break

                if next_form:
                    # Extract inputs for the next request
                    new_data = {}
                    for inp in next_form.select("input"):
                        name = inp.get("name")
                        value = inp.get("value")
                        if name:
                            new_data[name] = value
                    data = new_data
                else:
                    # No next page
                    break

            except Exception as e:
                logger.error(f"DuckDuckGo search failed: {e}")
                break

        return results
