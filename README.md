# Mini Search Engine

A simple Python library that attempts to scrape Google for search results, falling back to DuckDuckGo if blocked.

## Features

-   **Google Search**: Attempts to fetch results from Google directly.
-   **DuckDuckGo Fallback**: Automatically switches to DuckDuckGo if Google blocks the request (which is common).
-   **No API Key Needed**: Uses web scraping.

## Installation

```bash
pip install -r requirements.txt
pip install .
```

## Quick Start

```python
from mini_search_engine import SearchEngine
import logging

logging.basicConfig(level=logging.INFO)

# 1. Initialize the engine
engine = SearchEngine()

# 2. Search!
query = "python programming"
print(f"\nSearching for: '{query}'")
results = engine.search(query)

# Display results
for i, res in enumerate(results):
    print(f"#{i+1} {res['title']}")
    print(f"Link: {res['link']}")
    print(f"Snippet: {res['snippet']}")
    print("-" * 30)
```

## Note

This tool scrapes search engines. Use responsibly. Google frequently blocks scraping attempts. This tool includes a fallback to DuckDuckGo to ensure results are returned.
