"""
Main Orchestrator for Google Antigravity
Coordinates all modules and generates comprehensive market reports.
"""

import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import Dict, Any, List

# Load environment variables from .env file
load_dotenv()

# Import all modules
from news_aggregator import NewsAggregator
from llm_analysis import LLMAnalyzer
from price_integrator import PriceIntegrator
from ticker_screener import TickerScreener
from sentiment_analyzer import SentimentAnalyzer
from sector_backtest import SectorBacktest
from economic_calendar import EconomicCalendar
from macro_regime_detector import MacroRegimeDetector
from geopolitical_monitor import GeopoliticalMonitor
from portfolio_analyzer import PortfolioAnalyzer
from alert_engine import AlertEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AntigravityOrchestrator:
    """Main orchestrator for the Antigravity financial intelligence system."""
    
    def __init__(self):
        logger.info("Initializing Antigravity Orchestrator...")
        
        # Initialize all modules
        self.news_aggregator = NewsAggregator()
        self.llm_analyzer = LLMAnalyzer()
        self.price_integrator = PriceIntegrator()
        self.ticker_screener = TickerScreener()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.sector_backtest = SectorBacktest()
        self.economic_calendar = EconomicCalendar()
        self.macro_regime_detector = MacroRegimeDetector()
        self.geopolitical_monitor = GeopoliticalMonitor()
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.alert_engine = AlertEngine()
        
        logger.info("All modules initialized successfully.")
    
    def generate_morning_report(self) -> Dict[str, Any]:
        """Generate comprehensive morning market report."""
        logger.info("Generating morning report...")
        
        report = {
            'report_type': 'morning_brief',
            'timestamp': datetime.now().isoformat(),
            'sections': {}
        }
        
        # 1. Get latest news
        logger.info("Fetching news...")
        news = self.news_aggregator.aggregate_all_news(hours_back=12)
        all_articles = news['rss'] + news['finnhub'] + news['turkish']
        report['sections']['news_count'] = len(all_articles)
        
        # 2. Sentiment analysis
        logger.info("Analyzing sentiment...")
        sentiment = self.sentiment_analyzer.aggregate_sentiment(all_articles[:50])
        report['sections']['sentiment'] = sentiment
        
        # 3. Get market prices
        logger.info("Fetching market prices...")
        indices = {
            'SP500': self.price_integrator.get_index_data('SP500'),
            'NASDAQ': self.price_integrator.get_index_data('NASDAQ'),
            'BIST100': self.price_integrator.get_index_data('BIST100')
        }
        report['sections']['indices'] = indices
        
        # 4. Turkish stocks
        turkish_stocks = self.ticker_screener.screen_turkish_dividend_stocks()
        report['sections']['turkish_stocks'] = turkish_stocks[:5]  # Top 5
        
        # 5. Economic calendar
        upcoming_events = self.economic_calendar.get_upcoming_events(days_ahead=7)
        report['sections']['upcoming_events'] = upcoming_events[:5]
        
        # 6. Macro regime
        economic_data = {
            'gdp_growth': 2.5,  # Would fetch from API
            'inflation_rate': 3.2,
            'unemployment': 4.2
        }
        regime = self.macro_regime_detector.detect_regime(economic_data)
        report['sections']['macro_regime'] = regime
        
        # 7. Generate LLM summary
        logger.info("Generating LLM analysis...")
        market_summary = self.llm_analyzer.generate_market_summary(
            all_articles[:10],
            {'indices': indices, 'sentiment': sentiment}
        )
        report['sections']['executive_summary'] = market_summary
        
        # 8. Check for alerts
        alerts = []
        
        # Check sentiment alerts
        sentiment_alert = self.alert_engine.check_sentiment_alert(
            sentiment['overall_sentiment'],
            sentiment['confidence'],
            sentiment['average_compound']
        )
        if sentiment_alert:
            alerts.append(sentiment_alert)
        
        # Check calendar alerts
        for event in upcoming_events[:3]:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")
            days_until = (event_date - datetime.now()).days
            alert = self.alert_engine.check_economic_calendar_alert(event, days_until)
            if alert:
                alerts.append(alert)
        
        report['sections']['alerts'] = alerts
        
        logger.info("Morning report generated successfully.")
        return report
    
    def generate_midday_update(self) -> Dict[str, Any]:
        """Generate midday market update."""
        logger.info("Generating midday update...")
        
        return {
            'report_type': 'midday_update',
            'timestamp': datetime.now().isoformat(),
            'message': 'Midday update - monitoring market conditions'
        }
    
    def generate_evening_wrap(self) -> Dict[str, Any]:
        """Generate evening market wrap."""
        logger.info("Generating evening wrap...")
        
        report = {
            'report_type': 'evening_wrap',
            'timestamp': datetime.now().isoformat(),
            'sections': {}
        }
        
        # Daily movers
        movers = self.ticker_screener.get_daily_movers()
        report['sections']['daily_movers'] = movers
        
        # Sector performance
        # (Would integrate with actual data)
        
        return report
    
    def format_report_text(self, report: Dict[str, Any]) -> str:
        """Format report as human-readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"GOOGLE ANTIGRAVITY - {report['report_type'].upper()}")
        lines.append(f"Generated: {report['timestamp']}")
        lines.append("=" * 80)
        lines.append("")
        
        sections = report.get('sections', {})
        
        # Executive Summary
        if 'executive_summary' in sections:
            lines.append("EXECUTIVE SUMMARY")
            lines.append("-" * 80)
            lines.append(sections['executive_summary'])
            lines.append("")
        
        # Market Sentiment
        if 'sentiment' in sections:
            sent = sections['sentiment']
            lines.append("MARKET SENTIMENT")
            lines.append("-" * 80)
            lines.append(f"Overall: {sent['overall_sentiment'].upper()} (Score: {sent['average_compound']:.2f})")
            lines.append(f"Distribution: {sent['sentiment_distribution']}")
            lines.append(f"Confidence: {sent['confidence'].upper()}")
            lines.append("")
        
        # Macro Regime
        if 'macro_regime' in sections:
            regime = sections['macro_regime']
            lines.append("MACRO REGIME")
            lines.append("-" * 80)
            lines.append(f"Current Regime: {regime['regime'].upper()}")
            lines.append(f"Description: {regime['description']}")
            lines.append(f"Best Assets: {', '.join(regime['best_assets'])}")
            lines.append("")
        
        # Alerts
        if 'alerts' in sections and sections['alerts']:
            lines.append("ALERTS")
            lines.append("-" * 80)
            for alert in sections['alerts']:
                lines.append(f"[{alert['severity_name']}] {alert['message']}")
            lines.append("")
        
        # Turkish Stocks
        if 'turkish_stocks' in sections:
            lines.append("TOP TURKISH DIVIDEND STOCKS")
            lines.append("-" * 80)
            for stock in sections['turkish_stocks'][:5]:
                lines.append(f"{stock['ticker']}: ${stock.get('price', 'N/A')}")
            lines.append("")
        
        # Upcoming Events
        if 'upcoming_events' in sections:
            lines.append("UPCOMING ECONOMIC EVENTS")
            lines.append("-" * 80)
            for event in sections['upcoming_events'][:5]:
                lines.append(f"{event['date']}: {event['event']} [{event['country']}]")
            lines.append("")
        
        lines.append("=" * 80)
        lines.append("End of Report")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def run_scheduled_job(self, job_type: str) -> None:
        """Run scheduled job based on type."""
        logger.info(f"Running scheduled job: {job_type}")
        
        if job_type == 'morning':
            report = self.generate_morning_report()
        elif job_type == 'midday':
            report = self.generate_midday_update()
        elif job_type == 'evening':
            report = self.generate_evening_wrap()
        else:
            logger.error(f"Unknown job type: {job_type}")
            return
        
        # Format and output
        text_report = self.format_report_text(report)
        print(text_report)
        
        # Would also send to Slack/Email/Firestore here
        logger.info(f"Job {job_type} completed successfully.")


def main():
    """Main entry point."""
    import sys
    
    orchestrator = AntigravityOrchestrator()
    
    # Get job type from command line args
    job_type = sys.argv[1] if len(sys.argv) > 1 else 'morning'
    
    orchestrator.run_scheduled_job(job_type)


if __name__ == "__main__":
    main()
