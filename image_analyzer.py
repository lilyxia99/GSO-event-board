import openai
from PIL import Image
import base64
import io
import os
from config import OPENAI_API_KEY

class ImageAnalyzer:
    def __init__(self):
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
        
    def analyze_event_poster(self, image_path):
        """Analyze event poster using AI to extract relevant information"""
        if not OPENAI_API_KEY:
            return {"error": "OpenAI API key not configured"}
            
        try:
            # Read and encode image
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Analyze with OpenAI Vision
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this event poster and extract the following information in JSON format:
                                {
                                    "event_name": "extracted event name",
                                    "date": "extracted date",
                                    "time": "extracted time",
                                    "location": "extracted venue/location",
                                    "description": "brief description of the event",
                                    "event_type": "category like concert, meetup, festival, etc.",
                                    "key_details": ["list", "of", "important", "details"]
                                }
                                If any information is not clearly visible, use null for that field."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Error analyzing image: {str(e)}",
                "success": False
            }
    
    def batch_analyze_images(self, events):
        """Analyze all event images and add AI insights to event data"""
        for event in events:
            if event.get('local_image_path') and os.path.exists(event['local_image_path']):
                print(f"Analyzing image for: {event['title']}")
                analysis = self.analyze_event_poster(event['local_image_path'])
                event['ai_analysis'] = analysis
                
        return events

if __name__ == "__main__":
    analyzer = ImageAnalyzer()
    # Test with a sample image
    result = analyzer.analyze_event_poster("sample_poster.jpg")
    print(result)
