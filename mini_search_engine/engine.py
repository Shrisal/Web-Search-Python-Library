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
        self.inverted_index = {}
        self.doc_map = {}
        self.reverse_doc_map = {}
        self.doc_lengths = {}
        self.avgdl = 0

    def build_db(self, start_urls=None, max_pages=50, max_workers=10, timeout=None):
        """
        Builds the search engine database by crawling, indexing, and ranking.

        Args:
            start_urls (list): List of URLs to start crawling from. If None, uses default seeds.
            max_pages (int): Maximum number of pages to crawl.
            max_workers (int): Number of parallel crawl threads. Default increased to 10 for speed.
            timeout (int): Maximum time in seconds to crawl.
        """
        if start_urls is None:
            start_urls = DEFAULT_SEEDS

        self.crawler = Crawler(start_urls, max_pages=max_pages, max_workers=max_workers, timeout=timeout)
        self.crawled_data = self.crawler.crawl()

        self.indexer = Indexer(self.crawled_data)
        self.inverted_index, self.doc_map, self.doc_lengths, self.avgdl = self.indexer.build_index()
        self.reverse_doc_map = self.indexer.reverse_doc_map

        self.ranker = Ranker(
            self.crawled_data,
            self.doc_map,
            self.inverted_index,
            self.doc_lengths,
            self.avgdl
        )
        self.ranker.compute_pagerank()

    def search(self, query):
        if not self.indexer:
            raise Exception("Search engine not built. Call build_db() first.")

        print(f"Searching for: {query}")
        query_tokens = re.findall(r'\b[a-z0-9]+\b', query.lower())

        # Rank the results (BM25 + PageRank)
        ranked_scores = self.ranker.score(query_tokens)

        results = []
        for doc_id, score in ranked_scores:
            url = self.reverse_doc_map[doc_id]
            data = self.crawled_data[url]
            results.append({
                'title': data['title'],
                'link': url,
                'snippet': self._generate_snippet(data['content'], query_tokens),
                'score': float(score) # Ensure standard float
            })

        return results

    def _generate_snippet(self, content, query_tokens):
        lower_content = content.lower()
        best_pos = -1

        # Simple: find first occurrence of any term
        # A better approach would be to find the window with max terms
        for token in query_tokens:
            pos = lower_content.find(token)
            if pos != -1:
                # If we haven't found a position yet, or this one is earlier (or we want some logic)
                # Actually, earlier is good for top context.
                if best_pos == -1 or pos < best_pos:
                    best_pos = pos

        if best_pos == -1:
            return content[:200] + "..." if len(content) > 200 else content

        start = max(0, best_pos - 60)
        end = min(len(content), best_pos + 140)

        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet
