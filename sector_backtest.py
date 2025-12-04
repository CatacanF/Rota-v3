"""
Sector Backtest Module
Backtests sector performance strategies and analyzes sector rotation.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SectorBacktest:
    """Analyzes and backtests sector performance."""
    
    def __init__(self):
        self.sectors = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA'],
            'Finance': ['JPM', 'BAC', 'GS', 'WFC'],
            'Healthcare': ['UNH', 'JNJ', 'PFE', 'ABBV'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB'],
            'Consumer': ['AMZN', 'WMT', 'HD', 'MCD'],
            'Industrial': ['CAT', 'BA', 'GE', 'UNP']
        }
        
        self.turkish_sectors = {
            'Banking': ['AKBNK', 'GARAN', 'ISCTR', 'YKBNK'],
            'Industrial': ['EREGL', 'KRDMD', 'ARCLK'],
            'Energy': ['TUPRS', 'PETKM', 'AKSEN'],
            'Auto': ['FROTO', 'TOASO', 'DOAS']
        }
    
    def calculate_sector_performance(self, sector_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """Calculate performance metrics for each sector."""
        sector_performance = {}
        
        for sector_name, stocks in sector_data.items():
            if not stocks:
                continue
            
            # Calculate average performance
            total_change = sum(stock.get('change_percent', 0) for stock in stocks)
            avg_change = total_change / len(stocks) if stocks else 0
            
            # Find best and worst performers
            sorted_stocks = sorted(stocks, key=lambda x: x.get('change_percent', 0), reverse=True)
            
            sector_performance[sector_name] = {
                'average_change_percent': round(avg_change, 2),
                'num_stocks': len(stocks),
                'best_performer': sorted_stocks[0] if sorted_stocks else None,
                'worst_performer': sorted_stocks[-1] if sorted_stocks else None,
                'positive_stocks': len([s for s in stocks if s.get('change_percent', 0) > 0]),
                'negative_stocks': len([s for s in stocks if s.get('change_percent', 0) < 0])
            }
        
        return sector_performance
    
    def rank_sectors(self, sector_performance: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank sectors by performance."""
        ranked = []
        
        for sector_name, metrics in sector_performance.items():
            ranked.append({
                'sector': sector_name,
                'performance': metrics['average_change_percent'],
                'breadth': f"{metrics['positive_stocks']}/{metrics['num_stocks']}",
                'metrics': metrics
            })
        
        # Sort by performance descending
        ranked.sort(key=lambda x: x['performance'], reverse=True)
        
        return ranked
    
    def identify_sector_rotation(self, ranked_sectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify potential sector rotation trends."""
        if not ranked_sectors:
            return {'rotation_signal': 'neutral', 'explanation': 'Insufficient data'}
        
        top_sectors = ranked_sectors[:2]
        bottom_sectors = ranked_sectors[-2:]
        
        # Simple rotation logic
        top_avg = sum(s['performance'] for s in top_sectors) / len(top_sectors)
        bottom_avg = sum(s['performance'] for s in bottom_sectors) / len(bottom_sectors)
        
        spread = top_avg - bottom_avg
        
        if spread > 2.0:
            rotation_signal = 'strong_rotation'
            explanation = f"Strong rotation into {', '.join([s['sector'] for s in top_sectors])}"
        elif spread > 1.0:
            rotation_signal = 'moderate_rotation'
            explanation = f"Moderate rotation favoring {top_sectors[0]['sector']}"
        else:
            rotation_signal = 'low_rotation'
            explanation = "Sectors moving in sync, low rotation activity"
        
        return {
            'rotation_signal': rotation_signal,
            'spread': round(spread, 2),
            'explanation': explanation,
            'leaders': [s['sector'] for s in top_sectors],
            'laggards': [s['sector'] for s in bottom_sectors]
        }
    
    def generate_sector_report(self, sector_performance: Dict[str, Dict[str, Any]]) -> str:
        """Generate human-readable sector performance report."""
        ranked = self.rank_sectors(sector_performance)
        rotation = self.identify_sector_rotation(ranked)
        
        report = "SECTOR PERFORMANCE REPORT\n"
        report += "=" * 50 + "\n\n"
        
        report += f"Rotation Signal: {rotation['rotation_signal'].upper()}\n"
        report += f"Explanation: {rotation['explanation']}\n\n"
        
        report += "Sector Rankings:\n"
        for i, sector in enumerate(ranked, 1):
            report += f"{i}. {sector['sector']}: {sector['performance']:+.2f}% "
            report += f"({sector['breadth']} positive)\n"
        
        return report
    
    def get_sector_recommendations(self, ranked_sectors: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Get sector allocation recommendations."""
        if not ranked_sectors:
            return {'overweight': [], 'neutral': [], 'underweight': []}
        
        total_sectors = len(ranked_sectors)
        top_third = total_sectors // 3
        
        overweight = [s['sector'] for s in ranked_sectors[:top_third]]
        underweight = [s['sector'] for s in ranked_sectors[-top_third:]]
        neutral = [s['sector'] for s in ranked_sectors[top_third:-top_third]]
        
        return {
            'overweight': overweight,
            'neutral': neutral,
            'underweight': underweight
        }


if __name__ == "__main__":
    backtester = SectorBacktest()
    
    # Test with mock data
    mock_data = {
        'Technology': [
            {'ticker': 'AAPL', 'change_percent': 2.5},
            {'ticker': 'MSFT', 'change_percent': 1.8}
        ],
        'Finance': [
            {'ticker': 'JPM', 'change_percent': -0.5},
            {'ticker': 'BAC', 'change_percent': -1.2}
        ]
    }
    
    performance = backtester.calculate_sector_performance(mock_data)
    report = backtester.generate_sector_report(performance)
    print(report)
