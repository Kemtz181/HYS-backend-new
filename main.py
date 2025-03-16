import feedparser
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta
import os
import re
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

app = Flask(__name__)

def summarize_text(text, max_length=300):
    """Rewrite text with a professional and engaging tone using Sumy (LSA), with debug."""
    if not text or len(text) <= 0:
        print("No text to summarize")
        return "No summary available at this time."
    # Thoroughly clean artifacts
    cleaned_text = re.sub(r'\[\+\d+ chars\]', '', text).strip()
    cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text).strip()
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    print(f"Cleaned text: {cleaned_text[:100]}...")  # Debug: First 100 chars
    
    # Use Sumy to extract key sentences
    try:
        parser = PlaintextParser.from_string(cleaned_text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, 2)  # Get 2 key sentences
        summary_text = " ".join(str(sentence) for sentence in summary_sentences)
        print(f"Sumy summary: {summary_text[:100]}...")  # Debug: First 100 chars of summary
    except Exception as e:
        print(f"Sumy error: {e}")
        summary_text = cleaned_text[:max_length]  # Fallback to truncated cleaned text
    
    # Add professional and engaging tone
    if len(summary_text) <= max_length:
        return f"Unveiling a critical update, {summary_text.strip()}. Discover more at the source."
    return f"Shedding light on a pressing issue, {summary_text[:max_length].strip()}... Explore the full narrative at the source."

def extract_media_urls(article):
    """Extract image and video URLs with debug."""
    media = {}
    if 'urlToImage' in article and article['urlToImage']:
        media['image'] = article['urlToImage']
        print(f"Found image: {article['urlToImage']}")
    if 'media_content' in article:
        for content in article.get('media_content', []):
            if content.get('type', '').startswith('image/'):
                media['image'] = content.get('url')
                print(f"Found media image: {content.get('url')}")
            elif content.get('type', '').startswith('video/'):
                media['video'] = content.get('url')
                print(f"Found media video: {content.get('url')}")
    if 'media_thumbnail' in article:
        media['image'] = article['media_thumbnail'][0].get('url')
        print(f"Found thumbnail: {article['media_thumbnail'][0].get('url')}")
    return media

