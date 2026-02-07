# Mini Search Engine

A flexible Python library that scrapes Google and DuckDuckGo for search results. It supports extensive search features including pagination, safe search, and time filtering.

## Features

-   **Multi-Engine Support**: Search via Google or DuckDuckGo.
-   **Smart Fallback**: Automatically tries the next available engine if the primary one is blocked (e.g., falls back to DuckDuckGo if Google blocks).
-   **Pagination**: Retrieve as many results as you need.
-   **Safe Search**: Control safe search strictness (`strict`, `moderate`, `off`).
-   **Time Filtering**: Filter results by day, week, month, or year.
-   **No API Key Needed**: Uses direct web scraping.

## Installation

You can install the package directly from PyPI:

```bash
pip install mini-search-engine
```


## Usage

```python
from mini_search_engine import SearchEngine
import logging

# Optional: Enable logging to see what's happening under the hood
logging.basicConfig(level=logging.INFO)

engine = SearchEngine()

# Simple Search
results = engine.search("python programming")
for res in results:
    print(res['title'], res['link'])

# Advanced Search with Filters
results = engine.search(
    "latest python news",
    engine="auto",       # Try Google, then DDG
    limit=20,            # Get 20 results (handles pagination automatically)
    safe="strict",       # Strict safe search
    time_range="w"       # Past week
)

print(f"\nFound {len(results)} results:")
for i, res in enumerate(results):
    print(f"#{i+1} [{res['source']}] {res['title']}")
    print(f"Link: {res['link']}")
    print(f"Snippet: {res['snippet']}")
    print("-" * 30)
```

## API Reference

### `search(query, engine="auto", limit=10, safe="moderate", time_range=None)`

-   `query` (str): The search query.
-   `engine` (str): `'google'`, `'ddg'`, or `'auto'`. Defaults to `'auto'`.
-   `limit` (int): Number of results to return. Defaults to `10`.
-   `safe` (str): Safe search level: `'strict'`, `'moderate'`, `'off'`. Defaults to `'moderate'`.
-   `time_range` (str): `'d'` (day), `'w'` (week), `'m'` (month), `'y'` (year). Defaults to `None` (any time).

## License

MIT License

## Credits

This library was developed with extensive assistance from the Jules AI coding assistant.
