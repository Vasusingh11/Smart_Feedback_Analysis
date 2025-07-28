"""
Test Suite for Sentiment Analysis Module
Comprehensive tests for sentiment analysis functionality
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import Mock, patch

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_processing.sentiment_analyzer import SentimentAnalyzer


class TestSentimentAnalyzer:
    """Test cases for SentimentAnalyzer class"""
    
    @pytest.fixture
    def analyzer(self):
        """Create SentimentAnalyzer instance for testing"""
        return SentimentAnalyzer()
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing with known sentiment"""
        return {
            'positive': [
                "I love this product! It's amazing and works perfectly.",
                "Excellent service and fantastic quality. Highly recommend!",
                "Outstanding customer support and fast delivery.",
                "Great value for money, will definitely buy again!"
            ],
            'negative': [
                "This is terrible quality. I'm very disappointed.",
                "Poor customer service and slow response time.",
                "Product broke after one day. Complete waste of money.",
                "Worst experience ever. Would not recommend to anyone."
            ],
            'neutral': [
                "The product is okay, nothing special but does the job.",
                "Standard quality and reasonable price.",
                "Average experience, neither good nor bad.",
                "It works as expected, no major complaints."
            ]
        }
    
    def test_analyzer_initialization(self, analyzer):
        """Test SentimentAnalyzer initialization"""
        assert analyzer is not None
        assert hasattr(analyzer, 'sia')
        assert hasattr(analyzer, 'stop_words')
        assert len(analyzer.stop_words) > 0
    
    def test_clean_text_basic(self, analyzer):
        """Test basic text cleaning functionality"""
        # Test normal text
        clean_text = analyzer.clean_text("Hello World!")
        assert clean_text == "hello world"
        
        # Test text with URLs
        text_with_url = "Check out https://example.com for more info"
        clean_text = analyzer.clean_text(text_with_url)
        assert "https://example.com" not in clean_text
        assert "check out" in clean_text.lower()
        
        # Test text with mentions and hashtags
        social_text = "Great product @company #awesome #love"
        clean_text = analyzer.clean_text(social_text)
        assert "@company" not in clean_text
        assert "#awesome" not in clean_text
        assert "great product" in clean_text.lower()
    
    def test_clean_text_edge_cases(self, analyzer):
        """Test text cleaning with edge cases"""
        # Test empty string
        assert analyzer.clean_text("") == ""
        
        # Test None input
        assert analyzer.clean_text(None) == ""
        
        # Test only punctuation
        assert analyzer.clean_text("!!!???") == ""
        
        # Test only whitespace
        assert analyzer.clean_text("   \n\t  ") == ""
        
        # Test very long text
        long_text = "word " * 1000
        clean_long = analyzer.clean_text(long_text)
        assert len(clean_long) > 0
        assert "word" in clean_long
    
    def test_analyze_sentiment_positive(self, analyzer, sample_texts):
        """Test sentiment analysis for positive texts"""
        for text in sample_texts['positive']:
            result = analyzer.analyze_sentiment(text)
            
            # Check structure
            assert isinstance(result, dict)
            assert 'score' in result
            assert 'label' in result
            assert 'confidence' in result
            
            # Check positive sentiment
            assert result['score'] > 0, f"Expected positive score for: {text}"
            assert result['label'] == 'Positive', f"Expected Positive label for: {text}"
            assert 0 <= result['confidence'] <= 1
    
    def test_analyze_sentiment_negative(self, analyzer, sample_texts):
        """Test sentiment analysis for negative texts"""
        for text in sample_texts['negative']:
            result = analyzer.analyze_sentiment(text)
            
            # Check negative sentiment
            assert result['score'] < 0, f"Expected negative score for: {text}"
            assert result['label'] == 'Negative', f"Expected Negative label for: {text}"
            assert 0 <= result['confidence'] <= 1
    
    def test_analyze_sentiment_neutral(self, analyzer, sample_texts):
        """Test sentiment analysis for neutral texts"""
        for text in sample_texts['neutral']:
            result = analyzer.analyze_sentiment(text)
            
            # Check neutral sentiment (allowing some variance)
            assert -0.1 <= result['score'] <= 0.1, f"Expected neutral score for: {text}"
            assert result['label'] == 'Neutral', f"Expected Neutral label for: {text}"
    
    def test_analyze_sentiment_empty_text(self, analyzer):
        """Test sentiment analysis with empty text"""
        result = analyzer.analyze_sentiment("")
        
        assert result['score'] == 0
        assert result['label'] == 'Neutral'
        assert result['confidence'] == 0
    
    def test_analyze_sentiment_weights(self, analyzer):
        """Test sentiment analysis with different weights"""
        text = "This is a great product!"
        
        # Test with different weight combinations
        result1 = analyzer.analyze_sentiment(text, vader_weight=0.8, textblob_weight=0.2)
        result2 = analyzer.analyze_sentiment(text, vader_weight=0.2, textblob_weight=0.8)
        
        # Both should be positive but potentially different scores
        assert result1['label'] == 'Positive'
        assert result2['label'] == 'Positive'
        assert isinstance(result1['score'], float)
        assert isinstance(result2['score'], float)
    
    def test_analyze_batch_basic(self, analyzer, sample_texts):
        """Test batch analysis functionality"""
        all_texts = []
        expected_labels = []
        
        for label, texts in sample_texts.items():
            all_texts.extend(texts[:2])  # Take 2 from each category
            expected_labels.extend([label.title()] * 2)
        
        results_df = analyzer.analyze_batch(all_texts)
        
        # Check structure
        assert isinstance(results_df, pd.DataFrame)
        assert len(results_df) == len(all_texts)
        assert 'score' in results_df.columns
        assert 'label' in results_df.columns
        assert 'confidence' in results_df.columns
        
        # Check no missing values in essential columns
        assert not results_df['score'].isna().any()
        assert not results_df['label'].isna().any()
        assert not results_df['confidence'].isna().any()
    
    def test_analyze_batch_empty_list(self, analyzer):
        """Test batch analysis with empty list"""
        results_df = analyzer.analyze_batch([])
        
        assert isinstance(results_df, pd.DataFrame)
        assert len(results_df) == 0
    
    def test_analyze_batch_large_batch(self, analyzer):
        """Test batch analysis with large batch size"""
        # Create large list of texts
        large_text_list = ["This is test text number {}".format(i) for i in range(100)]
        
        results_df = analyzer.analyze_batch(large_text_list, batch_size=25)
        
        assert len(results_df) == 100
        assert 'text_id' in results_df.columns
        assert results_df['text_id'].max() == 99
    
    def test_get_sentiment_distribution(self, analyzer, sample_texts):
        """Test sentiment distribution calculation"""
        # Create test DataFrame
        all_texts = []
        for texts in sample_texts.values():
            all_texts.extend(texts[:2])
        
        results_df = analyzer.analyze_batch(all_texts)
        distribution = analyzer.get_sentiment_distribution(results_df)
        
        # Check structure
        assert isinstance(distribution, dict)
        assert 'total_count' in distribution
        assert 'positive_count' in distribution
        assert 'negative_count' in distribution
        assert 'neutral_count' in distribution
        assert 'positive_percentage' in distribution
        assert 'average_score' in distribution
        
        # Check counts add up
        total = distribution['positive_count'] + distribution['negative_count'] + distribution['neutral_count']
        assert total == distribution['total_count']
        
        # Check percentages add up to 100 (with small tolerance for rounding)
        total_percentage = (distribution['positive_percentage'] + 
                          distribution['negative_percentage'] + 
                          distribution['neutral_percentage'])
        assert abs(total_percentage - 100) < 0.1
    
    def test_get_sentiment_distribution_empty(self, analyzer):
        """Test sentiment distribution with empty DataFrame"""
        empty_df = pd.DataFrame()
        distribution = analyzer.get_sentiment_distribution(empty_df)
        
        assert distribution['total_count'] == 0
        assert distribution['positive_count'] == 0
        assert distribution['average_score'] == 0
    
    def test_sentiment_consistency(self, analyzer):
        """Test sentiment analysis consistency"""
        text = "I absolutely love this product!"
        
        # Run analysis multiple times
        results = [analyzer.analyze_sentiment(text) for _ in range(5)]
        
        # All results should be identical
        for result in results[1:]:
            assert result['score'] == results[0]['score']
            assert result['label'] == results[0]['label']
            assert result['confidence'] == results[0]['confidence']
    
    def test_score_ranges(self, analyzer, sample_texts):
        """Test that sentiment scores are within expected ranges"""
        all_texts = []
        for texts in sample_texts.values():
            all_texts.extend(texts)
        
        for text in all_texts:
            result = analyzer.analyze_sentiment(text)
            
            # Score should be between -1 and 1
            assert -1 <= result['score'] <= 1
            
            # Confidence should be between 0 and 1
            assert 0 <= result['confidence'] <= 1
            
            # Subjectivity should be between 0 and 1
            assert 0 <= result['subjectivity'] <= 1
    
    @pytest.mark.parametrize("text,expected_label", [
        ("I love this!", "Positive"),
        ("This is terrible!", "Negative"),
        ("It's okay.", "Neutral"),
        ("Amazing product! Highly recommend!", "Positive"),
        ("Worst service ever. Very disappointed.", "Negative"),
    ])
    def test_specific_sentiment_cases(self, analyzer, text, expected_label):
        """Test specific sentiment cases with parametrized testing"""
        result = analyzer.analyze_sentiment(text)
        assert result['label'] == expected_label
    
    def test_performance_benchmark(self, analyzer):
        """Test performance with timing"""
        import time
        
        texts = ["Test sentiment analysis performance."] * 100
        
        start_time = time.time()
        results_df = analyzer.analyze_batch(texts)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should process 100 texts in reasonable time (adjust threshold as needed)
        assert duration < 30  # 30 seconds max for 100 texts
        assert len(results_df) == 100
        
        # Log performance for monitoring
        print(f"Processed {len(texts)} texts in {duration:.2f} seconds")
        print(f"Rate: {len(texts)/duration:.1f} texts per second")
    
    def test_error_handling(self, analyzer):
        """Test error handling in sentiment analysis"""
        # Test with problematic inputs
        problematic_texts = [
            None,
            "",
            "   ",
            123,  # Non-string input
            {"text": "invalid"},  # Dictionary input
        ]
        
        for text in problematic_texts:
            try:
                result = analyzer.analyze_sentiment(text)
                # Should handle gracefully and return neutral sentiment
                assert isinstance(result, dict)
                assert 'score' in result
                assert 'label' in result
            except Exception as e:
                # If it raises an exception, it should be handled appropriately
                pytest.fail(f"Unexpected exception for input {text}: {e}")


