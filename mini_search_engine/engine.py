from .crawler import Crawler
from .indexer import Indexer
from .ranker import Ranker
from .seeds import DEFAULT_SEEDS
import re

class SearchEngine:
    def __init__(self):
        self.crawler = None
        self.indexer = None
        self.ranker = None
        self.crawled_data = {}

    def build_db(self, start_urls=None, max_pages=50, max_workers=5, timeout=None):
        """
        Builds the search engine database by crawling, indexing, and ranking.

        Args:
            start_urls (list): List of URLs to start crawling from. If None, uses default seeds.
            max_pages (int): Maximum number of pages to crawl.
            max_workers (int): Number of parallel crawl threads.
            timeout (int): Maximum time in seconds to crawl.
        """
        if start_urls is None:
            start_urls = DEFAULT_SEEDS

        self.crawler = Crawler(start_urls, max_pages=max_pages, max_workers=max_workers, timeout=timeout)
        self.crawled_data = self.crawler.crawl()

        self.indexer = Indexer(self.crawled_data)
        self.inverted_index, self.doc_map = self.indexer.build_index()
        self.reverse_doc_map = self.indexer.reverse_doc_map

        self.ranker = Ranker(self.crawled_data, self.doc_map)
        self.ranker.compute_pagerank()

    def search(self, query):
        if not self.indexer:
            raise Exception("Search engine not built. Call build_db() first.")

        print(f"Searching for: {query}")
        query_tokens = re.findall(r'\b\w+\b', query.lower())

        # AND search
        matching_doc_ids = set()
        first_term = True

        for token in query_tokens:
            if token in self.inverted_index:
                doc_ids = set(self.inverted_index[token])
                if first_term:
                    matching_doc_ids = doc_ids
                    first_term = False
                else:
                    matching_doc_ids = matching_doc_ids.intersection(doc_ids)
            else:
                matching_doc_ids = set()
                break

        # Rank the results
        ranked_scores = self.ranker.score_results(list(matching_doc_ids))

        results = []
        for doc_id, score in ranked_scores:
            url = self.reverse_doc_map[doc_id]
            data = self.crawled_data[url]
            results.append({
                'title': data['title'],
                'link': url,
                'snippet': data['content'][:200] + "...",
                'score': score
            })

        return results
