from flask import Flask
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# API keys
GROK_API_KEY = os.getenv("GROK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.route('/')
def home():
    return "Hello from HaveYourSay Backend!"

@app.route('/news')
def get_news():
    try:
        # NewsAPI request (real endpoint)
        params = {
            "q": "tech",
            "apiKey": NEWS_API_KEY,
            "language": "en"
        }
        response = requests.get("https://newsapi.org/v2/everything", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch news: {str(e)}"}, 500

@app.route('/grok')
def get_grok():
    try:
        # Grok API request (hypothetical endpoint)
        headers = {"Authorization": f"Bearer {GROK_API_KEY}"}
        response = requests.get("https://api.xai.com/grok-beta/news", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch Grok news: {str(e)}"}, 500

@app.route('/gemini')
def get_gemini():
    try:
        # Gemini API request (hypothetical text generation)
        headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
        response = requests.post(
            "https://api.google.com/gemini/v2/generate",
            headers=headers,
            json={"prompt": "Summarize recent tech news"}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch Gemini data: {str(e)}"}, 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)