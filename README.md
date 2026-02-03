# Google Search Library

A lightweight Python library to perform Google searches without using the official API.

## Installation

```bash
pip install .
```

## Usage

```python
from google_search_lib import google_search

results = google_search("python programming", num_results=5)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Link: {result['link']}")
    print(f"Snippet: {result['snippet']}")
    print("-" * 20)
```

## Features

- **No API Key Required**: Scrapes Google search results directly.
- **Lightweight**: Uses `requests` and `beautifulsoup4`.
- **Anti-Scraping Measures**: Randomizes `User-Agent` and adds delays between requests.
- **Pagination**: Automatically fetches multiple pages to reach the desired `num_results`.

## Limitations & Disclaimer

- **Rate Limiting**: Google aggressively blocks automated requests. This library includes delays and User-Agent rotation, but you may still encounter `429 Too Many Requests` or CAPTCHA pages (Service Interruption).
- **Structure Changes**: Google frequently changes its HTML structure. This library uses standard selectors that work for most desktop results, but it may break if the layout changes significantly.
- **IP Blocking**: Running this in cloud environments (like AWS, GCP, Azure) often results in immediate blocking. It works best on residential IPs.

## License

MIT
