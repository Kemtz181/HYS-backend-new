from datetime import datetime, timedelta
from flask import Flask, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Home route
@app.route('/')
def home():
    return "Hello from HaveYourSay Backend!"

from datetime import datetime, timedelta

@app.route('/news')
def get_news():
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            return jsonify({"error": "NEWS_API_KEY not found in environment variables"}), 500
        
        from_date = (datetime.utcnow() - timedelta(days=14)).strftime('%Y-%m-%d')  # Past 14 days
        url = f"https://newsapi.org/v2/everything?q=conflict+OR+war+OR+crisis+OR+dispute+-sports+-entertainment&from={from_date}&sortBy=publishedAt&apiKey={news_api_key}&pageSize=5"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('status') != 'ok':
            return jsonify({"error": "NewsAPI request failed", "details": data}), 500
        return data
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500

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