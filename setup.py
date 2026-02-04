from setuptools import setup, find_packages

setup(
    name="mini_search_engine",
    version="0.2.0",
    description="A simple search engine library scraping Google and DuckDuckGo.",
    author="Jules",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "certifi"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
