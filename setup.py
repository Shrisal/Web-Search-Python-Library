from setuptools import setup, find_packages
import pathlib

# Read the contents of your README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="mini_search_engine",
    version="1.0.0",
    description="A simple search engine library scraping Google and DuckDuckGo.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shrisal/Web-Search-Python-Library",
    author="Shriyan Salapakkam and Jules",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    keywords="search, google, duckduckgo, scraping, crawler",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "certifi"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Shrisal/Web-Search-Python-Library/issues",
        "Source": "https://github.com/Shrisal/Web-Search-Python-Library",
    },
)
