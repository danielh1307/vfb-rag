# VfB Stuttgart Blog Crawler

Sample RAG application, see also: https://python.langchain.com/docs/tutorials/rag/

This project contains tools to crawl content from the VfB Stuttgart website.

## Features

- `main.py`: Crawls player profiles from the VfB Stuttgart website
- `crawl_blog.py`: Crawls blog articles from the VfB Stuttgart news section

## Requirements

- Python 3.8+
- Chrome browser installed

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Crawling Blog Articles

To crawl blog articles from the VfB Stuttgart website:

```bash
python crawl_blog.py
```

This will:
1. Navigate to the VfB Stuttgart news page
2. Extract all blog articles from the page
3. Save the article metadata to a JSON file in the `blog_articles` directory
4. Save the full HTML content of each article to individual files in the `blog_articles` directory

### Crawling Player Profiles

To crawl player profiles from the VfB Stuttgart website:

```bash
python main.py
```

This will:
1. Navigate to the VfB Stuttgart website
2. Extract all player profile links
3. Save the content of each player profile to a text file in the `player_profiles` directory

## Notes

- The blog crawler uses Selenium to handle JavaScript-rendered content
- Make sure you have Chrome browser installed on your system
- The crawler may take some time to complete depending on the number of articles 