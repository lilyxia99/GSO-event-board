import pandas as pd
from datetime import datetime
import re
import json

class EventDataProcessor:
    def __init__(self):
        self.processed_events = []
    
    def process_events(self, raw_events):
        """Clean and standardize event data"""
        for event in raw_events:
            processed_event = self._clean_event_data(event)
            if processed_event:
                self.processed_events.append(processed_event)
        
        return self.processed_events
    
    def _clean_event_data(self, event):
        """Clean individual event data"""
        cleaned = {
            'title': self._clean_text(event.get('title', '')),
            'date': self._parse_date(event.get('date', '')),
            'time': self._clean_text(event.get('time', '')),
            'location': self._clean_text(event.get('location', '')),
            'description': self._clean_text(event.get('description', '')),
            'image_url': event.get('image_url', ''),
            'event_url': event.get('event_url', ''),
            'local_image_path': event.get('local_image_path', ''),
            'scraped_at': event.get('scraped_at', ''),
            'ai_extracted_info': self._extract_ai_info(event.get('ai_analysis', {}))
        }
        
        # Only keep events with meaningful data
        if cleaned['title'] or cleaned['ai_extracted_info'].get('event_name'):
            return cleaned
        
        return None
    
    def _clean_text(self, text):
        """Clean and normalize text data"""
        if not text:
            return ''
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', str(text)).strip()
        return text
    
    def _parse_date(self, date_str):
        """Attempt to parse and standardize date formats"""
        if not date_str:
            return ''
        
        # Common date patterns
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, str(date_str))
            if match:
                return date_str  # Return original for now, could standardize format
        
        return date_str
    
    def _extract_ai_info(self, ai_analysis):
        """Extract structured information from AI analysis"""
        if not ai_analysis or not ai_analysis.get('success'):
            return {}
        
        try:
            # Try to parse JSON from AI response
            analysis_text = ai_analysis.get('analysis', '')
            
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {'raw_analysis': ai_analysis.get('analysis', '')}
    
    def merge_ai_data(self):
        """Merge AI-extracted data with scraped data"""
        for event in self.processed_events:
            ai_info = event.get('ai_extracted_info', {})
            
            # Use AI data to fill in missing fields
            if not event['title'] and ai_info.get('event_name'):
                event['title'] = ai_info['event_name']
            
            if not event['date'] and ai_info.get('date'):
                event['date'] = ai_info['date']
            
            if not event['time'] and ai_info.get('time'):
                event['time'] = ai_info['time']
            
            if not event['location'] and ai_info.get('location'):
                event['location'] = ai_info['location']
            
            if not event['description'] and ai_info.get('description'):
                event['description'] = ai_info['description']
            
            # Add event type from AI
            event['event_type'] = ai_info.get('event_type', 'Unknown')
    
    def get_dataframe(self):
        """Convert processed events to pandas DataFrame"""
        if not self.processed_events:
            return pd.DataFrame()
        
        # Flatten the data for spreadsheet export
        flattened_events = []
        for event in self.processed_events:
            flat_event = {
                'Title': event['title'],
                'Date': event['date'],
                'Time': event['time'],
                'Location': event['location'],
                'Description': event['description'],
                'Event Type': event['event_type'],
                'Image URL': event['image_url'],
                'Event URL': event['event_url'],
                'Scraped At': event['scraped_at']
            }
            flattened_events.append(flat_event)
        
        return pd.DataFrame(flattened_events)

if __name__ == "__main__":
    processor = EventDataProcessor()
    # Test with sample data
    sample_events = [{'title': 'Test Event', 'date': '12/25/2023'}]
    processed = processor.process_events(sample_events)
    df = processor.get_dataframe()
    print(df.head())
