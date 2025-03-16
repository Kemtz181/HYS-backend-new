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

# News route (NewsAPI)
@app.route('/news')
def get_news():
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            return jsonify({"error": "NEWS_API_KEY not found in environment variables"}), 500
        
        from_date = (datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')  # Past 2 days
        url = f"https://newsapi.org/v2/everything?q=technology&from={from_date}&sortBy=publishedAt&apiKey={news_api_key}&pageSize=5"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('status') != 'ok':
            return jsonify({"error": "NewsAPI request failed", "details": data}), 500
        return data
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500

# Grok API route (xAI)
# Grok API route (xAI)
@app.route('/grok')
def get_grok():
    return jsonify({"status": "not_implemented", "message": "Grok API integration pending - correct endpoint required"}), 501

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