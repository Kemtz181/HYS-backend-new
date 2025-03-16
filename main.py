import feedparser
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta
import os

app = Flask(__name__)

@app.route('/news')
def get_news():
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            return jsonify({"error": "NEWS_API_KEY not found in environment variables"}), 500
        
        from_date = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%d')
        # NewsAPI call
        newsapi_url = f"https://newsapi.org/v2/everything?q=(conflict+OR+war+OR+crisis+OR+tension+OR+protest)+AND+(Africa+OR+Middle+East+OR+Ukraine+OR+Europe)+-technology+-entertainment+-sports+-automotive+-music+-lifestyle+-travel+-business+-finance&language=en&from={from_date}&sortBy=relevancy&apiKey={news_api_key}&pageSize=5"
        newsapi_response = requests.get(newsapi_url)
        newsapi_response.raise_for_status()
        newsapi_data = newsapi_response.json()
        newsapi_articles = newsapi_data.get('articles', [])

        # RSS feeds
        rss_feeds = [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "http://www.aljazeera.com/xml/rss/all.xml",
            "http://feeds.reuters.com/reuters/topNews",
            "https://www.apnews.com/apf-content/rss/feed/category/breaking-news"
        ]
        rss_articles = []
        for feed_url in rss_feeds:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:  # Limit to 2 per feed
                rss_articles.append({
                    'title': entry.get('title', 'No title'),
                    'description': entry.get('summary', 'No description')[:150] + '...' if len(entry.get('summary', 'No description')) > 150 else entry.get('summary', 'No description'),
                    'url': entry.get('link', '#'),
                    'full_text': entry.get('summary', 'No full text available') + f" [Full article at: {entry.get('link', '#')}]"
                })

        # Combine articles
        all_articles = newsapi_articles + rss_articles
        for article in all_articles:
            full_text = article.get('full_text', article.get('content', article.get('description', 'No full text available')))
            if full_text and '...' in full_text[-10:] or len(full_text) < 200:
                article['full_text'] = f"{full_text} [Full article at: {article.get('url', '#')}]"
            else:
                article['full_text'] = full_text
            article['description'] = article.get('description', full_text[:150] + '...') if len(full_text) > 150 else full_text

        return jsonify({"articles": all_articles})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500
except Exception as e:
    return jsonify({"error": f"Error processing RSS: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

import requests
import os
from datetime import datetime, timedelta

@app.route('/grok')
def get_grok():
    try:
        grok_api_key = os.getenv('GROK_API_KEY', 'xai-Xi5LRXNlaPl6fsU1d1r24oMpeEwX77q8l958XJluCW3hoLllIMHeBu9Jxm5S3WlFTpx0IIBEul1ziva')
        if not grok_api_key:
            return jsonify({"error": "GROK_API_KEY not found in environment variables"}), 500
        
        # Simulated X post data (replace with real X API call if you have a key)
        simulated_x_posts = [
            {"text": "Unreported clashes in rural Yemen, locals say aid is delayed.", "user": "YemenVoice", "date": "2025-03-14"},
            {"text": "Heavy fighting in eastern Congo, no media coverage.", "user": "CongoWatch", "date": "2025-03-13"}
        ]
        payload = {
            "messages": [
                {"role": "system", "content": "You are a news aggregator analyzing X posts for underreported conflicts."},
                {"role": "user", "content": f"Summarize these X posts for underreported conflicts: {simulated_x_posts}"}
            ],
            "model": "grok-2-latest"
        }
        headers = {
            "Authorization": f"Bearer {grok_api_key}",
            "Content-Type": "application/json"
        }
        url = "https://api.x.ai/v1/chat/completions"
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return jsonify({"summary": data.choices[0].message.content if data.choices else "No summary available"})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch Grok data: {str(e)}"}), 500

# Gemini API route (Google)
@app.route('/gemini')
def get_gemini():
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            return jsonify({"error": "GEMINI_API_KEY not found in environment variables"}), 500
        
        # Correct Gemini API endpoint (using the latest model name)
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "contents": [{
                "parts": [{
                    "text": "Summarize the latest trends in technology."
                }]
            }]
        }
        response = requests.post(f"{url}?key={gemini_api_key}", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch Gemini data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)