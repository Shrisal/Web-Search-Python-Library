import re
from collections import Counter

class Indexer:
    def __init__(self, crawled_data):
        self.crawled_data = crawled_data
        self.inverted_index = {} # token -> [(doc_id, tf), ...]
        self.doc_map = {} # url -> doc_id (int)
        self.reverse_doc_map = {} # doc_id -> url
        self.doc_lengths = {} # doc_id -> int
        self.avgdl = 0.0

    def build_index(self):
        print("Building index...")

        if not self.crawled_data:
            return self.inverted_index, self.doc_map, {}, 0

        # Create integer IDs for documents
        for i, url in enumerate(self.crawled_data.keys()):
            self.doc_map[url] = i
            self.reverse_doc_map[i] = url

        total_length = 0

        for url, data in self.crawled_data.items():
            doc_id = self.doc_map[url]
            # Weight title more? For now just concatenate.
            text = (data['title'] + " ") * 2 + data['content']
            tokens = self._tokenize(text)
            length = len(tokens)
            self.doc_lengths[doc_id] = length
            total_length += length

            # Calculate Term Frequencies
            term_counts = Counter(tokens)

            for token, count in term_counts.items():
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append((doc_id, count))

        num_docs = len(self.crawled_data)
        self.avgdl = total_length / num_docs if num_docs > 0 else 0

        print(f"Index built. Total terms: {len(self.inverted_index)}. Avg DL: {self.avgdl:.2f}")
        return self.inverted_index, self.doc_map, self.doc_lengths, self.avgdl

    def _tokenize(self, text):
        # Improved tokenization
        text = text.lower()
        # Keep alphanumeric, maybe some dashes?
        tokens = re.findall(r'\b[a-z0-9]+\b', text)
        return tokens
