# Mini Search Engine

A high-performance, beginner-friendly Python library that lets you build your own search engine from scratch.

It features a **Blazing Fast Async Crawler**, a **Search Indexer** with BM25, and a **Ranking Algorithm** (PageRank) optimized with sparse matrices.

## Features

-   **Extremely Fast Crawling**: Uses `asyncio` and `aiohttp` to fetch hundreds of pages in seconds.
-   **Smart Ranking**: Combines **BM25** (the industry standard for text relevance) with **PageRank** (link authority).
-   **Efficient**: Uses sparse matrices (`scipy.sparse`) to calculate PageRank for large networks without running out of memory.
-   **Contextual Snippets**: Generates result snippets highlighting your query terms.

## Installation

```bash
pip install -r requirements.txt
pip install .
```

## Quick Start

You can build a search engine in just 3 lines of code! By default, it starts crawling from a list of popular, high-quality websites (Wikipedia, Python.org, GitHub, etc.).

```python
from mini_search_engine import SearchEngine

# 1. Initialize the engine
engine = SearchEngine()

# 2. Build the database
# This will start crawling the web from default seeds.
# It uses asynchronous workers for maximum speed.
print("Crawling the web... please wait.")
engine.build_db(max_pages=50, max_workers=20)

# 3. Search!
query = "python programming"
print(f"\nSearching for: '{query}'")
results = engine.search(query)

# Display results
for i, res in enumerate(results):
    print(f"#{i+1} [Score: {res['score']:.2f}] {res['title']}")
    print(f"Link: {res['link']}")
    print(f"Snippet: {res['snippet']}")
    print("-" * 30)
```

## How It Works (Simplified)

### 1. The Crawler (The "Spider")
We use **Asynchronous I/O** (AsyncIO). Instead of using heavy threads, we use lightweight tasks. Imagine a single waiter efficiently taking orders from 50 tables at once, rather than hiring 50 waiters. This allows the crawler to reach thousands of pages extremely quickly.

### 2. The Indexer (The "Book")
The indexer builds an "Inverted Index" that maps words to documents. It also calculates:
*   **Term Frequency (TF)**: How often a word appears in a page.
*   **Document Length**: To normalize scores (a word in a short tweet is more important than in a long book).

### 3. The Ranker (The "Judge")
We combine two scores to give you the best results:
*   **BM25**: Calculates text relevance. It rewards pages where your search terms appear frequently but penalizes common words (like "the").
*   **PageRank**: Calculates authority. It looks at the "web" of links. If important pages link to Page A, Page A becomes important. We use **Sparse Matrices** to compute this efficiently for millions of pages.

## Advanced Usage

```python
# Customize crawling behavior
engine.build_db(
    start_urls=["https://en.wikipedia.org/wiki/Python_(programming_language)"],
    max_pages=500,      # Crawl more pages
    max_workers=50,     # Use 50 concurrent connections
    timeout=120         # Stop after 2 minutes
)
```

### Tips for Speed
-   `max_workers` controls concurrency. With `asyncio`, you can easily set this to 50 or 100 without slowing down your computer.

## License

MIT
