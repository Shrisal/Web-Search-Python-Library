import numpy as np
import scipy.sparse as sp
from collections import defaultdict
import math

class Ranker:
    def __init__(self, crawled_data, doc_map, inverted_index, doc_lengths, avgdl):
        self.crawled_data = crawled_data
        self.doc_map = doc_map
        self.reverse_doc_map = {v: k for k, v in doc_map.items()}
        self.inverted_index = inverted_index
        self.doc_lengths = doc_lengths
        self.avgdl = avgdl
        self.num_docs = len(doc_map)
        self.pagerank_scores = None

        # BM25 parameters
        self.k1 = 1.5
        self.b = 0.75

    def compute_pagerank(self, damping=0.85, max_iter=100, tol=1.0e-6):
        print("Computing PageRank (Sparse)...")
        if self.num_docs == 0:
            self.pagerank_scores = np.array([])
            return

        # Build Sparse Adjacency Matrix
        # M[i, j] = 1/OutDegree(j) if j -> i

        rows = []
        cols = []
        data = []

        out_degrees = np.zeros(self.num_docs)

        # First pass: calculate out-degrees and edges
        # We need to use doc_ids
        for url, doc_data in self.crawled_data.items():
            if url not in self.doc_map: continue

            src_id = self.doc_map[url]
            links = doc_data.get('links', [])

            valid_targets = [self.doc_map[link] for link in links if link in self.doc_map]
            out_degree = len(valid_targets)
            out_degrees[src_id] = out_degree

            if out_degree > 0:
                prob = 1.0 / out_degree
                for target_id in valid_targets:
                    rows.append(target_id)
                    cols.append(src_id)
                    data.append(prob)

        # Create CSC matrix for fast matrix-vector multiplication
        M = sp.csc_matrix((data, (rows, cols)), shape=(self.num_docs, self.num_docs))

        # Identify dangling nodes (out_degree == 0)
        dangling_nodes = np.where(out_degrees == 0)[0]

        # Power Iteration
        r = np.ones(self.num_docs) / self.num_docs
        teleport = (1 - damping) / self.num_docs

        for i in range(max_iter):
            prev_r = r.copy()

            # r = d * M * r + d * (sum(r[dangling]) / N) + (1-d)/N

            # Sparse multiply
            r = damping * (M @ r)

            # Add dangling mass
            dangling_sum = np.sum(prev_r[dangling_nodes])
            dangling_correction = damping * (dangling_sum / self.num_docs)

            # Add teleport and correction
            r += teleport + dangling_correction

            # Check convergence
            err = np.linalg.norm(r - prev_r, 1)
            if err < tol:
                print(f"PageRank converged in {i+1} iterations.")
                break

        self.pagerank_scores = r
        return r

    def score(self, query_terms):
        """
        Calculates scores for documents based on query terms using BM25 and PageRank.
        Returns list of (doc_id, score).
        """
        if self.num_docs == 0:
            return []

        scores = defaultdict(float)

        # 1. BM25 Scoring
        for term in query_terms:
            if term not in self.inverted_index:
                continue

            posting_list = self.inverted_index[term] # [(doc_id, tf), ...]
            df = len(posting_list)
            idf = math.log(1 + (self.num_docs - df + 0.5) / (df + 0.5))

            for doc_id, tf in posting_list:
                doc_len = self.doc_lengths.get(doc_id, 0)

                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avgdl))

                term_score = idf * (numerator / denominator)
                scores[doc_id] += term_score

        # 2. Combine with PageRank
        # Normalize BM25 scores to be somewhat comparable to PageRank or vice-versa?
        # PageRank sum is 1. BM25 scores can be anything (e.g. 5, 10, 20).
        # A simple linear combination might let one dominate.
        # But for now, let's just add a weighted PageRank.
        # Typically PageRank is multiplicative or added with a weight.
        # Score = BM25 + w * log(PageRank) ?
        # Or Score = BM25 * PageRank^w ?
        # Let's try: Score = BM25 + w * PageRank * (some_scaling_factor)
        # Since PageRank is small (~1/N), we need to boost it.
        # Let's say w=1000 assuming N is not huge, or just multiply.

        # A common approach: BM25 * Pagerank_Score (if Pagerank is quality).
        # But if Pagerank is 0 for some reason, it kills the score.
        # Let's do a weighted sum.

        final_results = []
        if not scores:
            return []

        # Find max BM25 to normalize?
        # max_bm25 = max(scores.values()) if scores else 1

        for doc_id, bm25_score in scores.items():
            pr_score = self.pagerank_scores[doc_id] if self.pagerank_scores is not None else 0
            # Heuristic combination
            final_score = bm25_score + (pr_score * 100) # Weight PageRank
            final_results.append((doc_id, final_score))

        final_results.sort(key=lambda x: x[1], reverse=True)
        return final_results
