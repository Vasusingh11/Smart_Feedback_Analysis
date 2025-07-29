#!/usr/bin/env python3
"""
Simple test script for the feedback analysis platform
"""

import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append('.')

# Import our working feedback analyzer
exec(open('feedback_analyzer.py').read())

def analyze_new_feedback(text):
    """Analyze a new piece of feedback"""
    analyzer = FeedbackAnalyzer()
    result = analyzer.analyze_sentiment(text)
    
    emoji = "😊" if result['sentiment_label'] == "Positive" else "😞" if result['sentiment_label'] == "Negative" else "😐"
    print(f"{emoji} '{text}'")
    print(f"   → {result['sentiment_label']} (score: {result['combined_score']:+.3f}, confidence: {result['confidence']:.3f})")
    print()
    return result

def show_data_summary():
    """Show summary of existing data"""
    try:
        feedback_df = pd.read_csv('data/raw/sample_feedback.csv')
        sentiment_df = pd.read_csv('data/processed/sentiment_results.csv')
        
        print(f"📊 Data Summary:")
        print(f"  Total feedback: {len(feedback_df)}")
        print(f"  Analyzed: {len(sentiment_df)}")
        
        if len(sentiment_df) > 0:
            sentiment_dist = sentiment_df['sentiment_label'].value_counts()
            print(f"  Sentiment distribution:")
            for label, count in sentiment_dist.items():
                emoji = "😊" if label == "Positive" else "😞" if label == "Negative" else "😐"
                print(f"    {emoji} {label}: {count}")
    except Exception as e:
        print(f"❌ Could not load data: {e}")

def main():
    print("🧪 Feedback Analysis Platform - Quick Test")
    print("=" * 45)
    
    # Show existing data
    show_data_summary()
    
    print("\nTesting sentiment analysis:")
    
    # Test sentiment analysis
    analyze_new_feedback("This product is absolutely amazing!")
    analyze_new_feedback("Poor quality, very disappointed.")
    analyze_new_feedback("It's okay, nothing special.")
    
    print("✅ Test completed!")
    print("\n💡 To analyze your own text:")
    print("   result = analyze_new_feedback('Your feedback text here')")

if __name__ == "__main__":
    main()
