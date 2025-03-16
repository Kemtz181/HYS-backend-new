import feedparser
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
    cleaned_text = re.sub(r'\[\+\d+ chars\]', '', text).strip()
    cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text).strip()
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
    print(f"Cleaned text: {cleaned_text[:100]}...")  # Debug: First 100 chars
    
    try:
        parser = PlaintextParser.from_string(cleaned_text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary_sentences = summarizer(parser.document, 2)  # Get 2 key sentences
        summary_text = " ".join(str(sentence) for sentence in summary_sentences)
        print(f"Sumy summary: {summary_text[:100]}...")  # Debug: First 100 chars of summary
    except Exception as e:
        print(f"Sumy error: {e}")
        summary_text = cleaned_text[:max_length]  # Fallback to truncated cleaned text
    
    if len(summary_text) <= max_length:
        return f"Unveiling a critical update, {summary_text.strip()}. Discover more at the source."
    return f"Shedding light on a pressing issue, {summary_text[:max_length].strip()}... Explore the full narrative at the source."

def extract_media_urls(article):
    """Extract image and video URLs with debug."""
    media = {}
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
        rss_feeds = [
            "https://www.aljazeera.com/xml/rss/all.xml",  # Al Jazeera
            "http://feeds.bbci.co.uk/news/world/rss.xml",  # BBC World
            "http://feeds.reuters.com/reuters/topNews",  # Reuters
            "https://www.lemonde.fr/rss/une.xml",  # Le Monde
            "https://www.ndtv.com/rss/news/world-news",  # NDTV World
            "https://africa.cgtn.com/feed/",  # CGTN Africa
        ]
        rss_articles = []
        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                print(f"Parsing RSS feed: {feed_url}, Entries: {len(feed.entries)}, Status: {feed.status}")
                if not feed.entries:
                    print(f"No entries in feed: {feed_url}")
                    continue
                for entry in feed.entries[:3]:
                    title = entry.get('title', '').lower()
                    summary = entry.get('summary', '').lower()
                    print(f"RSS entry - Title: {title[:50]}..., Summary: {summary[:50]}...")
                    # Exclude entertainment, tech, sports
                    if any(term in (title + summary) for term in ['entertainment', 'tech', 'technology', 'sports', 'sport']):
                        print(f"Rejected RSS article: {entry.get('title', 'No title')} - Contains excluded term")
                        continue
                    # Check publication date (last 7 days)
                    pub_date = entry.get('published_parsed')
                    if pub_date:
                        pub_datetime = datetime.fromtimestamp(sum(x * y for x, y in zip(pub_date[:6], [1, 60, 3600, 86400, 2629743, 31556926])))
                        if pub_datetime < (datetime.utcnow() - timedelta(days=7)):
                            print(f"Rejected RSS article: {entry.get('title', 'No title')} - Too old")
                            continue
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

        print(f"RSS articles count: {len(rss_articles)}")
        all_articles = rss_articles
        print(f"Total articles after combining: {len(all_articles)}")
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