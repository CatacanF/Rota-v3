"""
Alert Engine Module (v2.0)
Real-time alert system for critical market events.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertEngine:
    """Manages real-time alerts for critical market events."""
    
    def __init__(self):
        self.severity_levels = {
            1: {'name': 'Info', 'color': 'blue', 'channels': ['log']},
            2: {'name': 'Notice', 'color': 'green', 'channels': ['email']},
            3: {'name': 'Warning', 'color': 'yellow', 'channels': ['email', 'slack']},
            4: {'name': 'Critical', 'color': 'orange', 'channels': ['email', 'slack', 'sms']},
            5: {'name': 'Emergency', 'color': 'red', 'channels': ['email', 'slack', 'sms', 'voice']}
        }
        
        self.alert_types = {
            'price_movement': 'Price moved beyond threshold',
            'volume_spike': 'Unusual trading volume detected',
            'news_event': 'Breaking news event',
            'economic_data': 'Major economic data release',
            'geopolitical': 'Geopolitical event detected',
            'technical_signal': 'Technical indicator triggered',
            'portfolio_risk': 'Portfolio risk threshold exceeded',
            'margin_call': 'Margin requirements alert'
        }
    
    def create_alert(self, alert_type: str, severity: int, message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new alert.
        
        Args:
            alert_type: Type of alert from self.alert_types
            severity: 1-5 (Info to Emergency)
            message: Alert message
            metadata: Additional context data
        """
        severity = max(1, min(5, severity))  # Clamp between 1-5
        severity_info = self.severity_levels[severity]
        
        alert = {
            'id': self._generate_alert_id(),
            'type': alert_type,
            'severity': severity,
            'severity_name': severity_info['name'],
            'message': message,
            'channels': severity_info['channels'],
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'acknowledged': False
        }
        
        logger.info(f"Alert created: [{severity_info['name']}] {alert_type} - {message}")
        
        return alert
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"ALERT-{timestamp}"
    
    def check_price_alert(self, ticker: str, current_price: float, threshold_pct: float, previous_price: float) -> Optional[Dict[str, Any]]:
        """Check if price movement triggers an alert."""
        price_change_pct = ((current_price - previous_price) / previous_price) * 100
        
        if abs(price_change_pct) >= threshold_pct:
            severity = 4 if abs(price_change_pct) >= threshold_pct * 2 else 3
            
            direction = "surged" if price_change_pct > 0 else "dropped"
            message = f"{ticker} {direction} {abs(price_change_pct):.2f}% to ${current_price:.2f}"
            
            return self.create_alert(
                alert_type='price_movement',
                severity=severity,
                message=message,
                metadata={
                    'ticker': ticker,
                    'current_price': current_price,
                    'previous_price': previous_price,
                    'change_percent': round(price_change_pct, 2)
                }
            )
        
        return None
    
    def check_volume_alert(self, ticker: str, current_volume: int, avg_volume: int, threshold_multiplier: float = 2.0) -> Optional[Dict[str, Any]]:
        """Check if volume spike triggers an alert."""
        if current_volume >= avg_volume * threshold_multiplier:
            volume_increase_pct = ((current_volume - avg_volume) / avg_volume) * 100
            
            severity = 4 if current_volume >= avg_volume * 4 else 3
            message = f"{ticker} volume spike: {volume_increase_pct:.0f}% above average ({current_volume:,} vs {avg_volume:,})"
            
            return self.create_alert(
                alert_type='volume_spike',
                severity=severity,
                message=message,
                metadata={
                    'ticker': ticker,
                    'current_volume': current_volume,
                    'avg_volume': avg_volume,
                    'multiplier': round(current_volume / avg_volume, 2)
                }
            )
        
        return None
    
    def check_economic_calendar_alert(self, event: Dict[str, Any], days_until: int) -> Optional[Dict[str, Any]]:
        """Check if upcoming economic event triggers an alert."""
        if days_until <= 1:
            severity = 4
            message = f"IMMINENT: {event['event']} in {days_until} day(s) - {event['country']}"
        elif days_until <= 3:
            severity = 3
            message = f"UPCOMING: {event['event']} in {days_until} days - {event['country']}"
        else:
            return None
        
        return self.create_alert(
            alert_type='economic_data',
            severity=severity,
            message=message,
            metadata=event
        )
    
    def check_geopolitical_alert(self, risk_level: str, risk_score: float, events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check if geopolitical risk triggers an alert."""
        severity_map = {
            'critical': 5,
            'high': 4,
            'moderate': 3,
            'low': 2
        }
        
        severity = severity_map.get(risk_level, 2)
        
        if severity >= 3:
            message = f"Geopolitical risk elevated to {risk_level.upper()} (score: {risk_score:.1f})"
            
            return self.create_alert(
                alert_type='geopolitical',
                severity=severity,
                message=message,
                metadata={
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'event_count': len(events)
                }
            )
        
        return None
    
    def check_portfolio_risk_alert(self, sharpe_ratio: float, max_drawdown: float, var_95: float) -> Optional[Dict[str, Any]]:
        """Check if portfolio risk metrics trigger an alert."""
        alerts = []
        
        # Check Sharpe ratio
        if sharpe_ratio < 0.5:
            alerts.append(f"Low Sharpe ratio: {sharpe_ratio:.2f} (risk-adjusted returns poor)")
        
        # Check drawdown
        if max_drawdown > 20:
            alerts.append(f"High drawdown: {max_drawdown:.1f}% (significant losses)")
        
        # Check VaR
        if var_95 < -5:
            alerts.append(f"High Value at Risk: {var_95:.1f}% (potential large loss)")
        
        if alerts:
            severity = 4 if len(alerts) >= 2 else 3
            message = "Portfolio risk alert: " + "; ".join(alerts)
            
            return self.create_alert(
                alert_type='portfolio_risk',
                severity=severity,
                message=message,
                metadata={
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_drawdown,
                    'var_95': var_95
                }
            )
        
        return None
    
    def check_sentiment_alert(self, sentiment: str, confidence: str, compound_score: float) -> Optional[Dict[str, Any]]:
        """Check if market sentiment triggers an alert."""
        if confidence == 'high' and abs(compound_score) >= 0.5:
            if sentiment == 'negative':
                severity = 3
                message = f"Strong negative market sentiment detected (score: {compound_score:.2f})"
            elif sentiment == 'positive':
                severity = 2
                message = f"Strong positive market sentiment detected (score: {compound_score:.2f})"
            else:
                return None
            
            return self.create_alert(
                alert_type='news_event',
                severity=severity,
                message=message,
                metadata={
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'compound_score': compound_score
                }
            )
        
        return None
    
    def filter_alerts_by_severity(self, alerts: List[Dict[str, Any]], min_severity: int = 3) -> List[Dict[str, Any]]:
        """Filter alerts by minimum severity level."""
        return [alert for alert in alerts if alert['severity'] >= min_severity]
    
    def acknowledge_alert(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Mark an alert as acknowledged."""
        alert['acknowledged'] = True
        alert['acknowledged_at'] = datetime.now().isoformat()
        return alert
    
    def generate_alert_summary(self, alerts: List[Dict[str, Any]]) -> str:
        """Generate human-readable alert summary."""
        if not alerts:
            return "No active alerts."
        
        summary = f"ALERT SUMMARY - {len(alerts)} Active Alert(s)\n"
        summary += "=" * 70 + "\n\n"
        
        # Group by severity
        by_severity = {}
        for alert in alerts:
            severity = alert['severity']
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(alert)
        
        # Display from highest to lowest severity
        for severity in sorted(by_severity.keys(), reverse=True):
            severity_name = self.severity_levels[severity]['name']
            summary += f"{severity_name.upper()} ({len(by_severity[severity])}):\n"
            
            for alert in by_severity[severity]:
                summary += f"  • [{alert['type']}] {alert['message']}\n"
            summary += "\n"
        
        return summary


if __name__ == "__main__":
    engine = AlertEngine()
    
    # Test price alert
    alert = engine.check_price_alert('AAPL', 155, 5, 145)
    if alert:
        print(f"Alert: {alert['message']}")
    
    # Test portfolio risk alert
    risk_alert = engine.check_portfolio_risk_alert(sharpe_ratio=0.3, max_drawdown=25, var_95=-6)
    if risk_alert:
        print(f"Risk Alert: {risk_alert['message']}")
