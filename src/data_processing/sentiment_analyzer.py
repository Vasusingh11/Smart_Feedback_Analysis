"""
Sentiment Analysis Module
Handles text sentiment scoring using multiple NLP models
"""

import pandas as pd
import numpy as np
import nltk
from textblob import TextBlob
import re
import string
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
from typing import Dict, Any

class SentimentAnalyzer:
    """
    Advanced sentiment analysis using combined NLTK VADER and TextBlob models
    Provides sentiment scores, labels, and confidence measures
    """
    
    def __init__(self):
        """Initialize sentiment analyzer with required NLTK data"""
        self._download_nltk_data()
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self.logger = logging.getLogger(__name__)
        
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
            
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
    
    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text data
        
        Args:
            text (str): Raw text input
            
        Returns:
            str: Cleaned text
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation but keep sentence structure
        text = text.translate(str.maketrans('', '', string.punctuation.replace('.', '').replace('!', '').replace('?', '')))
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def analyze_sentiment_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using NLTK VADER
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, float]: VADER sentiment scores
        """
        if not text:
            return {'compound': 0, 'pos': 0, 'neu': 1, 'neg': 0}
            
        return self.sia.polarity_scores(text)
    
    def analyze_sentiment_textblob(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using TextBlob
        
        Args:
            text (str): Text to analyze
            
        Returns:
            Dict[str, float]: TextBlob sentiment scores
        """
        if not text:
            return {'polarity': 0, 'subjectivity': 0}
            
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def analyze_sentiment(self, text: str, vader_weight: float = 0.6, 
                         textblob_weight: float = 0.4) -> Dict[str, Any]:
        """
        Analyze sentiment using combined NLTK VADER and TextBlob models
        
        Args:
            text (str): Text to analyze
            vader_weight (float): Weight for VADER score (default: 0.6)
            textblob_weight (float): Weight for TextBlob score (default: 0.4)
            
        Returns:
            Dict[str, Any]: Combined sentiment analysis results
        """
        if not text:
            return {
                'score': 0,
                'label': 'Neutral',
                'confidence': 0,
                'vader_compound': 0,
                'textblob_polarity': 0,
                'subjectivity': 0
            }
        
        # Clean text first
        cleaned_text = self.clean_text(text)
        
        # VADER sentiment analysis
        vader_scores = self.analyze_sentiment_vader(cleaned_text)
        vader_compound = vader_scores['compound']
        
        # TextBlob sentiment analysis
        textblob_scores = self.analyze_sentiment_textblob(cleaned_text)
        textblob_polarity = textblob_scores['polarity']
        subjectivity = textblob_scores['subjectivity']
        
        # Combine scores using weighted average
        combined_score = (vader_compound * vader_weight) + (textblob_polarity * textblob_weight)
        
        # Determine sentiment label with thresholds
        if combined_score >= 0.05:
            label = 'Positive'
        elif combined_score <= -0.05:
            label = 'Negative'
        else:
            label = 'Neutral'
        
        # Calculate confidence based on absolute score and agreement
        score_magnitude = abs(combined_score)
        agreement_factor = 1 - abs(vader_compound - textblob_polarity) / 2
        confidence = min(score_magnitude * agreement_factor, 1.0)
        
        return {
            'score': round(combined_score, 4),
            'label': label,
            'confidence': round(confidence, 4),
            'vader_compound': round(vader_compound, 4),
            'textblob_polarity': round(textblob_polarity, 4),
            'subjectivity': round(subjectivity, 4)
        }
    
    def analyze_batch(self, texts: list, batch_size: int = 1000) -> pd.DataFrame:
        """
        Analyze sentiment for a batch of texts
        
        Args:
            texts (list): List of texts to analyze
            batch_size (int): Size of processing batches
            
        Returns:
            pd.DataFrame: Sentiment analysis results
        """
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for idx, text in enumerate(batch):
                try:
                    sentiment = self.analyze_sentiment(text)
                    sentiment['text_id'] = i + idx
                    sentiment['original_text'] = text
                    sentiment['cleaned_text'] = self.clean_text(text) if text else ""
                    results.append(sentiment)
                    
                except Exception as e:
                    self.logger.error(f"Error analyzing text {i + idx}: {e}")
                    # Add default neutral sentiment for failed analysis
                    results.append({
                        'text_id': i + idx,
                        'score': 0,
                        'label': 'Neutral',
                        'confidence': 0,
                        'vader_compound': 0,
                        'textblob_polarity': 0,
                        'subjectivity': 0,
                        'original_text': text,
                        'cleaned_text': ""
                    })
            
            # Log progress
            if i % (batch_size * 10) == 0:
                self.logger.info(f"Processed {min(i + batch_size, len(texts))}/{len(texts)} texts")
        
        return pd.DataFrame(results)
    
    def get_sentiment_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get sentiment distribution statistics
        
        Args:
            df (pd.DataFrame): DataFrame with sentiment analysis results
            
        Returns:
            Dict[str, Any]: Sentiment distribution statistics
        """
        if df.empty:
            return {
                'total_count': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'average_score': 0,
                'average_confidence': 0
            }
        
        total_count = len(df)
        positive_count = len(df[df['label'] == 'Positive'])
        negative_count = len(df[df['label'] == 'Negative'])
        neutral_count = len(df[df['label'] == 'Neutral'])
        
        return {
            'total_count': total_count,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': round((positive_count / total_count) * 100, 2),
            'negative_percentage': round((negative_count / total_count) * 100, 2),
            'neutral_percentage': round((neutral_count / total_count) * 100, 2),
            'average_score': round(df['score'].mean(), 4),
            'average_confidence': round(df['confidence'].mean(), 4)
        }

# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    # Test samples
    test_texts = [
        "I love this product! It's amazing and works perfectly.",
        "This is terrible quality. I'm very disappointed.",
        "The product is okay, nothing special but does the job.",
        "Excellent customer service and fast delivery!",
        "Poor experience, would not recommend to anyone.",
        ""  # Test empty text
    ]
    
    # Test individual analysis
    print("Individual Sentiment Analysis:")
    print("-" * 50)
    for i, text in enumerate(test_texts):
        result = analyzer.analyze_sentiment(text)
        print(f"Text {i + 1}: {text[:50]}...")
        print(f"Score: {result['score']}, Label: {result['label']}, Confidence: {result['confidence']}")
        print()
    
    # Test batch analysis
    print("Batch Analysis Results:")
    print("-" * 30)
    batch_results = analyzer.analyze_batch(test_texts)
    print(batch_results[['label', 'score', 'confidence']].head())
    
    # Test distribution
    print("\nSentiment Distribution:")
    print("-" * 25)
    distribution = analyzer.get_sentiment_distribution(batch_results)
    for key, value in distribution.items():
        print(f"{key}: {value}")