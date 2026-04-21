"""
News Sentiment Analysis - Analyze news impact on market
"""
import requests
from textblob import TextBlob
from datetime import datetime, timedelta
from config.config import NEWS_API_KEY
import json
import os

class NewsSentimentAnalyzer:
    """Analyze news sentiment for Indian market"""
    
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
        self.cache_file = 'data/news_cache.json'
        self.cache_duration_hours = 2  # Cache news for 2 hours (safer)
        self.request_count = 0
        self.max_requests_per_day = 90  # Leave buffer from 100 limit
    
    def fetch_news(self, query, days=1):
        """Fetch news articles with caching"""
        # Check cache first
        cached_news = self._get_cached_news(query)
        if cached_news:
            return cached_news
        
        # Check request limit
        if self.request_count >= self.max_requests_per_day:
            print(f"⚠️  News API daily limit reached ({self.max_requests_per_day} requests)")
            return []
        
        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            params = {
                'q': query,
                'from': from_date,
                'language': 'en',
                'sortBy': 'relevancy',
                'apiKey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            self.request_count += 1
            
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                # Cache the results
                self._cache_news(query, articles)
                return articles
            elif response.status_code == 429:
                print(f"⚠️  News API rate limit hit. Using cached data.")
                return []
            return []
        except Exception as e:
            print(f"⚠️  Error fetching news: {e}")
            return []
    
    def _get_cached_news(self, query):
        """Get news from cache if fresh"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            if query in cache:
                cached_data = cache[query]
                cache_time = datetime.fromisoformat(cached_data['timestamp'])
                
                # Check if cache is still fresh
                if datetime.now() - cache_time < timedelta(hours=self.cache_duration_hours):
                    return cached_data['articles']
            
            return None
        except Exception as e:
            return None
    
    def _cache_news(self, query, articles):
        """Cache news articles"""
        try:
            # Create data directory if doesn't exist
            os.makedirs('data', exist_ok=True)
            
            # Load existing cache
            cache = {}
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
            
            # Add new data
            cache[query] = {
                'timestamp': datetime.now().isoformat(),
                'articles': articles
            }
            
            # Save cache
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            pass  # Fail silently if caching fails
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text (-1 to +1)"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0
    
    def get_market_sentiment(self):
        """Get overall Indian market sentiment"""
        queries = [
            'India stock market',
            'Nifty Sensex',
            'Indian economy',
            'RBI policy',
            'India inflation'
        ]
        
        all_sentiments = []
        
        for query in queries:
            articles = self.fetch_news(query, days=1)
            for article in articles[:5]:  # Top 5 articles per query
                title = article.get('title', '')
                description = article.get('description', '')
                text = f"{title} {description}"
                sentiment = self.analyze_sentiment(text)
                all_sentiments.append(sentiment)
        
        if all_sentiments:
            avg_sentiment = sum(all_sentiments) / len(all_sentiments)
            return {
                'sentiment_score': avg_sentiment,
                'sentiment': self._classify_sentiment(avg_sentiment),
                'article_count': len(all_sentiments)
            }
        
        return {'sentiment_score': 0, 'sentiment': 'NEUTRAL', 'article_count': 0}
    
    def get_stock_sentiment(self, company_name):
        """Get sentiment for specific stock"""
        articles = self.fetch_news(f"{company_name} India stock", days=2)
        
        sentiments = []
        for article in articles[:10]:
            title = article.get('title', '')
            description = article.get('description', '')
            text = f"{title} {description}"
            sentiment = self.analyze_sentiment(text)
            sentiments.append(sentiment)
        
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            return {
                'sentiment_score': avg_sentiment,
                'sentiment': self._classify_sentiment(avg_sentiment)
            }
        
        return {'sentiment_score': 0, 'sentiment': 'NEUTRAL'}
    
    def _classify_sentiment(self, score):
        """Classify sentiment score"""
        if score > 0.2:
            return 'POSITIVE'
        elif score < -0.2:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
    
    def get_global_market_impact(self):
        """Check global market news impact"""
        queries = [
            'US stock market',
            'Federal Reserve',
            'China economy',
            'crude oil prices',
            'global recession'
        ]
        
        sentiments = []
        for query in queries:
            articles = self.fetch_news(query, days=1)
            for article in articles[:3]:
                text = f"{article.get('title', '')} {article.get('description', '')}"
                sentiments.append(self.analyze_sentiment(text))
        
        if sentiments:
            return sum(sentiments) / len(sentiments)
        return 0
