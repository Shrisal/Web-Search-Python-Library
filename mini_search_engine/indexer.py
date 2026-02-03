import re

class Indexer:
    def __init__(self, crawled_data):
        self.crawled_data = crawled_data
        self.inverted_index = {} # word -> [url, url, ...]
        self.doc_map = {} # url -> doc_id (int)
        self.reverse_doc_map = {} # doc_id -> url

    def build_index(self):
        print("Building index...")

        # Create integer IDs for documents for efficiency
        for i, url in enumerate(self.crawled_data.keys()):
            self.doc_map[url] = i
            self.reverse_doc_map[i] = url

        for url, data in self.crawled_data.items():
            doc_id = self.doc_map[url]
            text = data['content'] + " " + data['title']
            tokens = self._tokenize(text)

            for token in set(tokens): # Use set to record presence once per doc (simple inverted index)
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append(doc_id)

        print(f"Index built. Total terms: {len(self.inverted_index)}")
        return self.inverted_index, self.doc_map

    def _tokenize(self, text):
        # Simple tokenization: lowercase, remove non-alphanumeric
        text = text.lower()
        tokens = re.findall(r'\b\w+\b', text)
        return tokens
