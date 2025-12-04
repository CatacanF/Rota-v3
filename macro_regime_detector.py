"""
Macro Regime Detector Module (v2.0)
Identifies current market regime: Inflationary, Deflationary, Stagflation, or Goldilocks.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MacroRegimeDetector:
    """Detects and analyzes macro economic regimes."""
    
    def __init__(self):
        self.regimes = {
            'goldilocks': {
                'description': 'Strong growth + Low inflation',
                'best_assets': ['Equities', 'Corporate Bonds'],
                'characteristics': 'Ideal economic environment'
            },
            'inflationary': {
                'description': 'High inflation + Positive growth',
                'best_assets': ['Commodities', 'Real Estate', 'TIPS'],
                'characteristics': 'Rising prices, central bank tightening'
            },
            'stagflation': {
                'description': 'High inflation + Weak/Negative growth',
                'best_assets': ['Gold', 'Commodities', 'Cash'],
                'characteristics': 'Worst environment for risk assets'
            },
            'deflationary': {
                'description': 'Low/Negative inflation + Weak growth',
                'best_assets': ['Government Bonds', 'Cash', 'Gold'],
                'characteristics': 'Risk-off environment'
            },
            'reflation': {
                'description': 'Rising inflation from low base + Improving growth',
                'best_assets': ['Cyclical Stocks', 'Commodities', 'Value Stocks'],
                'characteristics': 'Economic recovery phase'
            }
        }
    
    def detect_regime(self, economic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect current macro regime based on economic indicators.
        
        Args:
            economic_data: {
                'gdp_growth': float (annual %),
                'inflation_rate': float (annual %),
                'unemployment': float (%),
                'interest_rate': float (%)
            }
        """
        gdp_growth = economic_data.get('gdp_growth', 0)
        inflation_rate = economic_data.get('inflation_rate', 0)
        unemployment = economic_data.get('unemployment', 0)
        
        # Regime detection logic
        regime = self._classify_regime(gdp_growth, inflation_rate, unemployment)
        
        regime_info = self.regimes.get(regime, self.regimes['goldilocks'])
        
        return {
            'regime': regime,
            'description': regime_info['description'],
            'best_assets': regime_info['best_assets'],
            'characteristics': regime_info['characteristics'],
            'confidence': self._calculate_confidence(economic_data),
            'indicators': {
                'gdp_growth': gdp_growth,
                'inflation': inflation_rate,
                'unemployment': unemployment
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _classify_regime(self, gdp_growth: float, inflation: float, unemployment: float) -> str:
        """Classify regime based on growth and inflation."""
        
        # Thresholds
        high_inflation = inflation > 3.0
        moderate_inflation = 1.0 < inflation <= 3.0
        low_inflation = inflation <= 1.0
        
        strong_growth = gdp_growth > 2.5
        moderate_growth = 1.0 < gdp_growth <= 2.5
        weak_growth = gdp_growth <= 1.0
        negative_growth = gdp_growth < 0
        
        # Classification logic
        if high_inflation and (negative_growth or weak_growth):
            return 'stagflation'
        elif high_inflation and (strong_growth or moderate_growth):
            return 'inflationary'
        elif moderate_inflation and strong_growth:
            return 'goldilocks'
        elif low_inflation and strong_growth:
            return 'reflation'
        elif (low_inflation or negative_growth) and weak_growth:
            return 'deflationary'
        else:
            return 'goldilocks'  # Default
    
    def _calculate_confidence(self, economic_data: Dict[str, Any]) -> str:
        """Calculate confidence in regime detection."""
        # Simple confidence based on data completeness
        required_fields = ['gdp_growth', 'inflation_rate', 'unemployment']
        present_fields = sum(1 for field in required_fields if field in economic_data)
        
        confidence_pct = (present_fields / len(required_fields)) * 100
        
        if confidence_pct >= 80:
            return 'high'
        elif confidence_pct >= 50:
            return 'medium'
        else:
            return 'low'
    
    def analyze_turkish_regime(self, turkish_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Turkish economic regime specifically."""
        # Turkish-specific thresholds (higher inflation tolerance)
        gdp_growth = turkish_data.get('gdp_growth', 0)
        inflation_rate = turkish_data.get('inflation_rate', 0)
        tcmb_rate = turkish_data.get('tcmb_interest_rate', 0)
        usdtry_rate = turkish_data.get('usdtry', 0)
        
        # Adjusted regime detection for Turkey
        if inflation_rate > 20:
            if gdp_growth > 3:
                regime = 'inflationary'
                recommendation = 'Focus on hard assets: real estate, gold, foreign currency'
            else:
                regime = 'stagflation'
                recommendation = 'Defensive positioning: gold, USD, quality dividend stocks'
        elif inflation_rate > 10:
            regime = 'inflationary'
            recommendation = 'Favor real assets and inflation hedges'
        elif gdp_growth > 4:
            regime = 'goldilocks'
            recommendation = 'Favor Turkish equities, especially exporters'
        else:
            regime = 'deflationary'
            recommendation = 'Conservative positioning, focus on TRY bonds if rates high'
        
        regime_info = self.regimes.get(regime, self.regimes['inflationary'])
        
        return {
            'regime': regime,
            'description': regime_info['description'],
            'turkish_context': f"Turkey-specific: Inflation at {inflation_rate}%, Growth at {gdp_growth}%",
            'recommendation': recommendation,
            'indicators': {
                'gdp_growth': gdp_growth,
                'inflation': inflation_rate,
                'tcmb_rate': tcmb_rate,
                'usdtry': usdtry_rate
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def get_regime_explanation(self, regime: str) -> str:
        """Get detailed explanation of a regime."""
        regime_info = self.regimes.get(regime)
        
        if not regime_info:
            return f"Unknown regime: {regime}"
        
        explanation = f"MACRO REGIME: {regime.upper()}\n"
        explanation += "=" * 60 + "\n\n"
        explanation += f"Description: {regime_info['description']}\n"
        explanation += f"Characteristics: {regime_info['characteristics']}\n"
        explanation += f"Best Asset Classes: {', '.join(regime_info['best_assets'])}\n"
        
        return explanation
    
    def compare_regimes(self, current_regime: str, previous_regime: str) -> Dict[str, Any]:
        """Compare current vs previous regime and suggest adjustments."""
        current_info = self.regimes.get(current_regime)
        previous_info = self.regimes.get(previous_regime)
        
        if current_regime == previous_regime:
            return {
                'change': 'no_change',
                'action': 'maintain_current_allocation',
                'explanation': f"Regime unchanged: {current_regime}"
            }
        
        # Determine strategy shift
        assets_to_add = set(current_info['best_assets']) - set(previous_info['best_assets'])
        assets_to_reduce = set(previous_info['best_assets']) - set(current_info['best_assets'])
        
        return {
            'change': 'regime_shift',
            'from': previous_regime,
            'to': current_regime,
            'assets_to_add': list(assets_to_add),
            'assets_to_reduce': list(assets_to_reduce),
            'explanation': f"Regime shifted from {previous_regime} to {current_regime}. Adjust portfolio accordingly."
        }


if __name__ == "__main__":
    detector = MacroRegimeDetector()
    
    # Test with sample data
    test_data = {
        'gdp_growth': 2.8,
        'inflation_rate': 2.1,
        'unemployment': 4.5,
        'interest_rate': 4.5
    }
    
    regime = detector.detect_regime(test_data)
    print(f"Detected regime: {regime['regime']}")
    print(detector.get_regime_explanation(regime['regime']))
