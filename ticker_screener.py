"""
Ticker Screener Module
Screens stocks based on technical and fundamental criteria.
"""

from typing import List, Dict, Any, Optional
import logging
from price_integrator import PriceIntegrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TickerScreener:
    """Screens stocks based on various criteria."""
    
    def __init__(self):
        self.price_integrator = PriceIntegrator()
        
        # Turkish dividend stocks
        self.turkish_dividend_stocks = [
            'EREGL', 'FROTO', 'TUPRS', 'DOAS', 'TTRAK', 
            'ISMEN', 'ENJSA', 'SAHOL', 'PETKM', 'AKBNK'
        ]
        
        # Major US tech stocks
        self.us_tech_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 
            'NVDA', 'TSLA', 'NFLX', 'AMD', 'INTC'
        ]
    
    def screen_by_performance(self, tickers: List[str], min_change_percent: float = 2.0) -> List[Dict[str, Any]]:
        """Screen stocks by daily performance."""
        prices = self.price_integrator.get_batch_prices(tickers)
        
        winners = []
        for ticker, data in prices.items():
            if data.get('change_percent', 0) >= min_change_percent:
                winners.append(data)
        
        # Sort by change_percent descending
        winners.sort(key=lambda x: x.get('change_percent', 0), reverse=True)
        
        logger.info(f"Found {len(winners)} stocks with >{min_change_percent}% gain")
        return winners
    
    def screen_by_volume(self, tickers: List[str], min_volume_increase: float = 1.5) -> List[Dict[str, Any]]:
        """Screen stocks by unusual volume."""
        # This is a simplified version - would need historical avg volume for accurate screening
        prices = self.price_integrator.get_batch_prices(tickers)
        
        high_volume = []
        for ticker, data in prices.items():
            volume = data.get('volume', 0)
            if volume > 0:  # Placeholder logic
                high_volume.append(data)
        
        high_volume.sort(key=lambda x: x.get('volume', 0), reverse=True)
        return high_volume[:10]  # Top 10 by volume
    
    def screen_value_stocks(self, tickers: List[str]) -> List[Dict[str, Any]]:
        """Screen for value stocks (low P/E ratio)."""
        prices = self.price_integrator.get_batch_prices(tickers)
        
        value_stocks = []
        for ticker, data in prices.items():
            pe_ratio = data.get('pe_ratio')
            if pe_ratio and pe_ratio < 15:  # P/E < 15 is generally considered value
                value_stocks.append({
                    **data,
                    'screen_reason': f'Low P/E: {pe_ratio:.2f}'
                })
        
        value_stocks.sort(key=lambda x: x.get('pe_ratio', 999))
        logger.info(f"Found {len(value_stocks)} value stocks")
        return value_stocks
    
    def screen_dividend_stocks(self, tickers: List[str], min_yield: float = 0.02) -> List[Dict[str, Any]]:
        """Screen for high dividend yield stocks."""
        prices = self.price_integrator.get_batch_prices(tickers)
        
        dividend_stocks = []
        for ticker, data in prices.items():
            div_yield = data.get('dividend_yield')
            if div_yield and div_yield >= min_yield:
                dividend_stocks.append({
                    **data,
                    'screen_reason': f'Yield: {div_yield*100:.2f}%'
                })
        
        dividend_stocks.sort(key=lambda x: x.get('dividend_yield', 0), reverse=True)
        logger.info(f"Found {len(dividend_stocks)} dividend stocks with >{min_yield*100}% yield")
        return dividend_stocks
    
    def screen_turkish_dividend_stocks(self) -> List[Dict[str, Any]]:
        """Screen top Turkish dividend paying stocks."""
        turkish_prices = self.price_integrator.get_turkish_stocks(self.turkish_dividend_stocks)
        
        results = []
        for ticker, data in turkish_prices.items():
            results.append({
                **data,
                'screen_reason': 'Turkish High Dividend Stock'
            })
        
        logger.info(f"Screened {len(results)} Turkish dividend stocks")
        return results
    
    def screen_momentum_stocks(self, tickers: List[str], min_change: float = 5.0) -> List[Dict[str, Any]]:
        """Screen for momentum stocks (strong positive movement)."""
        prices = self.price_integrator.get_batch_prices(tickers)
        
        momentum_stocks = []
        for ticker, data in prices.items():
            change_pct = data.get('change_percent', 0)
            if change_pct >= min_change:
                momentum_stocks.append({
                    **data,
                    'screen_reason': f'Strong momentum: +{change_pct:.2f}%'
                })
        
        momentum_stocks.sort(key=lambda x: x.get('change_percent', 0), reverse=True)
        return momentum_stocks
    
    def get_daily_movers(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get daily top movers (gainers and losers)."""
        # Combine US tech stocks for screening
        all_tickers = self.us_tech_stocks
        prices = self.price_integrator.get_batch_prices(all_tickers)
        
        price_list = list(prices.values())
        price_list.sort(key=lambda x: x.get('change_percent', 0), reverse=True)
        
        return {
            'gainers': price_list[:5],
            'losers': price_list[-5:]
        }
    
    def comprehensive_screen(self) -> Dict[str, Any]:
        """Run comprehensive screening across multiple criteria."""
        logger.info("Running comprehensive stock screen...")
        
        results = {
            'turkish_dividend_stocks': self.screen_turkish_dividend_stocks(),
            'us_momentum_stocks': self.screen_momentum_stocks(self.us_tech_stocks, min_change=2.0),
            'daily_movers': self.get_daily_movers(),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        return results


if __name__ == "__main__":
    screener = TickerScreener()
    results = screener.comprehensive_screen()
    print(f"Turkish dividend stocks: {len(results['turkish_dividend_stocks'])}")
    print(f"US momentum stocks: {len(results['us_momentum_stocks'])}")
