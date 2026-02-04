import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
import sys

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(self, start_urls, max_pages=50, max_workers=10, timeout=None):
        self.start_urls = start_urls
        self.max_pages = max_pages
        self.max_workers = max_workers
        self.timeout = timeout
        self.start_time = None
        self.visited = set()
        self.crawled_data = {}
        self.queue = None
        self.session = None
        self.stop_event = None

    async def _fetch(self, url):
        try:
            async with self.session.get(url, timeout=5) as response:
                if response.status != 200:
                    return None
                if 'text/html' not in response.headers.get('Content-Type', ''):
                    return None
                return await response.text()
        except Exception as e:
            logger.debug(f"Failed to fetch {url}: {e}")
            return None

    def _parse(self, html, url):
        try:
            # Use lxml for speed
            soup = BeautifulSoup(html, 'lxml')
            title = soup.title.string if soup.title else url
            text_content = soup.get_text(separator=' ', strip=True)

            outbound_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)

                parsed = urlparse(full_url)
                if parsed.scheme in ('http', 'https'):
                    clean_url = full_url.split('#')[0]
                    # Simple normalization
                    if clean_url != '/' and clean_url.endswith('/'):
                        clean_url = clean_url[:-1]
                    outbound_links.append(clean_url)

            return {
                'title': title,
                'content': text_content,
                'links': outbound_links
            }
        except Exception as e:
            logger.error(f"Error parsing {url}: {e}")
            return None

    async def _worker(self):
        while True:
            try:
                url = await self.queue.get()

                if url is None:
                    self.queue.task_done()
                    break

                # Check limits
                if self.timeout and (time.time() - self.start_time > self.timeout):
                    self.stop_event.set()
                    self.queue.task_done()
                    continue

                if len(self.visited) >= self.max_pages:
                    self.stop_event.set()
                    self.queue.task_done()
                    continue

                if url in self.visited:
                    self.queue.task_done()
                    continue

                self.visited.add(url)
                logger.info(f"Crawling: {url} (Visited: {len(self.visited)})")

                html = await self._fetch(url)
                if not html:
                    self.queue.task_done()
                    continue

                # Run parsing in executor
                loop = asyncio.get_running_loop()
                data = await loop.run_in_executor(None, self._parse, html, url)

                if data:
                    self.crawled_data[url] = data
                    for link in data['links']:
                        if link not in self.visited:
                            self.queue.put_nowait(link)

                self.queue.task_done()

            except Exception as e:
                logger.error(f"Worker exception: {e}")
                try:
                    self.queue.task_done()
                except ValueError:
                    pass

    async def _run_crawl(self):
        self.start_time = time.time()
        self.queue = asyncio.Queue()
        self.visited = set()
        self.crawled_data = {}
        self.stop_event = asyncio.Event()

        for url in self.start_urls:
            self.queue.put_nowait(url)

        timeout = aiohttp.ClientTimeout(total=10)
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            self.session = session

            workers = [asyncio.create_task(self._worker()) for _ in range(self.max_workers)]

            # Wait for queue to be empty OR stop signal (max pages/timeout)
            queue_join_task = asyncio.create_task(self.queue.join())
            stop_signal_task = asyncio.create_task(self.stop_event.wait())

            done, pending = await asyncio.wait(
                [queue_join_task, stop_signal_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            # If we stopped due to signal (max pages), drain queue so workers can pick up Poison Pills
            if stop_signal_task in done:
                logger.info("Stop signal received (Max pages or Timeout). Stopping workers...")
                while not self.queue.empty():
                    try:
                        self.queue.get_nowait()
                        self.queue.task_done()
                    except asyncio.QueueEmpty:
                        break

            # Send Poison Pills (Sentinels) to stop workers gracefully
            for _ in range(self.max_workers):
                self.queue.put_nowait(None)

            # Wait for all workers to finish their current task and exit
            await asyncio.gather(*workers)

            # Cleanup helper tasks
            if not stop_signal_task.done():
                stop_signal_task.cancel()
            if not queue_join_task.done():
                queue_join_task.cancel()

            # Await cancelled tasks to suppress warnings
            try: await stop_signal_task;
            except asyncio.CancelledError: pass
            try: await queue_join_task;
            except asyncio.CancelledError: pass

        logger.info(f"Crawl complete. Visited {len(self.visited)} pages.")
        return self.crawled_data

    def crawl(self):
        """
        Synchronous entry point for the crawler.
        """
        try:
            # Fix for Windows asyncio loop with aiohttp
            if sys.platform == 'win32':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            return asyncio.run(self._run_crawl())
        except Exception as e:
            logger.error(f"Crawl failed: {e}")
            return {}
