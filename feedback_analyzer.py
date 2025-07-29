#!/usr/bin/env python3
"""
Smart Feedback Analysis - Working Demo
Uses NLTK VADER and TextBlob for sentiment analysis
"""

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import pandas as pd
import numpy as np
from datetime import datetime

class FeedbackAnalyzer:
    def __init__(self):
        # Download required NLTK data
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        
        # Initialize VADER sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
        
    def analyze_sentiment(self, text):
        """Analyze sentiment using both VADER and TextBlob"""
        if not text or pd.isna(text):
            return {
                'text': text,
                'vader_compound': 0,
                'textblob_polarity': 0,
                'combined_score': 0,
                'sentiment_label': 'Neutral',
                'confidence': 0
            }
        
        # VADER analysis
        vader_scores = self.sia.polarity_scores(text)
        vader_compound = vader_scores['compound']
        
        # TextBlob analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity
        
        # Combined score (weighted average)
        combined_score = (vader_compound * 0.6) + (textblob_polarity * 0.4)
        
        # Determine sentiment label
        if combined_score > 0.05:
            sentiment_label = 'Positive'
            confidence = abs(combined_score)
        elif combined_score < -0.05:
            sentiment_label = 'Negative'
            confidence = abs(combined_score)
        else:
            sentiment_label = 'Neutral'
            confidence = 1 - abs(combined_score)
        
        return {
            'text': text,
            'vader_compound': round(vader_compound, 3),
            'textblob_polarity': round(textblob_polarity, 3),
            'combined_score': round(combined_score, 3),
            'sentiment_label': sentiment_label,
            'confidence': round(confidence, 3)
        }
    
    def analyze_batch(self, feedback_list):
        """Analyze multiple feedback texts"""
        results = []
        for i, feedback in enumerate(feedback_list):
            result = self.analyze_sentiment(feedback)
            result['id'] = i + 1
            results.append(result)
        return results
    
    def get_statistics(self, results):
        """Calculate sentiment statistics"""
        if not results:
            return {}
        
        total = len(results)
        positive = sum(1 for r in results if r['sentiment_label'] == 'Positive')
        negative = sum(1 for r in results if r['sentiment_label'] == 'Negative')
        neutral = sum(1 for r in results if r['sentiment_label'] == 'Neutral')
        
        avg_score = np.mean([r['combined_score'] for r in results])
        avg_confidence = np.mean([r['confidence'] for r in results])
        
        return {
            'total_feedback': total,
            'positive_count': positive,
            'negative_count': negative,
            'neutral_count': neutral,
            'positive_percentage': round((positive/total)*100, 1),
            'negative_percentage': round((negative/total)*100, 1),
            'neutral_percentage': round((neutral/total)*100, 1),
            'average_sentiment_score': round(avg_score, 3),
            'average_confidence': round(avg_confidence, 3)
        }

def main():
    print("🚀 Smart Feedback Analysis Platform")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize analyzer
    print("\n🔧 Initializing sentiment analyzer...")
    analyzer = FeedbackAnalyzer()
    print("✅ Analyzer ready!")
    
    # Sample feedback data
    sample_feedback = [
        "This product is absolutely amazing! I love the quality and design.",
        "Terrible experience. The product broke after just one day of use.",
        "It's okay, nothing special but does what it's supposed to do.",
        "Outstanding customer service! They resolved my issue immediately.",
        "Very disappointed with the purchase. Poor quality and overpriced.",
        "Great value for money. Fast shipping and excellent packaging.",
        "The website is confusing and the checkout process was frustrating.",
        "Fantastic product! Exceeded my expectations completely.",
        "Average quality. Not bad but not great either.",
        "Excellent delivery speed and the product works perfectly!"
    ]
    
    print(f"\n📝 Analyzing {len(sample_feedback)} feedback items...")
    
    # Analyze all feedback
    results = analyzer.analyze_batch(sample_feedback)
    
    # Display results
    print("\n📊 ANALYSIS RESULTS")
    print("-" * 50)
    
    for result in results:
        sentiment_emoji = "😊" if result['sentiment_label'] == 'Positive' else "😞" if result['sentiment_label'] == 'Negative' else "😐"
        print(f"{result['id']:2d}. {sentiment_emoji} {result['sentiment_label']} (Score: {result['combined_score']:+.3f})")
        print(f"     '{result['text'][:60]}...'" if len(result['text']) > 60 else f"     '{result['text']}'")
        print(f"     VADER: {result['vader_compound']:+.3f} | TextBlob: {result['textblob_polarity']:+.3f} | Confidence: {result['confidence']:.3f}")
        print()
    
    # Calculate and display statistics
    stats = analyzer.get_statistics(results)
    
    print("📈 SUMMARY STATISTICS")
    print("-" * 30)
    print(f"Total Feedback Items: {stats['total_feedback']}")
    print(f"Positive: {stats['positive_count']} ({stats['positive_percentage']}%)")
    print(f"Negative: {stats['negative_count']} ({stats['negative_percentage']}%)")
    print(f"Neutral: {stats['neutral_count']} ({stats['neutral_percentage']}%)")
    print(f"Average Sentiment Score: {stats['average_sentiment_score']:+.3f}")
    print(f"Average Confidence: {stats['average_confidence']:.3f}")
    
    # Provide insights
    print("\n💡 KEY INSIGHTS")
    print("-" * 20)
    if stats['positive_percentage'] > 60:
        print("🎉 Great news! Majority of feedback is positive.")
    elif stats['negative_percentage'] > 40:
        print("⚠️  Warning: High negative feedback detected. Review needed.")
    else:
        print("📊 Mixed feedback pattern. Balanced sentiment distribution.")
    
    if stats['average_confidence'] > 0.7:
        print("🎯 High confidence in sentiment predictions.")
    else:
        print("🤔 Moderate confidence. Some feedback may need manual review.")
    
    print("\n✅ Analysis completed successfully!")
    print("\n🚀 Next steps:")
    print("  1. Connect to your database to analyze real feedback")
    print("  2. Set up automated processing pipeline")
    print("  3. Create Power BI dashboards for visualization")

if __name__ == "__main__":
    main() 