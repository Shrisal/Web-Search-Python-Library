from .crawler import Crawler
from .indexer import Indexer
from .ranker import Ranker
import re

class SearchEngine:
    def __init__(self):
        self.crawler = None
        self.indexer = None
        self.ranker = None
        self.crawled_data = {}

    def build_db(self, start_urls, max_pages=50):
        self.crawler = Crawler(start_urls, max_pages)
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

        # Find docs containing ANY of the terms (OR search)
        # Better: AND search
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
                # If a term is not found in AND search, result is empty
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
                'snippet': data['content'][:200] + "...", # Simple snippet
                'score': score
            })

        return results

# Convenience function similar to previous library
def google_search(query, num_results=10):
    # This is a placeholder as this engine usually requires a build step.
    # But to satisfy the interface, we could instantiate and throw an error or usage hint.
    raise NotImplementedError("This is a local search engine. Instantiate SearchEngine, call build_db(seed_urls), then search().")
