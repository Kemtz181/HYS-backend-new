import feedparser
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)

def summarize_text(text, max_length=300):
    """Truncates text at sentence boundaries and removes unwanted markers."""
    if not text or len(text.strip()) == 0:
        return "No summary available."

    # Remove artifacts like "[+380 chars]" and other bracketed text
    cleaned_text = re.sub(r'\[\+\d+ chars\]', '', text).strip()
    cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text).strip()

    if len(cleaned_text) <= max_length:
        return cleaned_text

    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + " "
        else:
            break

    return summary.strip() + " [Read full article at the source]" if len(cleaned_text) > max_length else summary.strip()

def extract_media_urls(article):
    """Extracts images and videos from articles."""
    media = {}
    
    # Extract from NewsAPI
    if 'urlToImage' in article and article['urlToImage']:
        media['image'] = article['urlToImage']

    # Extract from RSS Feeds (if media content exists)
    if 'media_content' in article:
        for content in article.get('media_content', []):
            if content.get('type', '').startswith('image/'):
                media['image'] = content.get('url')
            elif content.get('type', '').startswith('video/'):
                media['video'] = content.get('url')
    
    return media

@app.route("/")
def home():
    return (
        "Welcome to HaveYourSay – a platform dedicated to amplifying voices from underreported conflicts "
        "and political tensions worldwide. Stay informed, explore, and share impactful stories."
    )

@app.route('/news')
def get_news():
    """Fetches news from NewsAPI and RSS feeds."""
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            return jsonify({"error": "NEWS_API_KEY not found in environment variables"}), 500

        from_date = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%d')

        # Fetch news from NewsAPI
        newsapi_url = (
            f"https://newsapi.org/v2/everything?q=(conflict OR war OR crisis OR tension OR protest) "
            f"AND (Africa OR Middle East OR Ukraine OR Europe) -technology -entertainment -sports "
            f"-automotive -music -lifestyle -travel -business -finance&language=en&from={from_date}&sortBy=relevancy"
            f"&apiKey={news_api_key}&pageSize=5"
        )
        newsapi_response = requests.get(newsapi_url)
        newsapi_response.raise_for_status()
        newsapi_data = newsapi_response.json()
        newsapi_articles = newsapi_data.get('articles', [])

        # Fetch news from RSS feeds
        rss_feeds = [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "http://www.aljazeera.com/xml/rss/all.xml",
            "http://feeds.reuters.com/reuters/topNews",
            "https://www.apnews.com/apf-content/rss/feed/category/breaking-news"
        ]
        rss_articles = []
        for feed_url in rss_feeds:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:  # Get 2 articles per feed
                rss_article = {
                    'title': entry.get('title', 'No title'),
                    'description': summarize_text(entry.get('summary', 'No description'), 150),
                    'url': entry.get('link', '#'),
                    'publishedAt': entry.get('published', datetime.utcnow().isoformat())
                }
                rss_articles.append(rss_article)

        # Combine NewsAPI & RSS articles
        all_articles = newsapi_articles + rss_articles

        # Process and clean each article
        for article in all_articles:
            raw_text = article.get('content', article.get('description', article.get('summary', 'No full text available')))
            article['description'] = summarize_text(raw_text, 150)
            article['full_text'] = summarize_text(raw_text, 300) + f" [Read full article at: {article.get('url', '#')}]"
            article['media'] = extract_media_urls(article)

        return jsonify({"articles": all_articles})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error processing news: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