class TestSentimentAnalyzerIntegration:
    """Integration tests for SentimentAnalyzer"""
    
    def test_real_world_feedback_samples(self):
        """Test with real-world feedback samples"""
        analyzer = SentimentAnalyzer()
        
        real_feedback = [
            "The delivery was very fast and the product quality exceeded my expectations!",
            "Poor customer service. Waited on hold for 45 minutes with no resolution.",
            "Product is decent for the price. Nothing extraordinary but gets the job done.",
            "Absolutely fantastic! Will definitely recommend to friends and family.",
            "Website checkout process was buggy and caused multiple failed transactions.",
        ]
        
        expected_sentiments = ['Positive', 'Negative', 'Neutral', 'Positive', 'Negative']
        
        for text, expected in zip(real_feedback, expected_sentiments):
            result = analyzer.analyze_sentiment(text)
            assert result['label'] == expected, f"Failed for: {text}"
    
    def test_multilingual_handling(self):
        """Test handling of non-English text (basic test)"""
        analyzer = SentimentAnalyzer()
        
        # These should not crash the analyzer
        non_english_texts = [
            "¡Excelente producto!",  # Spanish
            "Très bon service!",      # French
            "Sehr gut!",             # German
        ]
        
        for text in non_english_texts:
            result = analyzer.analyze_sentiment(text)
            assert isinstance(result, dict)
            assert 'score' in result
            assert 'label' in result
    
    def test_mixed_content_handling(self):
        """Test handling of mixed content (emojis, numbers, etc.)"""
        analyzer = SentimentAnalyzer()
        
        mixed_texts = [
            "Great product! 😊 5/5 stars ⭐⭐⭐⭐⭐",
            "Price: $29.99 - Good value 👍",
            "Ordered 3 items, received 2. Missing item #12345",
            "100% satisfied with my purchase! 💯",
        ]
        
        for text in mixed_texts:
            result = analyzer.analyze_sentiment(text)
            assert isinstance(result, dict)
            assert -1 <= result['score'] <= 1
            assert result['label'] in ['Positive', 'Negative', 'Neutral']


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])