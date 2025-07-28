#!/usr/bin/env python3
"""
Simple Demo - Direct Import Test
"""

import sys
import os
sys.path.append('.')

def test_sentiment():
    print("🔍 Testing Sentiment Analysis...")
    
    # Try direct import
    try:
        import src.data_processing.sentiment_analyzer as sa
        print("✅ Module imported successfully!")
        
        # Create analyzer instance
        analyzer = sa.SentimentAnalyzer()
        print("✅ Analyzer created!")
        
        # Test analysis
        text = "This is a great product!"
        result = analyzer.analyze_sentiment(text)
        print(f"✅ Analysis result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_nltk():
    print("\n📦 Testing NLTK...")
    try:
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer
        
        # Download required data
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        
        # Test VADER
        sia = SentimentIntensityAnalyzer()
        text = "This is amazing!"
        scores = sia.polarity_scores(text)
        print(f"✅ VADER scores: {scores}")
        
        return True
        
    except Exception as e:
        print(f"❌ NLTK Error: {e}")
        return False

def test_textblob():
    print("\n📝 Testing TextBlob...")
    try:
        from textblob import TextBlob
        
        text = "This product is excellent!"
        blob = TextBlob(text)
        print(f"✅ TextBlob polarity: {blob.sentiment.polarity}")
        
        return True
        
    except Exception as e:
        print(f"❌ TextBlob Error: {e}")
        return False

def main():
    print("🚀 Smart Feedback Analysis - Component Test")
    print("=" * 50)
    
    # Test individual components
    nltk_ok = test_nltk()
    textblob_ok = test_textblob()
    sentiment_ok = test_sentiment()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  NLTK: {'✅' if nltk_ok else '❌'}")
    print(f"  TextBlob: {'✅' if textblob_ok else '❌'}")
    print(f"  Sentiment Analyzer: {'✅' if sentiment_ok else '❌'}")
    
    if all([nltk_ok, textblob_ok, sentiment_ok]):
        print("\n🎉 All components working! Ready to run analysis.")
    else:
        print("\n⚠️  Some components have issues. Check the errors above.")

if __name__ == "__main__":
    main() 