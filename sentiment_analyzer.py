"""
Sentiment Analyzer Module
Analyzes market sentiment from news and social media.
"""

from typing import List, Dict, Any
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment from text data."""
    
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze_text_vader(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using VADER (better for social media/news)."""
        scores = self.vader.polarity_scores(text)
        
        # Determine overall sentiment
        compound = scores['compound']
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'compound': round(compound, 3),
            'positive': round(scores['pos'], 3),
            'negative': round(scores['neg'], 3),
            'neutral': round(scores['neu'], 3),
            'method': 'vader'
        }
    
    def analyze_text_textblob(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob."""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'polarity': round(polarity, 3),
            'subjectivity': round(subjectivity, 3),
            'method': 'textblob'
        }
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of a news article."""
        title = article.get('title', '')
        summary = article.get('summary', '')
        text = f"{title}. {summary}"
        
        # Use VADER for news sentiment
        sentiment_data = self.analyze_text_vader(text)
        
        return {
            **article,
            'sentiment_analysis': sentiment_data
        }
    
    def analyze_article_batch(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment for multiple articles."""
        analyzed = []
        for article in articles:
            analyzed.append(self.analyze_article(article))
        
        logger.info(f"Analyzed sentiment for {len(analyzed)} articles")
        return analyzed
    
    def aggregate_sentiment(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate sentiment across multiple articles."""
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'average_compound': 0.0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        analyzed = self.analyze_article_batch(articles)
        
        compounds = []
        distribution = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in analyzed:
            sentiment_data = article.get('sentiment_analysis', {})
            compound = sentiment_data.get('compound', 0)
            sentiment = sentiment_data.get('sentiment', 'neutral')
            
            compounds.append(compound)
            distribution[sentiment] = distribution.get(sentiment, 0) + 1
        
        avg_compound = sum(compounds) / len(compounds) if compounds else 0
        
        # Determine overall sentiment
        if avg_compound >= 0.05:
            overall = 'positive'
        elif avg_compound <= -0.05:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'average_compound': round(avg_compound, 3),
            'sentiment_distribution': distribution,
            'total_articles': len(articles),
            'confidence': self._calculate_confidence(distribution, len(articles))
        }
    
    def _calculate_confidence(self, distribution: Dict[str, int], total: int) -> str:
        """Calculate confidence level based on sentiment distribution."""
        if total == 0:
            return 'low'
        
        max_count = max(distribution.values())
        percentage = (max_count / total) * 100
        
        if percentage >= 70:
            return 'high'
        elif percentage >= 50:
            return 'medium'
        else:
            return 'low'
    
    def analyze_by_topic(self, articles: List[Dict[str, Any]], keywords: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
        """Analyze sentiment by topic/keyword groups."""
        topic_sentiments = {}
        
        for topic, keyword_list in keywords.items():
            topic_articles = []
            
            for article in articles:
                text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
                if any(keyword.lower() in text for keyword in keyword_list):
                    topic_articles.append(article)
            
            if topic_articles:
                topic_sentiments[topic] = self.aggregate_sentiment(topic_articles)
            else:
                topic_sentiments[topic] = {
                    'overall_sentiment': 'neutral',
                    'average_compound': 0.0,
                    'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                    'total_articles': 0
                }
        
        return topic_sentiments
    
    def get_sentiment_summary(self, articles: List[Dict[str, Any]]) -> str:
        """Get human-readable sentiment summary."""
        agg = self.aggregate_sentiment(articles)
        sentiment = agg['overall_sentiment']
        compound = agg['average_compound']
        distribution = agg['sentiment_distribution']
        
        summary = f"Market sentiment is {sentiment.upper()} "
        summary += f"(score: {compound:.2f}). "
        summary += f"Analysis of {agg['total_articles']} articles: "
        summary += f"{distribution['positive']} positive, "
        summary += f"{distribution['negative']} negative, "
        summary += f"{distribution['neutral']} neutral. "
        summary += f"Confidence: {agg['confidence']}."
        
        return summary


if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    
    # Test with sample article
    test_article = {
        'title': 'Stock Market Rallies on Strong Economic Data',
        'summary': 'Markets surged higher today as investors cheered better-than-expected GDP numbers.'
    }
    
    result = analyzer.analyze_article(test_article)
    print(f"Sentiment: {result['sentiment_analysis']['sentiment']}")
