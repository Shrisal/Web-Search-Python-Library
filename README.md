# Google Search Library

A robust, lightweight Python library to perform Google searches without using the official API.

## Installation

```bash
pip install .
```

## Usage

```python
from google_search_lib import google_search

# Basic search
results = google_search("python programming", num_results=5)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Link: {result['link']}")
    print(f"Snippet: {result['snippet']}")
    print("-" * 20)

# Using Proxies and Retries
proxies = {
    "http": "http://user:pass@10.10.1.10:3128",
    "https": "http://user:pass@10.10.1.10:1080",
}

results = google_search(
    "web scraping",
    num_results=20,
    proxies=proxies,
    retry_count=5
)
```

## Features

- **No API Key Required**: Scrapes Google search results directly.
- **Robust Session Handling**: Uses a session to manage cookies and headers, mimicking a real browser to avoid detection.
- **Anti-Scraping Measures**:
    - Randomizes `User-Agent` and other headers.
    - Adds polite delays between requests.
    - Visits the homepage first to establish session cookies.
- **Proxy Support**: Full support for HTTP/HTTPS proxies.
- **Retry Logic**: Built-in exponential backoff for handling `429 Too Many Requests` or network errors.

## Limitations & Disclaimer

- **Rate Limiting**: Google aggressively blocks automated requests. While this library is designed to be robust (handling retries and sessions), you may still encounter blocks (CAPTHCAs) if making excessive requests from a single IP.
- **IP Blocking**: Cloud data center IPs (AWS, GCP, etc.) are often flagged by Google. For best results, use residential proxies or a local machine.
- **Structure Changes**: Google frequently changes its HTML structure. This library uses standard selectors that work for most desktop results, but it may break if the layout changes significantly.

## License

MIT
