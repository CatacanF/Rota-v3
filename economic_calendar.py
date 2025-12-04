"""
Economic Calendar Module
Tracks major economic events and releases.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EconomicCalendar:
    """Manages economic events and calendar."""
    
    def __init__(self):
        # Turkish Central Bank (TCMB/CBT) Meeting Dates 2025
        self.cbt_meetings_2025 = [
            "2025-01-23", "2025-02-20", "2025-03-20", "2025-04-24",
            "2025-05-22", "2025-06-19", "2025-07-24", "2025-08-21",
            "2025-09-18", "2025-10-23", "2025-11-20", "2025-12-25"
        ]
        
        # Turkish Inflation Data Release Dates 2025
        self.inflation_dates_2025 = [
            "2025-01-03", "2025-02-03", "2025-03-03", "2025-04-03",
            "2025-05-05", "2025-06-03", "2025-07-03", "2025-08-04",
            "2025-09-03", "2025-10-03", "2025-11-03", "2025-12-03"
        ]
        
        # Fed Meeting Dates 2025 (FOMC)
        self.fed_meetings_2025 = [
            "2025-01-29", "2025-03-19", "2025-05-07", "2025-06-18",
            "2025-07-30", "2025-09-17", "2025-11-05", "2025-12-17"
        ]
        
        # ECB Meeting Dates 2025
        self.ecb_meetings_2025 = [
            "2025-01-30", "2025-03-06", "2025-04-17", "2025-06-05",
            "2025-07-24", "2025-09-11", "2025-10-30", "2025-12-18"
        ]
    
    def get_upcoming_events(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming economic events within specified days."""
        today = datetime.now()
        cutoff_date = today + timedelta(days=days_ahead)
        
        events = []
        
        # Turkish Central Bank Meetings
        for date_str in self.cbt_meetings_2025:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            if today <= event_date <= cutoff_date:
                events.append({
                    'date': date_str,
                    'event': 'TCMB Interest Rate Decision',
                    'country': 'Turkey',
                    'importance': 'high',
                    'category': 'monetary_policy'
                })
        
        # Turkish Inflation Data
        for date_str in self.inflation_dates_2025:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            if today <= event_date <= cutoff_date:
                events.append({
                    'date': date_str,
                    'event': 'Turkey CPI (Inflation) Data',
                    'country': 'Turkey',
                    'importance': 'high',
                    'category': 'economic_data'
                })
        
        # Fed Meetings
        for date_str in self.fed_meetings_2025:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            if today <= event_date <= cutoff_date:
                events.append({
                    'date': date_str,
                    'event': 'FOMC Interest Rate Decision',
                    'country': 'USA',
                    'importance': 'high',
                    'category': 'monetary_policy'
                })
        
        # ECB Meetings
        for date_str in self.ecb_meetings_2025:
            event_date = datetime.strptime(date_str, "%Y-%m-%d")
            if today <= event_date <= cutoff_date:
                events.append({
                    'date': date_str,
                    'event': 'ECB Interest Rate Decision',
                    'country': 'Eurozone',
                    'importance': 'high',
                    'category': 'monetary_policy'
                })
        
        # Sort by date
        events.sort(key=lambda x: x['date'])
        
        logger.info(f"Found {len(events)} upcoming events in next {days_ahead} days")
        return events
    
    def get_next_major_event(self) -> Dict[str, Any]:
        """Get the next major economic event."""
        upcoming = self.get_upcoming_events(days_ahead=90)
        
        if upcoming:
            next_event = upcoming[0]
            event_date = datetime.strptime(next_event['date'], "%Y-%m-%d")
            days_until = (event_date - datetime.now()).days
            
            return {
                **next_event,
                'days_until': days_until
            }
        
        return {'event': 'No upcoming events', 'days_until': None}
    
    def get_this_week_events(self) -> List[Dict[str, Any]]:
        """Get events happening this week."""
        return self.get_upcoming_events(days_ahead=7)
    
    def get_turkish_events(self, days_ahead: int = 90) -> List[Dict[str, Any]]:
        """Get upcoming Turkish economic events only."""
        all_events = self.get_upcoming_events(days_ahead)
        turkish_events = [e for e in all_events if e['country'] == 'Turkey']
        
        logger.info(f"Found {len(turkish_events)} Turkish events")
        return turkish_events
    
    def generate_calendar_summary(self, days_ahead: int = 30) -> str:
        """Generate human-readable calendar summary."""
        events = self.get_upcoming_events(days_ahead)
        
        if not events:
            return f"No major economic events scheduled in the next {days_ahead} days."
        
        summary = f"ECONOMIC CALENDAR - Next {days_ahead} Days\n"
        summary += "=" * 60 + "\n\n"
        
        current_week = None
        for event in events:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")
            week = event_date.strftime("%Y-W%W")
            
            if week != current_week:
                summary += f"\nWeek of {event_date.strftime('%B %d, %Y')}:\n"
                summary += "-" * 60 + "\n"
                current_week = week
            
            days_until = (event_date - datetime.now()).days
            summary += f"  {event['date']} ({days_until} days): "
            summary += f"{event['event']} [{event['country']}]\n"
        
        return summary
    
    def get_event_alerts(self, alert_days: int = 3) -> List[Dict[str, Any]]:
        """Get events that should trigger alerts (within alert_days)."""
        upcoming = self.get_upcoming_events(days_ahead=alert_days)
        
        alerts = []
        for event in upcoming:
            event_date = datetime.strptime(event['date'], "%Y-%m-%d")
            days_until = (event_date - datetime.now()).days
            
            if days_until <= alert_days:
                alerts.append({
                    **event,
                    'days_until': days_until,
                    'alert_message': f"Alert: {event['event']} in {days_until} day(s)"
                })
        
        return alerts


if __name__ == "__main__":
    calendar = EconomicCalendar()
    
    print("Next Major Event:")
    next_event = calendar.get_next_major_event()
    print(f"{next_event['event']} in {next_event['days_until']} days")
    
    print("\n" + calendar.generate_calendar_summary(days_ahead=60))
