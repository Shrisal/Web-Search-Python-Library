import requests
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, unquote

# List of realistic User-Agents to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
]

class GoogleSearchSession:
    """
    Manages a session with Google to mimic a real browser behavior.
    """
    def __init__(self, proxies=None):
        self.session = requests.Session()
        if proxies:
            self.session.proxies.update(proxies)

        self.user_agent = random.choice(USER_AGENTS)
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def _ensure_cookies(self):
        """
        Visits the Google homepage to establish cookies if not present.
        """
        if not self.session.cookies.get("NID") and not self.session.cookies.get("AEC"):
            try:
                self.session.get("https://www.google.com/", timeout=10)
                time.sleep(random.uniform(0.5, 1.5))
            except requests.RequestException:
                pass

    def search(self, query, num_results=10, retry_count=3):
        self._ensure_cookies()

        results = []
        start = 0
        results_per_page = 10

        while len(results) < num_results:
            if start == 0:
                self.session.headers.update({"Referer": "https://www.google.com/"})
            else:
                prev_start = start - results_per_page
                self.session.headers.update({"Referer": f"https://www.google.com/search?q={quote_plus(query)}&start={prev_start}&gbv=1"})

            # Using gbv=1 for Google Basic Version (non-JS)
            url = f"https://www.google.com/search?q={quote_plus(query)}&start={start}&gbv=1"

            attempt = 0
            success = False

            while attempt <= retry_count:
                try:
                    if start > 0 or attempt > 0:
                        delay = random.uniform(2, 5) * (1.5 ** attempt)
                        time.sleep(delay)

                    response = self.session.get(url, timeout=10)

                    if response.status_code == 200:
                        new_results = _parse_results(response.text)

                        if not new_results:
                            if "trouble accessing Google Search" in response.text:
                                pass # Blocked
                            else:
                                break # End of results

                        if new_results:
                            results.extend(new_results)
                            start += results_per_page
                            success = True
                            break
                        else:
                            attempt += 1
                            continue

                    elif response.status_code in [429, 500, 502, 503, 504]:
                        attempt += 1
                        continue
                    else:
                        break

                except requests.RequestException:
                    attempt += 1

            if not success:
                break

        return results[:num_results]

def _parse_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # In gbv=1 (Basic HTML), results are often in:
    # div.g, or sometimes just div class="g"
    # Title is h3 > a
    # Snippet is often in div.s, div.st, or just a div after title

    result_blocks = soup.select("div.g")

    for block in result_blocks:
        item = {}

        title_el = block.select_one("h3")
        if not title_el:
            # Sometimes simpler structure
            title_el = block.select_one("a")
            if not title_el or len(title_el.get_text()) < 5: continue

        item["title"] = title_el.get_text()

        link_el = block.select_one("a")
        # Ensure we get the actual link, not the /url?q= redirect if possible,
        # but in gbv=1 it's often /url?q=...
        if not link_el or not link_el.has_attr("href"): continue

        href = link_el["href"]
        if href.startswith("/url?q="):
            # Extract and unquote the actual URL
            href = href.split("/url?q=")[1].split("&")[0]
            href = unquote(href)

        item["link"] = href

        # Snippet logic for gbv=1
        snippet_el = block.select_one("div.s") or \
                     block.select_one("div.st") or \
                     block.select_one("div.VwiC3b") or \
                     block.select_one("span.st")

        if snippet_el:
            item["snippet"] = snippet_el.get_text().replace('\n', '')
        else:
            # Fallback: look for text container that isn't title/link/metadata
            item["snippet"] = ""

        results.append(item)

    return results

def google_search(query, num_results=10, proxies=None, retry_count=3):
    """
    Performs a Google search and returns a list of results.
    """
    session = GoogleSearchSession(proxies=proxies)
    return session.search(query, num_results=num_results, retry_count=retry_count)
