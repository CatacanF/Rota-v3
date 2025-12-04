"""
Price Integrator Module
Fetches and normalizes market price data from multiple sources.
Now with enhanced rate limiting and caching via RateLimitedAPIClient.
"""

import os
import time
import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Import rate limiter
from rate_limiter import RateLimitedAPIClient, rate_limited_api_call

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceIntegrator:
    """Integrates market price data from multiple sources with rate limiting."""
    
    def __init__(self):
        self.finnhub_api_key = os.environ.get('FINNHUB_API_KEY')
        self.alpha_vantage_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
        
        # Initialize rate-limited clients
        self.yahoo_client = RateLimitedAPIClient.get_client('yfinance')
        self.finnhub_client = RateLimitedAPIClient.get_client('finnhub')
        
    def get_stock_price(self, ticker: str, source: str = 'yahoo') -> Optional[Dict[str, Any]]:
        """Get current stock price and basic info with automatic fallback."""
        # Try primary source
        if source == 'yahoo':
            price_data = self._get_yahoo_price(ticker)
            # If Yahoo fails (rate limit or other error), fallback to Finnhub
            if price_data is None and self.finnhub_api_key:
                logger.info(f"Yahoo failed for {ticker}, falling back to Finnhub")
                price_data = self._get_finnhub_price(ticker)
            return price_data
        elif source == 'finnhub':
            return self._get_finnhub_price(ticker)
        else:
            logger.warning(f"Unknown source: {source}")
            return None
    
    def _get_yahoo_price(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch price data from Yahoo Finance with rate limiting and caching."""
        def fetch():
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period='1d')
            
            if hist.empty:
                logger.warning(f"No historical data for {ticker} from Yahoo")
                return None
            
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            
            return {
                'ticker': ticker,
                'price': round(float(current_price), 2),
                'previous_close': round(float(previous_close), 2),
                'change': round(float(current_price - previous_close), 2),
                'change_percent': round(((current_price - previous_close) / previous_close) * 100, 2) if previous_close != 0 else 0,
                'volume': int(hist['Volume'].iloc[-1]) if not hist.empty else 0,
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'source': 'yahoo',
                'timestamp': datetime.now().isoformat()
            }
        
        result, success = self.yahoo_client.call_with_cache_and_limit(
            fetch,
            f"yahoo_price_{ticker}",
            use_cache=True
        )
        return result if success else None
    
    def _get_finnhub_price(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch price data from Finnhub with rate limiting and caching."""
        if not self.finnhub_api_key:
            logger.warning("Finnhub API key not set")
            return None
        
        def fetch():
            url = f"https://finnhub.io/api/v1/quote"
            params = {'symbol': ticker, 'token': self.finnhub_api_key}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current_price = data.get('c', 0)
            previous_close = data.get('pc', current_price)
            
            return {
                'ticker': ticker,
                'price': round(float(current_price), 2),
                'previous_close': round(float(previous_close), 2),
                'change': round(float(data.get('d', 0)), 2),
                'change_percent': round(float(data.get('dp', 0)), 2),
                'high': round(float(data.get('h', 0)), 2),
                'low': round(float(data.get('l', 0)), 2),
                'open': round(float(data.get('o', 0)), 2),
                'source': 'finnhub',
                'timestamp': datetime.now().isoformat()
            }
        
        result, success = self.finnhub_client.call_with_cache_and_limit(
            fetch,
            f"finnhub_price_{ticker}",
            use_cache=True
        )
        return result if success else None
    
    def get_batch_prices(self, tickers: List[str], source: str = 'yahoo') -> Dict[str, Dict[str, Any]]:
        """Fetch prices for multiple tickers with automatic rate limiting."""
        prices = {}
        for ticker in tickers:
            # Rate limiting is now handled automatically by RateLimitedAPIClient
            price_data = self.get_stock_price(ticker, source)
            if price_data:
                prices[ticker] = price_data
        
        logger.info(f"✅ Fetched prices for {len(prices)}/{len(tickers)} tickers")
        return prices
    
    def get_turkish_stocks(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get prices for Turkish stocks (BIST)."""
        # Add .IS suffix for Istanbul Stock Exchange
        turkish_tickers = [f"{ticker}.IS" for ticker in tickers]
        prices = self.get_batch_prices(turkish_tickers, source='yahoo')
        
        # Remove .IS suffix from keys for cleaner output
        return {k.replace('.IS', ''): v for k, v in prices.items()}
    
    def get_index_data(self, index_symbol: str) -> Optional[Dict[str, Any]]:
        """Get index data (S&P 500, BIST 100, etc.)."""
        index_map = {
            'SP500': '^GSPC',
            'NASDAQ': '^IXIC',
            'DOW': '^DJI',
            'BIST100': 'XU100.IS',
            'BIST30': 'XU030.IS'
        }
        
        ticker = index_map.get(index_symbol, index_symbol)
        return self.get_stock_price(ticker, source='yahoo')
    
    def get_forex_rate(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get forex exchange rate (e.g., 'USDTRY', 'EURUSD')."""
        forex_ticker = f"{pair}=X"
        return self.get_stock_price(forex_ticker, source='yahoo')
    
    def get_commodity_price(self, commodity: str) -> Optional[Dict[str, Any]]:
        """Get commodity prices (Gold, Oil, etc.)."""
        commodity_map = {
            'GOLD': 'GC=F',
            'SILVER': 'SI=F',
            'OIL': 'CL=F',
            'BRENT': 'BZ=F',
            'NATGAS': 'NG=F'
        }
        
        ticker = commodity_map.get(commodity.upper(), commodity)
        return self.get_stock_price(ticker, source='yahoo')
    
    def get_historical_data(self, ticker: str, period: str = '1mo') -> Optional[Dict[str, Any]]:
        """Get historical price data."""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return None
            
            return {
                'ticker': ticker,
                'period': period,
                'data': hist.to_dict('records'),
                'summary': {
                    'high': round(float(hist['High'].max()), 2),
                    'low': round(float(hist['Low'].min()), 2),
                    'avg_volume': int(hist['Volume'].mean()),
                    'volatility': round(float(hist['Close'].pct_change().std() * 100), 2)
                }
            }
        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {e}")
            return None


if __name__ == "__main__":
    integrator = PriceIntegrator()
    
    # Test with a few tickers
    price = integrator.get_stock_price('AAPL')
    print(f"AAPL: ${price['price']}" if price else "Failed to fetch")
    
    # Test Turkish stocks
    turkish_stocks = integrator.get_turkish_stocks(['EREGL', 'FROTO', 'TUPRS'])
    print(f"Turkish stocks: {len(turkish_stocks)} fetched")