@app.route('/news')
def get_news():
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            print("ERROR: NEWS_API_KEY not found in environment variables")
            return jsonify({"error": "NEWS_API_KEY not found in environment variables"}), 500
        print(f"NEWS_API_KEY found: {news_api_key[:5]}...")  # Debug: First 5 chars for security

        from_date = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%d')
        # Simplified query to test NewsAPI response
        newsapi_url = f"https://newsapi.org/v2/everything?q=(Africa+OR+Middle+East+OR+Syria+OR+Palestine+OR+Gaza+OR+Yemen+OR+Sudan)+-Ukraine+-Russia+-Zelensky&language=en&from={from_date}&sortBy=relevancy&apiKey={news_api_key}&pageSize=5"
        print(f"NewsAPI URL: {newsapi_url}")  # Debug: Print the query
        try:
            newsapi_response = requests.get(newsapi_url)
            newsapi_response.raise_for_status()
            newsapi_data = newsapi_response.json()
            print(f"NewsAPI response status: {newsapi_data.get('status')}")  # Debug: API status
            print(f"NewsAPI total results: {newsapi_data.get('totalResults')}")  # Debug: Total results
            newsapi_articles = newsapi_data.get('articles', [])
            print(f"NewsAPI raw articles count: {len(newsapi_articles)}")  # Debug: Raw count
            # Log first article for inspection
            if newsapi_articles:
                print(f"First NewsAPI article: {newsapi_articles[0].get('title')}, {newsapi_articles[0].get('description')[:100]}...")
            # Filter NewsAPI articles
            filtered_newsapi_articles = [
                a for a in newsapi_articles
                if not any(term in (a.get('title', '').lower() or a.get('description', '').lower()) for term in ['ukraine', 'russia', 'zelensky'])
            ]
            print(f"NewsAPI filtered articles count: {len(filtered_newsapi_articles)}")  # Debug: Filtered count
        except requests.exceptions.RequestException as e:
            print(f"NewsAPI request error: {e}")
            filtered_newsapi_articles = []

        rss_feeds = [
            "https://africa.cgtn.com/feed/",  # CGTN Africa
            "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera
            "https://www.middleeasteye.net/rss",  # Middle East Eye
            "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",  # BBC Middle East
            "http://feeds.bbci.co.uk/news/world/africa/rss.xml",  # BBC Africa
            "https://www.africanews.com/rss",  # AfricaNews
        ]
        rss_articles = []
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                print(f"Parsing RSS feed: {feed_url}, Entries: {len(feed.entries)}, Status: {feed.status}")  # Debug: Feed status
                if not feed.entries:
                    print(f"No entries in feed: {feed_url}")
                for entry in feed.entries[:3]:
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()
                    print(f"RSS entry - Title: {title[:50]}..., Summary: {summary[:50]}...")  # Debug: Entry details
                    is_relevant = (
                        ("africa" in title or "africa" in summary or
                         "syria" in title or "syria" in summary or
                         "palestine" in title or "palestine" in summary or
                         "gaza" in title or "gaza" in summary or
                         "yemen" in title or "yemen" in summary or
                         "sudan" in title or "sudan" in summary or
                         "violence" in title or "violence" in summary or
                         "crisis" in title or "crisis" in summary or
                         "protest" in title or "protest" in summary)
                    )
                    # Relaxed exclusion: only reject if explicitly about Ukraine
                    if is_relevant and not any(term in (title + summary) for term in ['ukraine', 'russia', 'zelensky']):
                        rss_article = {
                            'title': entry.get('title', 'No title'),
                            'description': entry.get('summary', 'No description'),
                            'url': entry.get('link', '#'),
                            'publishedAt': entry.get('published', datetime.utcnow().isoformat()),
                            'media_content': entry.get('media_content', []),
                            'media_thumbnail': entry.get('media_thumbnail', [])
                        }
                        rss_articles.append(rss_article)
                        print(f"Added RSS article: {entry.get('title', 'No title')}")
            except Exception as e:
                print(f"RSS feed error for {feed_url}: {e}")

        print(f"RSS articles count: {len(rss_articles)}")  # Debug: RSS count
        all_articles = filtered_newsapi_articles + rss_articles
        print(f"Total articles after combining: {len(all_articles)}")  # Debug: Total count
        if not all_articles:
            print("No articles passed filtering")
            return jsonify({"articles": [], "message": "No recent reports available. Check back soon!"})
        for article in all_articles:
            raw_text = article.get('content', article.get('description', article.get('summary', 'No full text available')))
            if not raw_text or len(raw_text) <= 0:
                raw_text = "No content available for this article."
            article['description'] = summarize_text(raw_text, 150)
            cleaned_text = re.sub(r'\[\+\d+ chars\]', '', raw_text).strip()
            cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text).strip()
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
            if len(cleaned_text) > 300:
                article['full_text'] = summarize_text(cleaned_text, 300) + f" [Explore the full narrative at: {article.get('url', '#')}]"
            else:
                article['full_text'] = summarize_text(cleaned_text, 300) + f" [Full article at: {article.get('url', '#')}]"
            media = extract_media_urls(article)
            if media:
                article['media'] = media

        return jsonify({"articles": all_articles})
    except requests.exceptions.RequestException as e:
        print(f"Global request error: {e}")
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500
    except Exception as e:
        print(f"Global error: {e}")
        return jsonify({"error": f"Error processing news: {str(e)}"}), 500

@app.route('/grok')
def get_grok():
    try:
        insights = "Insights from the community will be displayed here once available."
        return jsonify({"summary": insights})
    except Exception as e:
        return jsonify({"error": f"Failed to fetch Grok insights: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)