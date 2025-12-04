"""
Portfolio Analyzer Module (v2.0)
Analyzes portfolio allocation, performance, and risk metrics.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """Analyzes portfolio allocation and risk."""
    
    def __init__(self):
        self.risk_free_rate = 0.04  # 4% risk-free rate assumption
    
    def analyze_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze portfolio allocation.
        
        Args:
            holdings: List of holdings, each with:
                - ticker: str
                - shares: float
                - current_price: float
                - asset_class: str (equity, bond, commodity, cash, crypto)
                - sector: str (optional)
        """
        if not holdings:
            return {'error': 'No holdings provided'}
        
        total_value = sum(h['shares'] * h['current_price'] for h in holdings)
        
        # Asset class allocation
        asset_class_allocation = {}
        sector_allocation = {}
        
        for holding in holdings:
            shares = holding['shares']
            price = holding['current_price']
            value = shares * price
            weight = (value / total_value) * 100 if total_value > 0 else 0
            
            asset_class = holding.get('asset_class', 'other')
            sector = holding.get('sector', 'other')
            
            # Aggregate by asset class
            if asset_class not in asset_class_allocation:
                asset_class_allocation[asset_class] = 0
            asset_class_allocation[asset_class] += weight
            
            # Aggregate by sector
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += weight
        
        # Calculate concentration risk (Herfindahl index)
        holding_weights = [(h['shares'] * h['current_price'] / total_value) * 100 for h in holdings]
        herfindahl_index = sum(w ** 2 for w in holding_weights) / 100
        
        concentration_risk = 'high' if herfindahl_index > 25 else 'moderate' if herfindahl_index > 15 else 'low'
        
        return {
            'total_value': round(total_value, 2),
            'num_holdings': len(holdings),
            'asset_class_allocation': {k: round(v, 2) for k, v in asset_class_allocation.items()},
            'sector_allocation': {k: round(v, 2) for k, v in sector_allocation.items()},
            'concentration_risk': concentration_risk,
            'herfindahl_index': round(herfindahl_index, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_performance(self, holdings: List[Dict[str, Any]], previous_values: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate portfolio performance.
        
        Args:
            previous_values: {ticker: previous_total_value}
        """
        current_value = sum(h['shares'] * h['current_price'] for h in holdings)
        
        total_gain_loss = 0
        for holding in holdings:
            ticker = holding['ticker']
            current_position_value = holding['shares'] * holding['current_price']
            previous_value = previous_values.get(ticker, current_position_value)
            
            gain_loss = current_position_value - previous_value
            total_gain_loss += gain_loss
        
        previous_total_value = sum(previous_values.values())
        return_pct = (total_gain_loss / previous_total_value * 100) if previous_total_value > 0 else 0
        
        return {
            'current_value': round(current_value, 2),
            'previous_value': round(previous_total_value, 2),
            'gain_loss': round(total_gain_loss, 2),
            'return_percent': round(return_pct, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_risk_metrics(self, holdings: List[Dict[str, Any]], daily_returns: List[float]) -> Dict[str, Any]:
        """
        Calculate risk metrics including Sharpe ratio, volatility, max drawdown.
        
        Args:
            daily_returns: List of daily portfolio returns (as decimals, e.g., 0.01 for 1%)
        """
        if not daily_returns:
            return {'error': 'No return data provided'}
        
        # Calculate metrics
        avg_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
        volatility = variance ** 0.5
        
        # Annualize (assuming 252 trading days)
        annual_return = avg_return * 252
        annual_volatility = volatility * (252 ** 0.5)
        
        # Sharpe ratio
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Max drawdown
        cumulative = [1]
        for ret in daily_returns:
            cumulative.append(cumulative[-1] * (1 + ret))
        
        running_max = cumulative[0]
        max_drawdown = 0
        for value in cumulative:
            if value > running_max:
                running_max = value
            drawdown = (running_max - value) / running_max
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Value at Risk (95% confidence, parametric)
        var_95 = avg_return - (1.65 * volatility)  # Daily VaR
        
        return {
            'annual_return': round(annual_return * 100, 2),
            'annual_volatility': round(annual_volatility * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'value_at_risk_95': round(var_95 * 100, 2),
            'risk_rating': self._get_risk_rating(annual_volatility)
        }
    
    def _get_risk_rating(self, annual_volatility: float) -> str:
        """Assign risk rating based on volatility."""
        vol_pct = annual_volatility * 100
        
        if vol_pct < 10:
            return 'low_risk'
        elif vol_pct < 20:
            return 'moderate_risk'
        elif vol_pct < 30:
            return 'high_risk'
        else:
            return 'very_high_risk'
    
    def get_rebalancing_recommendations(self, current_allocation: Dict[str, float], target_allocation: Dict[str, float]) -> Dict[str, Any]:
        """Get portfolio rebalancing recommendations."""
        deviations = {}
        significant_deviations = []
        
        for asset_class, target_weight in target_allocation.items():
            current_weight = current_allocation.get(asset_class, 0)
            deviation = current_weight - target_weight
            deviations[asset_class] = round(deviation, 2)
            
            if abs(deviation) > 5:  # More than 5% deviation
                significant_deviations.append({
                    'asset_class': asset_class,
                    'current': current_weight,
                    'target': target_weight,
                    'deviation': round(deviation, 2),
                    'action': 'reduce' if deviation > 0 else 'increase'
                })
        
        needs_rebalancing = len(significant_deviations) > 0
        
        return {
            'needs_rebalancing': needs_rebalancing,
            'deviations': deviations,
            'significant_deviations': significant_deviations,
            'recommendation': 'Rebalance portfolio to target allocation' if needs_rebalancing else 'Portfolio is well-balanced'
        }
    
    def generate_portfolio_report(self, holdings: List[Dict[str, Any]], daily_returns: Optional[List[float]] = None) -> str:
        """Generate comprehensive portfolio report."""
        allocation = self.analyze_allocation(holdings)
        
        report = "PORTFOLIO ANALYSIS REPORT\n"
        report += "=" * 70 + "\n\n"
        
        report += f"Total Portfolio Value: ${allocation['total_value']:,.2f}\n"
        report += f"Number of Holdings: {allocation['num_holdings']}\n"
        report += f"Concentration Risk: {allocation['concentration_risk'].upper()}\n\n"
        
        report += "Asset Class Allocation:\n"
        for asset_class, weight in allocation['asset_class_allocation'].items():
            report += f"  • {asset_class.title()}: {weight:.1f}%\n"
        
        report += "\nSector Allocation:\n"
        for sector, weight in allocation['sector_allocation'].items():
            if weight > 1:  # Only show sectors > 1%
                report += f"  • {sector.title()}: {weight:.1f}%\n"
        
        if daily_returns:
            risk_metrics = self.calculate_risk_metrics(holdings, daily_returns)
            report += "\nRisk Metrics:\n"
            report += f"  • Annual Return: {risk_metrics['annual_return']:.2f}%\n"
            report += f"  • Annual Volatility: {risk_metrics['annual_volatility']:.2f}%\n"
            report += f"  • Sharpe Ratio: {risk_metrics['sharpe_ratio']:.2f}\n"
            report += f"  • Max Drawdown: {risk_metrics['max_drawdown']:.2f}%\n"
            report += f"  • Risk Rating: {risk_metrics['risk_rating'].upper().replace('_', ' ')}\n"
        
        return report


if __name__ == "__main__":
    analyzer = PortfolioAnalyzer()
    
    # Test with sample portfolio
    test_holdings = [
        {'ticker': 'AAPL', 'shares': 10, 'current_price': 150, 'asset_class': 'equity', 'sector': 'technology'},
        {'ticker': 'GOOGL', 'shares': 5, 'current_price': 120, 'asset_class': 'equity', 'sector': 'technology'},
        {'ticker': 'GLD', 'shares': 20, 'current_price': 180, 'asset_class': 'commodity', 'sector': 'gold'}
    ]
    
    allocation = analyzer.analyze_allocation(test_holdings)
    print(f"Total value: ${allocation['total_value']:,.2f}")
    print(f"Asset allocation: {allocation['asset_class_allocation']}")
