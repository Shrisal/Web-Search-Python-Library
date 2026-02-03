import numpy as np

class Ranker:
    def __init__(self, crawled_data, doc_map):
        self.crawled_data = crawled_data
        self.doc_map = doc_map
        self.num_docs = len(doc_map)
        if self.num_docs > 0:
            self.pagerank_scores = np.ones(self.num_docs) / self.num_docs
        else:
            self.pagerank_scores = np.array([])

    def compute_pagerank(self, damping=0.85, max_iter=100, tol=1.0e-6):
        print("Computing PageRank...")
        if self.num_docs == 0:
            return self.pagerank_scores

        # Build Adjacency Matrix
        # M[j][i] = 1/L(j) if j -> i
        M = np.zeros((self.num_docs, self.num_docs))

        for url, data in self.crawled_data.items():
            if url not in self.doc_map: continue

            src_id = self.doc_map[url]
            outbound_links = data['links']

            # Filter valid internal links (links to pages we actually crawled)
            valid_targets = []
            for link in outbound_links:
                if link in self.doc_map:
                    valid_targets.append(self.doc_map[link])

            if not valid_targets:
                # Dangling node (no outbound links): distribute score to all
                M[:, src_id] = 1.0 / self.num_docs
            else:
                prob = 1.0 / len(valid_targets)
                for target_id in valid_targets:
                    M[target_id, src_id] = prob

        # Power Iteration
        # r = d * M * r + (1 - d) / N
        r = np.ones(self.num_docs) / self.num_docs
        constant = (1 - damping) / self.num_docs

        for i in range(max_iter):
            prev_r = r.copy()
            r = damping * M @ r + constant

            err = np.linalg.norm(r - prev_r, 1)
            if err < tol:
                print(f"PageRank converged in {i+1} iterations.")
                break

        self.pagerank_scores = r
        return r

    def score_results(self, result_doc_ids):
        """
        Combines PageRank with (implicit) keyword relevance.
        For now, returns just the PageRank score for sorting.
        """
        if self.num_docs == 0:
            return []

        scores = []
        for doc_id in result_doc_ids:
            score = self.pagerank_scores[doc_id]
            scores.append((doc_id, score))

        # Sort by score desc
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
