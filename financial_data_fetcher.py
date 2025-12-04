"""
Practical Example: Financial Data Fetcher with Rate Limiting
Ready to use in your Rota-v1 application
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from rate_limiter import RateLimitedAPIClient, DataCache, APICallTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialDataFetcher:
    """
    Complete financial data fetching system with:
    - Rate limiting for all APIs
    - Intelligent caching
    - Multi-source fallback
    - Error handling and retries
    """
    
    def __init__(self):
        """Initialize all API clients"""
        self.clients = {
            'finnhub': RateLimitedAPIClient.get_client('finnhub'),
            'yfinance': RateLimitedAPIClient.get_client('yfinance'),
            'alpha_vantage': RateLimitedAPIClient.get_client('alpha_vantage'),
            'iex_cloud': RateLimitedAPIClient.get_client('iex_cloud'),
        }
        self.cache = DataCache()
    
    # ============ STOCK QUOTE METHODS ============
    
    def get_stock_quote(self, ticker: str, source: str = 'finnhub') -> Optional[Dict]:
        """
        Get real-time stock quote with rate limiting
        
        Supported sources: finnhub, yfinance, alpha_vantage, iex_cloud
        Cache TTL: 10 minutes
        
        Example:
            >>> fetcher = FinancialDataFetcher()
            >>> quote = fetcher.get_stock_quote('AAPL')
            >>> print(f"Price: ${quote['c']}, Previous: ${quote['pc']}")
        """
        import finnhub
        import os
        
        api_key = os.environ.get('FINNHUB_API_KEY', '')
        if not api_key:
            logger.warning("FINNHUB_API_KEY not set")
            return None
            
        client = finnhub.Client(api_key=api_key)
        
        def fetch():
            return client.quote(ticker)
        
        result, success = self.clients['finnhub'].call_with_cache_and_limit(
            fetch,
            f"quote_{ticker}",
            use_cache=True
        )
        
        if success and result:
            return {
                'ticker': ticker,
                'price': result.get('c'),
                'previous_close': result.get('pc'),
                'open': result.get('o'),
                'high': result.get('h'),
                'low': result.get('l'),
                'timestamp': datetime.now().isoformat()
            }
        return None
    
    def get_multiple_quotes(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get quotes for multiple stocks efficiently
        Uses thread pooling with rate limiting
        
        Example:
            >>> quotes = fetcher.get_multiple_quotes(['AAPL', 'MSFT', 'GOOGL'])
            >>> for ticker, quote in quotes.items():
            ...     print(f"{ticker}: ${quote['price']}")
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        def fetch_single(ticker):
            return ticker, self.get_stock_quote(ticker)
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fetch_single, t) for t in tickers]
            
            for future in as_completed(futures):
                ticker, quote = future.result()
                results[ticker] = quote
        
        return results
    
    # ============ COMPANY INFORMATION METHODS ============
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Get company profile and information
        Cache TTL: 1 day (stable data)
        
        Example:
            >>> info = fetcher.get_company_info('AAPL')
            >>> print(f"Company: {info['name']}, Industry: {info['finnhubIndustry']}")
        """
        import finnhub
        import os
        
        api_key = os.environ.get('FINNHUB_API_KEY', '')
        if not api_key:
            logger.warning("FINNHUB_API_KEY not set")
            return None
            
        client = finnhub.Client(api_key=api_key)
        
        def fetch():
            return client.company_profile2(symbol=ticker)
        
        result, success = self.clients['finnhub'].call_with_cache_and_limit(
            fetch,
            f"company_{ticker}",
            use_cache=True,
            ttl_override=1440  # 1 day cache for stable data
        )
        
        if success and result:
            return {
                'ticker': ticker,
                'name': result.get('name'),
                'industry': result.get('finnhubIndustry'),
                'market_cap': result.get('marketCapitalization'),
                'website': result.get('weburl'),
                'description': result.get('description', '')[:500],
                'ipo': result.get('ipo'),
                'employees': result.get('employeeTotal')
            }
        return None
    
    # ============ DIVIDEND METHODS ============
    
    def get_dividend_info(self, ticker: str) -> Optional[Dict]:
        """
        Get dividend information and history
        Cache TTL: 15 minutes
        Perfect for Turkish dividend stocks!
        
        Example:
            >>> divs = fetcher.get_dividend_info('GARAN.IS')
            >>> print(f"Annual Yield: {divs['yield']}")
            >>> print(f"Last Dividend: {divs['last_dividend_date']}")
        """
        import yfinance as yf
        
        def fetch():
            tick = yf.Ticker(ticker)
            info = tick.info
            
            return {
                'ticker': ticker,
                'dividend_yield': info.get('dividendYield'),
                'dividend_rate': info.get('dividendRate'),
                'last_dividend_value': info.get('lastDividendValue'),
                'last_dividend_date': info.get('lastDividendDate'),
                'trailing_annual_dividend_rate': info.get('trailingAnnualDividendRate'),
                'trailing_annual_dividend_yield': info.get('trailingAnnualDividendYield'),
                'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield'),
                'payout_ratio': info.get('payoutRatio'),
            }
        
        result, success = self.clients['yfinance'].call_with_cache_and_limit(
            fetch,
            f"dividend_{ticker}",
            use_cache=True
        )
        
        return result if success else None
    
    def get_dividend_history(self, ticker: str, years: int = 5) -> Optional[Dict]:
        """
        Get detailed dividend payment history
        
        Example:
            >>> history = fetcher.get_dividend_history('KCHOL.IS')
            >>> for date, value in history['payments'].items():
            ...     print(f"{date}: {value}")
        """
        import yfinance as yf
        
        def fetch():
            tick = yf.Ticker(ticker)
            divs = tick.dividends
            return {
                'ticker': ticker,
                'payments': {str(date): float(value) for date, value in divs.items()},
                'total_payments': len(divs),
                'average_payment': float(divs.mean()) if len(divs) > 0 else 0,
            }
        
        result, success = self.clients['yfinance'].call_with_cache_and_limit(
            fetch,
            f"div_history_{ticker}",
            use_cache=True,
            ttl_override=60  # Cache for 1 hour
        )
        
        return result if success else None
    
    # ============ FINANCIAL STATEMENTS ============
    
    def get_key_metrics(self, ticker: str) -> Optional[Dict]:
        """
        Get key financial metrics
        Cache TTL: 1 day
        
        Example:
            >>> metrics = fetcher.get_key_metrics('ASELS.IS')
            >>> print(f"P/E Ratio: {metrics['pe_ratio']}")
            >>> print(f"Debt/Equity: {metrics['debt_to_equity']}")
        """
        import yfinance as yf
        
        def fetch():
            tick = yf.Ticker(ticker)
            info = tick.info
            
            return {
                'ticker': ticker,
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'roa': info.get('returnOnAssets'),
                'roe': info.get('returnOnEquity'),
                'gross_margin': info.get('grossMargins'),
                'operating_margin': info.get('operatingMargins'),
                'profit_margin': info.get('profitMargins'),
                'book_value': info.get('bookValue'),
                'earnings_per_share': info.get('trailingEps'),
            }
        
        result, success = self.clients['yfinance'].call_with_cache_and_limit(
            fetch,
            f"metrics_{ticker}",
            use_cache=True,
            ttl_override=1440  # Cache for 1 day
        )
        
        return result if success else None
    
    # ============ TECHNICAL ANALYSIS ============
    
    def get_moving_averages(self, ticker: str, periods: List[int] = None) -> Optional[Dict]:
        """
        Calculate moving averages
        
        Example:
            >>> ma = fetcher.get_moving_averages('AAPL', [20, 50])
            >>> print(f"20-day MA: {ma['20']}, 50-day MA: {ma['50']}")
        """
        import yfinance as yf
        import pandas as pd
        
        if periods is None:
            periods = [20, 50, 200]
        
        def fetch():
            tick = yf.Ticker(ticker)
            hist = tick.history(period='1y')
            
            mas = {}
            for period in periods:
                ma = hist['Close'].rolling(window=period).mean().iloc[-1]
                mas[str(period)] = round(float(ma), 2) if pd.notna(ma) else None
            
            return {
                'ticker': ticker,
                'moving_averages': mas,
                'current_price': round(float(hist['Close'].iloc[-1]), 2),
                'last_date': str(hist.index[-1].date())
            }
        
        result, success = self.clients['yfinance'].call_with_cache_and_limit(
            fetch,
            f"ma_{ticker}",
            use_cache=True
        )
        
        return result if success else None
    
    def get_volatility(self, ticker: str, period: int = 30) -> Optional[Dict]:
        """
        Calculate volatility metrics
        
        Example:
            >>> vol = fetcher.get_volatility('GARAN.IS')
            >>> print(f"30-day volatility: {vol['volatility']:.2%}")
        """
        import yfinance as yf
        
        def fetch():
            tick = yf.Ticker(ticker)
            hist = tick.history(period='3mo')
            
            returns = hist['Close'].pct_change().dropna()
            daily_vol = returns.std()
            annualized_vol = daily_vol * (252 ** 0.5)  # Annualized
            
            return {
                'ticker': ticker,
                'daily_volatility': round(float(daily_vol), 4),
                'annualized_volatility': round(float(annualized_vol), 4),
                'period_days': period
            }
        
        result, success = self.clients['yfinance'].call_with_cache_and_limit(
            fetch,
            f"volatility_{ticker}",
            use_cache=True
        )
        
        return result if success else None
    
    # ============ ECONOMIC DATA ============
    
    def get_economic_calendar(self, country: str = 'TR') -> Optional[List[Dict]]:
        """
        Get economic calendar events
        
        Example:
            >>> events = fetcher.get_economic_calendar('TR')
            >>> for event in events[:5]:
            ...     print(f"{event['date']}: {event['event']}")
        """
        import finnhub
        import os
        from datetime import timedelta
        
        api_key = os.environ.get('FINNHUB_API_KEY', '')
        if not api_key:
            logger.warning("FINNHUB_API_KEY not set")
            return None
            
        client = finnhub.Client(api_key=api_key)
        
        def fetch():
            today = datetime.now()
            from_date = today.strftime('%Y-%m-%d')
            to_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')
            return client.economic_calendar(_from=from_date, to=to_date)
        
        result, success = self.clients['finnhub'].call_with_cache_and_limit(
            fetch,
            f"economic_calendar_{country}",
            use_cache=True,
            ttl_override=60  # Cache for 1 hour
        )
        
        if success and result:
            events = result.get('economicCalendar', [])
            return [
                {
                    'country': event.get('country'),
                    'event': event.get('event'),
                    'date': event.get('time'),
                    'actual': event.get('actual'),
                    'estimate': event.get('estimate'),
                    'previous': event.get('prev'),
                    'impact': event.get('impact'),
                }
                for event in events if event.get('country') == country
            ]
        return None
    
    # ============ TURKISH STOCK HELPERS ============
    
    def get_turkish_stock(self, ticker: str) -> Optional[Dict]:
        """
        Get Turkish stock data (BIST)
        Automatically adds .IS suffix if needed
        
        Example:
            >>> stock = fetcher.get_turkish_stock('GARAN')
            >>> print(f"Price: {stock['price']} TRY")
        """
        import yfinance as yf
        
        # Add .IS suffix for Istanbul Stock Exchange
        if not ticker.endswith('.IS'):
            ticker = f"{ticker}.IS"
        
        def fetch():
            tick = yf.Ticker(ticker)
            info = tick.info
            hist = tick.history(period='1d')
            
            return {
                'ticker': ticker,
                'name': info.get('shortName', info.get('longName', '')),
                'price': round(float(hist['Close'].iloc[-1]), 2) if not hist.empty else None,
                'change_percent': round(info.get('regularMarketChangePercent', 0), 2),
                'volume': int(hist['Volume'].iloc[-1]) if not hist.empty else 0,
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'currency': 'TRY'
            }
        
        result, success = self.clients['yfinance'].call_with_cache_and_limit(
            fetch,
            f"turkish_{ticker}",
            use_cache=True
        )
        
        return result if success else None
    
    def get_turkish_stocks_batch(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get multiple Turkish stocks efficiently
        
        Example:
            >>> stocks = fetcher.get_turkish_stocks_batch(['GARAN', 'ASELS', 'KCHOL'])
            >>> for ticker, data in stocks.items():
            ...     print(f"{ticker}: {data['price']} TRY")
        """
        results = {}
        for ticker in tickers:
            results[ticker] = self.get_turkish_stock(ticker)
        return results
    
    # ============ UTILITY METHODS ============
    
    def get_all_stats(self) -> Dict:
        """Get comprehensive statistics about API usage"""
        stats = {}
        for source, client in self.clients.items():
            stats[source] = client.get_stats()
        return stats
    
    def print_stats(self):
        """Print formatted API usage statistics"""
        stats = self.get_all_stats()
        
        print("\n" + "=" * 60)
        print("API USAGE & PERFORMANCE REPORT")
        print("=" * 60)
        print(f"Generated: {datetime.now().isoformat()}\n")
        
        for source, stat in stats.items():
            api_stats = stat.get('api_stats', {})
            print(f"\n{source.upper()}")
            print("-" * 40)
            print(f"  Total Calls:    {api_stats.get('total_calls', 0)}")
            print(f"  Successful:     {api_stats.get('success', 0)}")
            print(f"  Cache Hits:     {api_stats.get('cache_hits', 0)}")
            print(f"  Rate Limited:   {api_stats.get('rate_limited', 0)}")
            print(f"  Success Rate:   {api_stats.get('success_rate', 0):.1f}%")
        
        print("\n" + "=" * 60)
    
    def export_stats(self, filename: str = 'api_stats.json'):
        """Export statistics to JSON file"""
        stats = self.get_all_stats()
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        logger.info(f"Statistics exported to {filename}")
    
    def clear_cache(self):
        """Clear expired cache entries"""
        deleted = self.cache.clear_expired()
        logger.info(f"Cleared {deleted} expired cache entries")
        return deleted


# ============ EXAMPLE USAGE ============

if __name__ == '__main__':
    # Initialize fetcher
    fetcher = FinancialDataFetcher()
    
    print("\n" + "=" * 60)
    print("Financial Data Fetcher with Rate Limiting")
    print("=" * 60)
    
    # Example 1: Turkish dividend stocks
    print("\n1. Turkish Dividend Stocks:")
    turkish_stocks = ['GARAN', 'ASELS', 'KCHOL', 'AKBNK']
    for ticker in turkish_stocks:
        data = fetcher.get_turkish_stock(ticker)
        if data:
            print(f"   {data['ticker']}: {data['price']} TRY "
                  f"(Yield: {data.get('dividend_yield', 'N/A')})")
    
    # Example 2: Dividend info
    print("\n2. Dividend Information:")
    divs = fetcher.get_dividend_info('GARAN.IS')
    if divs:
        print(f"   Yield: {divs.get('dividend_yield', 'N/A')}")
        print(f"   Rate: {divs.get('dividend_rate', 'N/A')}")
    
    # Example 3: Key metrics
    print("\n3. Key Metrics (ASELS.IS):")
    metrics = fetcher.get_key_metrics('ASELS.IS')
    if metrics:
        print(f"   P/E Ratio: {metrics.get('pe_ratio', 'N/A')}")
        print(f"   ROE: {metrics.get('roe', 'N/A')}")
    
    # Example 4: Technical analysis
    print("\n4. Moving Averages (GARAN.IS):")
    ma = fetcher.get_moving_averages('GARAN.IS')
    if ma:
        print(f"   Current: {ma['current_price']}")
        print(f"   MA-20: {ma['moving_averages'].get('20')}")
        print(f"   MA-50: {ma['moving_averages'].get('50')}")
    
    # Print API usage statistics
    fetcher.print_stats()
