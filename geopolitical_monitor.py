"""
Geopolitical Monitor Module (v2.0)
Tracks global geopolitical risks and their market impact.
"""

from typing import List, Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeopoliticalMonitor:
    """Monitors geopolitical events and assesses market impact."""
    
    def __init__(self):
        self.risk_categories = {
            'military_conflict': {'severity_multiplier': 1.5, 'affected_assets': ['Oil', 'Gold', 'Defense stocks']},
            'trade_war': {'severity_multiplier': 1.2, 'affected_assets': ['Export stocks', 'Currencies']},
            'political_crisis': {'severity_multiplier': 1.0, 'affected_assets': ['Local equities', 'Currency']},
            'sanctions': {'severity_multiplier': 1.3, 'affected_assets': ['Commodities', 'Regional stocks']},
            'election': {'severity_multiplier': 0.8, 'affected_assets': ['All assets', 'Volatility']},
            'central_bank': {'severity_multiplier': 1.4, 'affected_assets': ['Bonds', 'Currency', 'Equities']}
        }
        
        # Key regions to monitor
        self.regions = {
            'Middle_East': ['Israel', 'Iran', 'Saudi Arabia', 'Syria', 'Iraq'],
            'Eastern_Europe': ['Ukraine', 'Russia', 'Poland', 'Belarus'],
            'Asia_Pacific': ['China', 'Taiwan', 'North Korea', 'South Korea', 'Japan'],
            'Turkey': ['Turkey domestic', 'Turkey-EU relations', 'Turkey-US relations'],
            'Latin_America': ['Venezuela', 'Argentina', 'Brazil', 'Mexico']
        }
    
    def assess_risk_level(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess overall geopolitical risk level.
        
        Args:
            events: List of geopolitical events, each with:
                - category: str
                - region: str
                - severity: int (1-10)
                - description: str
        """
        if not events:
            return {
                'overall_risk': 'low',
                'risk_score': 0,
                'explanation': 'No significant geopolitical events detected'
            }
        
        total_score = 0
        for event in events:
            category = event.get('category', 'political_crisis')
            severity = event.get('severity', 5)
            multiplier = self.risk_categories.get(category, {}).get('severity_multiplier', 1.0)
            
            event_score = severity * multiplier
            total_score += event_score
        
        avg_score = total_score / len(events)
        
        # Classify risk level
        if avg_score >= 12:
            risk_level = 'critical'
        elif avg_score >= 8:
            risk_level = 'high'
        elif avg_score >= 5:
            risk_level = 'moderate'
        else:
            risk_level = 'low'
        
        return {
            'overall_risk': risk_level,
            'risk_score': round(avg_score, 2),
            'total_events': len(events),
            'explanation': f"Analyzed {len(events)} events, average risk score: {avg_score:.2f}",
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_market_impact(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market impact of geopolitical events."""
        affected_assets = set()
        high_impact_events = []
        
        for event in events:
            category = event.get('category', 'political_crisis')
            severity = event.get('severity', 5)
            
            if severity >= 7:
                high_impact_events.append(event)
            
            category_info = self.risk_categories.get(category, {})
            assets = category_info.get('affected_assets', [])
            affected_assets.update(assets)
        
        # Determine market sentiment
        if high_impact_events:
            sentiment = 'risk_off'
            recommendation = 'Reduce risk exposure, increase cash and safe havens'
        elif len(events) > 5:
            sentiment = 'cautious'
            recommendation = 'Monitor closely, hedge key positions'
        else:
            sentiment = 'neutral'
            recommendation = 'Maintain current allocations with vigilance'
        
        return {
            'market_sentiment': sentiment,
            'affected_assets': list(affected_assets),
            'high_impact_events_count': len(high_impact_events),
            'recommendation': recommendation,
            'details': high_impact_events
        }
    
    def monitor_turkish_geopolitics(self) -> Dict[str, Any]:
        """Monitor geopolitical factors specific to Turkey."""
        # This would integrate with news APIs to detect Turkish geopolitical events
        # For now, returning structure
        
        turkish_factors = {
            'domestic_politics': {
                'stability': 'moderate',
                'upcoming_events': ['Local elections', 'Economic reforms'],
                'risk_level': 'moderate'
            },
            'regional_tensions': {
                'neighbors': ['Syria', 'Iraq', 'Greece'],
                'tension_level': 'elevated',
                'impact': 'Currency volatility, defense spending'
            },
            'international_relations': {
                'eu_relations': 'complicated',
                'us_relations': 'improving',
                'russia_relations': 'pragmatic',
                'impact': 'Trade flows, investment'
            },
            'syrian_refugee_situation': {
                'status': 'ongoing',
                'economic_impact': 'moderate',
                'political_impact': 'significant'
            }
        }
        
        # Calculate overall Turkish geopolitical score
        risk_factors = sum([
            2 if turkish_factors['regional_tensions']['tension_level'] == 'elevated' else 0,
            1 if turkish_factors['domestic_politics']['stability'] != 'high' else 0,
            1  # Base level
        ])
        
        overall_assessment = 'elevated' if risk_factors >= 3 else 'moderate'
        
        return {
            'assessment': overall_assessment,
            'risk_score': risk_factors,
            'factors': turkish_factors,
            'investment_implications': self._get_turkish_investment_implications(overall_assessment),
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_turkish_investment_implications(self, assessment: str) -> str:
        """Get investment implications for Turkish markets."""
        implications = {
            'low': 'Favorable for Turkish assets. Consider increasing exposure.',
            'moderate': 'Selective positioning. Focus on quality names and exporters.',
            'elevated': 'Cautious approach. Hedge currency risk. Favor defensive sectors.',
            'high': 'Risk-off for Turkish assets. Preserve capital, focus on hard currency assets.'
        }
        
        return implications.get(assessment, implications['moderate'])
    
    def generate_geopolitical_report(self, events: List[Dict[str, Any]]) -> str:
        """Generate human-readable geopolitical report."""
        risk = self.assess_risk_level(events)
        impact = self.analyze_market_impact(events)
        
        report = "GEOPOLITICAL RISK ASSESSMENT\n"
        report += "=" * 70 + "\n\n"
        
        report += f"Overall Risk Level: {risk['overall_risk'].upper()} (Score: {risk['risk_score']}/15)\n"
        report += f"Market Sentiment: {impact['market_sentiment'].upper()}\n\n"
        
        report += "Affected Assets:\n"
        for asset in impact['affected_assets']:
            report += f"  • {asset}\n"
        
        report += f"\nRecommendation: {impact['recommendation']}\n\n"
        
        if impact['high_impact_events_count'] > 0:
            report += "High Impact Events:\n"
            for event in impact['details']:
                report += f"  • {event.get('description', 'N/A')} "
                report += f"[{event.get('region', 'Unknown')}] "
                report += f"(Severity: {event.get('severity', 'N/A')}/10)\n"
        
        return report
    
    def detect_tail_risks(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect potential tail risk events."""
        tail_risks = []
        
        for event in events:
            severity = event.get('severity', 0)
            category = event.get('category', '')
            
            # Tail risk criteria: severity >= 8 OR military conflict
            if severity >= 8 or category == 'military_conflict':
                tail_risks.append({
                    **event,
                    'tail_risk_reason': 'High severity event with potential for market dislocation'
                })
        
        logger.info(f"Detected {len(tail_risks)} potential tail risk events")
        return tail_risks


if __name__ == "__main__":
    monitor = GeopoliticalMonitor()
    
    # Test with sample events
    test_events = [
        {
            'category': 'military_conflict',
            'region': 'Middle_East',
            'severity': 7,
            'description': 'Border tensions escalate'
        },
        {
            'category': 'election',
            'region': 'Turkey',
            'severity': 5,
            'description': 'Upcoming elections create uncertainty'
        }
    ]
    
    risk = monitor.assess_risk_level(test_events)
    print(f"Risk level: {risk['overall_risk']}")
    print("\n" + monitor.generate_geopolitical_report(test_events))
