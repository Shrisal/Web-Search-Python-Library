import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class Crawler:
    def __init__(self, start_urls, max_pages=50):
        self.start_urls = start_urls
        self.max_pages = max_pages
        self.visited = set()
        self.queue = list(start_urls)

        # Maps url -> {title: str, content: str, links: [urls]}
        self.crawled_data = {}

    def crawl(self):
        print(f"Starting crawl with max_pages={self.max_pages}")
        while self.queue and len(self.visited) < self.max_pages:
            url = self.queue.pop(0)

            if url in self.visited:
                continue

            print(f"Crawling: {url}")
            try:
                # Basic politeness
                time.sleep(0.5)

                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    continue

                # Verify content type
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type:
                    continue

                self.visited.add(url)

                # Parse
                soup = BeautifulSoup(response.text, 'html.parser')

                title = soup.title.string if soup.title else url
                text_content = soup.get_text(separator=' ', strip=True)

                # Extract links
                outbound_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)

                    # Basic filtering: http/https only, remove fragments
                    parsed = urlparse(full_url)
                    if parsed.scheme in ('http', 'https'):
                        clean_url = full_url.split('#')[0]
                        outbound_links.append(clean_url)

                        if clean_url not in self.visited and clean_url not in self.queue:
                            self.queue.append(clean_url)

                self.crawled_data[url] = {
                    'title': title,
                    'content': text_content,
                    'links': outbound_links
                }

            except Exception as e:
                print(f"Failed to crawl {url}: {e}")

        print(f"Crawl complete. Visited {len(self.visited)} pages.")
        return self.crawled_data
