from setuptools import setup, find_packages

setup(
    name="mini_search_engine",
    version="0.1.0",
    description="A simple search engine library with Crawling, Indexing, and PageRank.",
    author="Jules",
    packages=find_packages(),
    install_requires=[
        "requests",
        "beautifulsoup4",
        "numpy"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
