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

# News route with unique date and limited articles
@app.route('/news')
def get_news():
    try:
        news_api_key = os.getenv('NEWS_API_KEY')
        if not news_api_key:
            return jsonify({"error": "NEWS_API_KEY not found in environment variables"}), 500
        
        url = f"https://newsapi.org/v2/everything?q=technology&sortBy=publishedAt&apiKey={news_api_key}&pageSize=5"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('status') != 'ok':
            return jsonify({"error": "NewsAPI request failed", "details": data}), 500
        return data
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch news: {str(e)}"}), 500

# Grok API route (placeholder - replace with real endpoint)
@app.route('/grok')
def get_grok():
    try:
        grok_api_key = os.getenv('GROK_API_KEY')
        if not grok_api_key:
            return jsonify({"error": "GROK_API_KEY not found in environment variables"}), 500
        
        url = "https://api.xai.com/grok/query"  # Replace with actual xAI Grok API endpoint
        headers = {"Authorization": f"Bearer {grok_api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch Grok data: {str(e)}"}), 500

# Gemini API route (placeholder - replace with real endpoint)
@app.route('/gemini')
def get_gemini():
    try:
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            return jsonify({"error": "GEMINI_API_KEY not found in environment variables"}), 500
        
        url = "https://api.google.com/gemini/query"  # Replace with actual Google Gemini API endpoint
        headers = {"Authorization": f"Bearer {gemini_api_key}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch Gemini data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)