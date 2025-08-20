from flask import Flask, render_template, jsonify
import pandas as pd
import json
from datetime import datetime, timedelta
import os
from config import HOST, PORT, DEBUG, SPREADSHEET_PATH

app = Flask(__name__)

class EventCalendarApp:
    def __init__(self):
        self.events_data = []
        self.load_events()
    
    def load_events(self):
        """Load events from the Excel file"""
        try:
            if os.path.exists(SPREADSHEET_PATH):
                df = pd.read_excel(SPREADSHEET_PATH, sheet_name='Greensboro Events', skiprows=3)
                self.events_data = df.to_dict('records')
            else:
                self.events_data = []
        except Exception as e:
            print(f"Error loading events: {e}")
            self.events_data = []
    
    def get_events_for_calendar(self):
        """Format events for calendar display"""
        calendar_events = []
        
        for event in self.events_data:
            if pd.notna(event.get('Title', '')):
                calendar_event = {
                    'title': event.get('Title', 'Untitled Event'),
                    'start': self._parse_event_date(event.get('Date', ''), event.get('Time', '')),
                    'description': event.get('Description', ''),
                    'location': event.get('Location', ''),
                    'url': event.get('Event URL', ''),
                    'type': event.get('Event Type', 'Unknown')
                }
                calendar_events.append(calendar_event)
        
        return calendar_events
    
    def _parse_event_date(self, date_str, time_str):
        """Parse event date and time for calendar format"""
        try:
            if pd.isna(date_str) or not date_str:
                return datetime.now().isoformat()
            
            # Try to parse the date
            if isinstance(date_str, str):
                # Handle various date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%B %d, %Y']:
                    try:
                        parsed_date = datetime.strptime(date_str, fmt)
                        
                        # Add time if available
                        if pd.notna(time_str) and time_str:
                            try:
                                time_part = datetime.strptime(str(time_str), '%H:%M').time()
                                parsed_date = datetime.combine(parsed_date.date(), time_part)
                            except:
                                pass
                        
                        return parsed_date.isoformat()
                    except ValueError:
                        continue
            
            return datetime.now().isoformat()
            
        except Exception as e:
            print(f"Error parsing date {date_str}: {e}")
            return datetime.now().isoformat()

# Initialize the app
calendar_app = EventCalendarApp()

@app.route('/')
def index():
    """Main calendar page"""
    return render_template('calendar.html')

@app.route('/api/events')
def get_events():
    """API endpoint to get events for calendar"""
    calendar_app.load_events()  # Refresh data
    events = calendar_app.get_events_for_calendar()
    return jsonify(events)

@app.route('/api/refresh')
def refresh_events():
    """API endpoint to refresh events data"""
    calendar_app.load_events()
    return jsonify({'status': 'success', 'count': len(calendar_app.events_data)})

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
