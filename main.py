import feedparser
import requests
from flask import Flask, jsonify
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)

def clean_text(text):
    """Cleans up news descriptions by removing incomplete text and unnecessary brackets."""
    if not text:
        return "No summary available."
    
    # Remove cutoff markers (e.g., "... [+380 chars]")
    text = re.sub(r'\s*\[\+\d+ chars\]', '', text)
    
    # Ensure proper sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return ' '.join(sentences[:2])  # Use first two full sentences

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
            {
                "title": a["title"], 
                "description": clean_text(a.get("description", "")), 
                "url": a["url"], 
                "media": {"image": a.get("urlToImage")}
            }
            for a in data.get("articles", [])
        ]
        return jsonify({"articles": articles})

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
