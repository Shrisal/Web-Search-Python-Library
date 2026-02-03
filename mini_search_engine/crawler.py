import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import concurrent.futures
import threading

class Crawler:
    def __init__(self, start_urls, max_pages=50, max_workers=5, timeout=None):
        self.start_urls = start_urls
        self.max_pages = max_pages
        self.max_workers = max_workers
        self.timeout = timeout
        self.start_time = None

        # Thread-safe structures
        self.visited = set()
        self.lock = threading.Lock()

        self.queue = list(start_urls)
        # Maps url -> {title: str, content: str, links: [urls]}
        self.crawled_data = {}

    def _is_visited(self, url):
        with self.lock:
            return url in self.visited

    def _mark_visited(self, url):
        with self.lock:
            self.visited.add(url)

    def _should_stop(self):
        with self.lock:
            if len(self.visited) >= self.max_pages:
                return True
            if self.timeout and (time.time() - self.start_time > self.timeout):
                return True
            return False

    def _add_to_queue(self, urls):
        with self.lock:
            for url in urls:
                if url not in self.visited and url not in self.queue:
                    self.queue.append(url)

    def _get_next_url(self):
        with self.lock:
            if not self.queue:
                return None
            return self.queue.pop(0)

    def _crawl_page(self, url):
        if self._should_stop():
            return

        print(f"Crawling: {url}")
        try:
            time.sleep(0.5)

            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return

            if 'text/html' not in response.headers.get('Content-Type', ''):
                return

            self._mark_visited(url)

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else url
            text_content = soup.get_text(separator=' ', strip=True)

            outbound_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)

                parsed = urlparse(full_url)
                if parsed.scheme in ('http', 'https'):
                    clean_url = full_url.split('#')[0]
                    outbound_links.append(clean_url)

            with self.lock:
                self.crawled_data[url] = {
                    'title': title,
                    'content': text_content,
                    'links': outbound_links
                }

            self._add_to_queue(outbound_links)

        except Exception as e:
            print(f"Failed to crawl {url}: {e}")

    def crawl(self):
        self.start_time = time.time()
        print(f"Starting parallel crawl with {self.max_workers} workers...")
        if self.timeout:
            print(f"Time limit set to {self.timeout} seconds.")

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            while not self._should_stop():
                url = self._get_next_url()

                if url:
                    if self._is_visited(url):
                        continue

                    future = executor.submit(self._crawl_page, url)
                    futures.append(future)
                else:
                    running = [f for f in futures if not f.done()]
                    if not running:
                        break
                    time.sleep(0.1)

            concurrent.futures.wait(futures)

        print(f"Crawl complete. Visited {len(self.visited)} pages.")
        return self.crawled_data
