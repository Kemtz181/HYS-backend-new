import feedparser
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)

def summarize_text(text, max_length=300):
    """Improved summarization with sentence boundary detection."""
    cleaned_text = re.sub(r'\[.*?\]', '', text or '').strip()
    if len(cleaned_text) <= max_length:
        return cleaned_text
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + " "
        else:
            break
    return summary.strip() + "..."

@app.route('/news')
def get_news():
    try:
        api_key = os.getenv('NEWS_API_KEY')
        if not api_key:
            return jsonify({"error": "NEWS_API_KEY missing"}), 500

        from_date = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%d')
        url = f"https://newsapi.org/v2/everything?q=conflict&from={from_date}&language=en&apiKey={api_key}&pageSize=5"
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        articles = [
            {"title": a["title"], "description": summarize_text(a["description"]), "url": a["url"], "media": {"image": a.get("urlToImage")}}
            for a in data.get("articles", [])
        ]
        return jsonify({"articles": articles})

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
