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
    """Rewrite text with a professional and engaging tone using Sumy (LSA)."""
    if not text or len(text) <= 0:
        return "No summary available at this time."
    # Clean up artifacts thoroughly
    cleaned_text = re.sub(r'\[\+\d+ chars\]', '', text).strip()
    cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text).strip()
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    
    # Use Sumy to extract key sentences
    parser = PlaintextParser.from_string(cleaned_text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary_sentences = summarizer(parser.document, 2)  # Get 2 key sentences for coherence
    summary_text = " ".join(str(sentence) for sentence in summary_sentences)
    
    # Ensure the summary fits the length and add a professional, engaging tone
    if len(summary_text) <= max_length:
        return f"Unveiling a critical update, {summary_text.strip()}. Discover more at the source."
    return f"Shedding light on a pressing issue, {summary_text[:max_length].strip()}... Explore the full narrative at the source."

def extract_media_urls(article):
    """Extract image and video URLs from article metadata."""
    media = {}
    # NewsAPI media
    if 'urlToImage' in article and article['urlToImage']:
        media['image'] = article['urlToImage']
    # RSS feed media
    if 'media_content' in article:
        for content in article.get('media_content', []):
            if content.get('type', '').startswith('image/'):
                media['image'] = content.get('url')
            elif content.get('type', '').startswith('video/'):
                media['video'] = content.get('url')
    # Additional RSS fields
    if 'media_thumbnail' in article:
        media['image'] = article['media_thumbnail'][0].get('url')
    if 'enclosure' in article and 'type' in article['enclosure'] and article['enclosure']['type'].startswith('image/'):
        media['image'] = article['enclosure'].get('url')
    return media

@app.route('/news')
def get_news():
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            return jsonify({"error": "NEWS_API_KEY not found in environment variables"}), 500
        
        from_date = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%d')
        # Stronger focus on Africa and Middle East, excluding Ukraine
        newsapi_url = f"https://newsapi.org/v2/everything?q=((Africa+OR+Middle+East+OR+Syria+OR+Palestine+OR+Gaza+OR+Yemen+OR+Sudan)+AND+(conflict+OR+war+OR+crisis+OR+tension+OR+violence+OR+protest))+-Ukraine+-Russia+-Zelensky+-technology+-entertainment+-sports+-automotive+-music+-lifestyle+-travel+-business+-finance&language=en&from={from_date}&sortBy=relevancy&apiKey={news_api_key}&pageSize=5"
        newsapi_response = requests.get(newsapi_url)
        newsapi_response.raise_for_status()
        newsapi_data = newsapi_response.json()
        newsapi_articles = newsapi_data.get('articles', [])

        # RSS feeds with stricter filtering
        rss_feeds = [
            "https://africa.cgtn.com/feed/",  # CGTN Africa
            "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera (filter for Africa)
            "https://www.middleeasteye.net/rss",  # Middle East Eye
            "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera (filter for Syria/Palestine)
            "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml",  # BBC Middle East
            "http://feeds.bbci.co.uk/news/world/africa/rss.xml",  # BBC Africa
        ]
        rss_articles = []
        for feed_url in rss_feeds:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:  # Increase to 3 entries per feed for more content
                title = entry.get('title', '').lower()
                summary = entry.get('summary', '').lower()
                # Stricter filtering for Africa, Middle East, excluding Ukraine
                is_relevant = (
                    ("africa" in title or "africa" in summary or
                     "syria" in title or "syria" in summary or
                     "palestine" in title or "palestine" in summary or
                     "gaza" in title or "gaza" in summary or
                     "yemen" in title or "yemen" in summary or
                     "sudan" in title or "sudan" in summary or
                     "violence" in title or "violence" in summary or
                     "crisis" in title or "crisis" in summary) and
                    "ukraine" not in title and "ukraine" not in summary and
                    "russia" not in title and "russia" not in summary and
                    "zelensky" not in title and "zelensky" not in summary
                )
                if is_relevant:
                    rss_article = {
                        'title': entry.get('title', 'No title'),
                        'description': entry.get('summary', 'No description'),
                        'url': entry.get('link', '#'),
                        'publishedAt': entry.get('published', datetime.utcnow().isoformat()),
                        'media_content': entry.get('media_content', []),
                        'media_thumbnail': entry.get('media_thumbnail', []),
                        'enclosure': entry.get('enclosure', {})
                    }
                    rss_articles.append(rss_article)

        all_articles = newsapi_articles + rss_articles
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
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500
    except Exception as e:
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