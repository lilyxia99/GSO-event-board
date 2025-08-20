#!/usr/bin/env python3
"""
Main entry point for the Greensboro Events Scraper
This script orchestrates the entire process:
1. Scrape Facebook events
2. Download and analyze event images with AI
3. Process and clean the data
4. Export to spreadsheet
5. Start the web server for calendar view
"""

import sys
import os
import argparse
from datetime import datetime

# Import our modules
from scraper import FacebookEventScraper
from image_analyzer import ImageAnalyzer
from data_processor import EventDataProcessor
from spreadsheet_exporter import SpreadsheetExporter
from app import app
from config import HOST, PORT, DEBUG, SPREADSHEET_PATH

def run_scraper():
    """Run the complete scraping and processing pipeline"""
    print("🚀 Starting Greensboro Events Scraper...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Scrape Facebook events
    print("\n📱 Step 1: Scraping Facebook events...")
    scraper = FacebookEventScraper()
    raw_events = scraper.scrape_events()
    print(f"✅ Found {len(raw_events)} events")
    
    if not raw_events:
        print("❌ No events found. Exiting...")
        return
    
    # Step 2: Download event images
    print("\n🖼️  Step 2: Downloading event images...")
    scraper.download_event_images()
    
    # Step 3: Analyze images with AI
    print("\n🤖 Step 3: Analyzing event images with AI...")
    analyzer = ImageAnalyzer()
    events_with_ai = analyzer.batch_analyze_images(raw_events)
    
    # Step 4: Process and clean data
    print("\n🧹 Step 4: Processing and cleaning event data...")
    processor = EventDataProcessor()
    processed_events = processor.process_events(events_with_ai)
    processor.merge_ai_data()
    
    # Step 5: Export to spreadsheet
    print("\n📊 Step 5: Exporting to spreadsheet...")
    events_df = processor.get_dataframe()
    
    if not events_df.empty:
        exporter = SpreadsheetExporter()
        exporter.export_events(events_df)
        exporter.create_summary_sheet(events_df)
        print(f"✅ Exported {len(events_df)} events to {SPREADSHEET_PATH}")
    else:
        print("❌ No valid events to export")
    
    print(f"\n🎉 Scraping completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return len(processed_events)

def start_web_server():
    """Start the Flask web server for calendar view"""
    print(f"\n🌐 Starting web server at http://{HOST}:{PORT}")
    print("📅 Calendar will be available in your browser")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")

def main():
    """Main function with command line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Greensboro Events Scraper - Scrape Facebook events and display in calendar"
    )
    
    parser.add_argument(
        '--mode', 
        choices=['scrape', 'server', 'both'], 
        default='both',
        help='Mode to run: scrape only, server only, or both (default: both)'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser in non-headless mode (visible browser window)'
    )
    
    args = parser.parse_args()
    
    # Update config if needed
    if args.no_headless:
        import config
        config.HEADLESS = False
    
    print("🎯 Greensboro Events Scraper")
    print("=" * 50)
    
    if args.mode in ['scrape', 'both']:
        event_count = run_scraper()
        
        if args.mode == 'scrape':
            print(f"\n✨ Scraping complete! Found {event_count} events.")
            print(f"📄 Check {SPREADSHEET_PATH} for the results")
            return
    
    if args.mode in ['server', 'both']:
        if args.mode == 'both':
            print("\n" + "=" * 50)
        
        # Check if spreadsheet exists
        if not os.path.exists(SPREADSHEET_PATH):
            print(f"⚠️  Warning: {SPREADSHEET_PATH} not found.")
            print("Run with --mode scrape first, or the calendar will be empty.")
        
        start_web_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
