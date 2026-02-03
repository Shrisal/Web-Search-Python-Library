# Mini Search Engine

A lightweight, beginner-friendly Python library that lets you build your own search engine from scratch.

It includes a **Parallel Web Crawler**, a **Search Indexer**, and a **Ranking Algorithm** (PageRank) to find and sort the most relevant websites.

## Installation

```bash
pip install .
```

## Quick Start

You can build a search engine in just 3 lines of code! By default, it starts crawling from a list of popular, high-quality websites (Wikipedia, Python.org, GitHub, etc.).

```python
from mini_search_engine import SearchEngine

# 1. Initialize the engine
engine = SearchEngine()

# 2. Build the database
# This will start crawling the web from default seeds in parallel.
# It fetches 20 pages to create a small network.
print("Crawling the web... please wait.")
engine.build_db(max_pages=20)

# 3. Search!
query = "python"
print(f"\nSearching for: '{query}'")
results = engine.search(query)

# Display results
for i, res in enumerate(results):
    print(f"#{i+1} [Score: {res['score']:.4f}] {res['title']}")
    print(f"Link: {res['link']}")
    print("-" * 30)
```

## How It Works (Simplified)

### 1. The Crawler (The "Spider")
Imagine sending out 10 little robots (threads) to different websites. They read the page, save the text, and find all the links to other pages. They add those new links to a queue, and the robots go visit them next. This continues until they have visited `max_pages`.

### 2. The Indexer (The "Book")
Once the robots return, the Indexer reads all the text. It creates a massive list (like the index at the back of a textbook) that maps every word to the pages it appears on.
*   "Apple" -> [Page 1, Page 5]
*   "Banana" -> [Page 2]

### 3. The Ranker (The "Judge")
Not all pages are equal. The Ranker uses an algorithm called **PageRank** (famous for being Google's original algorithm). It looks at the links between pages.
*   If Page A links to Page B, it's like a "vote" for Page B.
*   If a really popular page votes for Page B, that vote counts more.
*   The Ranker calculates a score for every page based on these votes.

### 4. The Search
When you search for "Python":
1.  The engine looks in the **Index** to find all pages containing "Python".
2.  It uses the **Ranker's** scores to sort them, so the most authoritative pages come first.

## Advanced Usage

You can customize where the crawler starts (seeds), how fast it crawls (threads), and how long it runs.

```python
# Customize crawling behavior
engine.build_db(
    start_urls=["https://en.wikipedia.org/wiki/Python_(programming_language)"],
    max_pages=100,      # Stop after 100 pages
    max_workers=20,     # Use 20 parallel threads for super fast crawling!
    timeout=60          # OR stop after 60 seconds, whichever comes first
)
```

### Tips for Speed
- Increase `max_workers` to crawl more sites at once (e.g., 50).
- Be careful! Crawling too fast might get you blocked by some websites.

## License

MIT
