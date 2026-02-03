from setuptools import setup, find_packages

setup(
    name="google_search_lib",
    version="0.1.0",
    description="A lightweight Google search library without API.",
    author="Jules",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
        "beautifulsoup4>=4.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
