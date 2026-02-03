# Mini Search Engine

A lightweight Python library to **Build Your Own Search Engine**. It includes a web crawler, an inverted indexer, and a ranking algorithm based on **PageRank** to find and rank relevant links.

## Installation

```bash
pip install .
```

## Usage

This library allows you to crawl a set of websites, build an index in memory, and search through them with relevance sorting.

```python
from mini_search_engine import SearchEngine

# 1. Initialize the engine
engine = SearchEngine()

# 2. Build the database (Crawl -> Index -> Rank)
# This may take time depending on max_pages
print("Crawling and building index...")
engine.build_db(
    start_urls=["https://www.python.org/"],
    max_pages=20
)

# 3. Search
print("\n--- Search Results for 'documentation' ---")
results = engine.search("documentation")

for i, res in enumerate(results):
    print(f"#{i+1} [Score: {res['score']:.4f}] {res['title']}")
    print(f"Link: {res['link']}")
    print("-" * 20)
```

## How It Works

1.  **Crawler**: Fetches pages using `requests` and `BeautifulSoup`. It follows links (BFS) up to `max_pages`.
2.  **Indexer**: tokenizes content and builds an **Inverted Index** mapping keywords to documents.
3.  **Ranker**:
    *   Constructs a link graph from the crawled data.
    *   Computes **PageRank** scores (iterative power method) to determine authority.
4.  **Search**:
    *   Finds documents containing all query terms (AND search).
    *   Ranks them by their pre-computed PageRank score.

## Limitations

- **In-Memory**: All data is stored in memory. Not suitable for crawling thousands of pages without modification.
- **Simple Tokenization**: Does not handle stemming (e.g., "running" vs "run") or complex NLP.
- **Politeness**: Includes basic delays, but aggressive crawling may get you blocked by target sites.

## License

MIT
