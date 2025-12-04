"""
News Aggregator Module
Aggregates financial news from multiple sources including RSS feeds, APIs, and web scraping.
Now with rate limiting support for API calls.
"""

import os
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Import rate limiter
from rate_limiter import RateLimitedAPIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsAggregator:
    """Aggregates financial news from multiple sources with rate limiting."""
    
    def __init__(self):
        self.finnhub_api_key = os.environ.get('FINNHUB_API_KEY')
        self.sources = {
            'rss_feeds': [
                'https://feeds.bloomberg.com/markets/news.rss',
                'https://www.reuters.com/rssfeed/businessNews',
                'https://seekingalpha.com/feed.xml',
            ],
            'news_apis': ['finnhub']
        }
        
        # Initialize rate-limited client for Finnhub
        self.finnhub_client = RateLimitedAPIClient.get_client('finnhub')
        
    def fetch_rss_news(self, feed_url: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Fetch news from RSS feed."""
        try:
            feed = feedparser.parse(feed_url)
            articles = []
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            for entry in feed.entries[:20]:  # Limit to 20 most recent
                published = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                
                if published >= cutoff_time:
                    articles.append({
                        'title': entry.title,
                        'summary': entry.get('summary', ''),
                        'link': entry.link,
                        'published': published.isoformat(),
                        'source': feed_url
                    })
            
            return articles
        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []
    
    def fetch_finnhub_news(self, category: str = 'general', hours_back: int = 24) -> List[Dict[str, Any]]:
        """Fetch market news from Finnhub API with rate limiting and caching."""
        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not set")
            return []
        
        def fetch():
            url = f"https://finnhub.io/api/v1/news"
            params = {
                'category': category,
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            articles = []
            cutoff_timestamp = (datetime.now() - timedelta(hours=hours_back)).timestamp()
            
            for item in response.json():
                if item.get('datetime', 0) >= cutoff_timestamp:
                    articles.append({
                        'title': item.get('headline', ''),
                        'summary': item.get('summary', ''),
                        'link': item.get('url', ''),
                        'published': datetime.fromtimestamp(item['datetime']).isoformat(),
                        'source': 'finnhub',
                        'category': item.get('category', ''),
                        'image': item.get('image', '')
                    })
            
            return articles
        
        result, success = self.finnhub_client.call_with_cache_and_limit(
            fetch,
            f"finnhub_news_{category}_{hours_back}h",
            use_cache=True,
            ttl_override=30  # News cache for 30 minutes
        )
        return result if success and result else []
    
    def fetch_turkish_market_news(self) -> List[Dict[str, Any]]:
        """Fetch news specific to Turkish markets (BIST)."""
        # This is a placeholder - would integrate with Turkish news sources
        logger.info("Fetching Turkish market news...")
        return []
    
    def aggregate_all_news(self, hours_back: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregate news from all configured sources."""
        all_news = {
            'rss': [],
            'finnhub': [],
            'turkish': []
        }
        
        # Fetch from RSS feeds
        for feed_url in self.sources['rss_feeds']:
            articles = self.fetch_rss_news(feed_url, hours_back)
            all_news['rss'].extend(articles)
        
        # Fetch from Finnhub
        all_news['finnhub'] = self.fetch_finnhub_news('general', hours_back)
        
        # Fetch Turkish market news
        all_news['turkish'] = self.fetch_turkish_market_news()
        
        total_articles = sum(len(v) for v in all_news.values())
        logger.info(f"Aggregated {total_articles} articles from all sources")
        
        return all_news
    
    def filter_by_keywords(self, articles: List[Dict[str, Any]], keywords: List[str]) -> List[Dict[str, Any]]:
        """Filter articles by keywords."""
        filtered = []
        keywords_lower = [k.lower() for k in keywords]
        
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            if any(keyword in text for keyword in keywords_lower):
                filtered.append(article)
        
        return filtered


if __name__ == "__main__":
    aggregator = NewsAggregator()
    news = aggregator.aggregate_all_news(hours_back=12)
    print(f"Total articles: {sum(len(v) for v in news.values())}")
