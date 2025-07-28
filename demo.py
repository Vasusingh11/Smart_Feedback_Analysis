#!/usr/bin/env python3
"""
Simple Demo Script for Smart Feedback Analysis
Tests the core functionality without requiring a database
"""

import sys
import os
sys.path.append('.')

def main():
    print("🚀 Smart Feedback Analysis Platform - Demo")
    print("=" * 50)
    
    try:
        # Test 1: Import core modules
        print("📦 Testing imports...")
        from src.data_processing.sentiment_analyzer import SentimentAnalyzer
        from src.data_processing.text_cleaner import TextCleaner
        print("✅ Core modules imported successfully!")
        
        # Test 2: Initialize sentiment analyzer
        print("\n🔍 Initializing sentiment analyzer...")
        analyzer = SentimentAnalyzer()
        print("✅ Sentiment analyzer initialized!")
        
        # Test 3: Analyze sample feedback
        print("\n📝 Analyzing sample feedback...")
        sample_feedback = [
            "This product is absolutely amazing! Love it!",
            "Terrible quality, very disappointed with the purchase.",
            "It's okay, nothing special but does the job.",
            "Excellent customer service and fast delivery!",
            "Poor experience, would not recommend to anyone."
        ]
        
        results = []
        for i, feedback in enumerate(sample_feedback, 1):
            result = analyzer.analyze_sentiment(feedback)
            results.append(result)
            
            sentiment_label = "Positive" if result['compound'] > 0.05 else "Negative" if result['compound'] < -0.05 else "Neutral"
            print(f"  {i}. '{feedback[:50]}...' → {sentiment_label} (Score: {result['compound']:.3f})")
        
        # Test 4: Show statistics
        print("\n📊 Analysis Statistics:")
        positive_count = sum(1 for r in results if r['compound'] > 0.05)
        negative_count = sum(1 for r in results if r['compound'] < -0.05)
        neutral_count = len(results) - positive_count - negative_count
        
        print(f"  Positive: {positive_count}")
        print(f"  Negative: {negative_count}")
        print(f"  Neutral: {neutral_count}")
        print(f"  Total: {len(results)}")
        
        # Test 5: Test text cleaning
        print("\n🧹 Testing text cleaning...")
        cleaner = TextCleaner()
        dirty_text = "This is a GREAT product!!! @user123 #awesome http://example.com"
        clean_text = cleaner.clean_text(dirty_text)
        print(f"  Original: '{dirty_text}'")
        print(f"  Cleaned: '{clean_text}'")
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Run 'python scripts/run_analysis.py sample --count 1000' to generate sample data")
        print("2. Set up a database (SQL Server or SQLite)")
        print("3. Run 'python scripts/run_analysis.py run' for full analysis")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 