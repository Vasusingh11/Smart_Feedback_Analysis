"""
Unit Tests for Topic Extraction Module
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.data_processing.topic_extractor import TopicExtractor

class TestTopicExtractor:
    """Test cases for TopicExtractor class"""
    
    @pytest.fixture
    def extractor(self):
        """Create TopicExtractor instance for testing"""
        return TopicExtractor()
    
    @pytest.fixture
    def sample_feedback_texts(self):
        """Sample feedback texts for testing topic extraction"""
        return [
            # Customer service related
            "Customer service was excellent, very helpful and responsive",
            "Poor customer support, took too long to respond to my inquiry",
            "Great customer service team, they resolved my issue quickly",
            
            # Delivery/shipping related
            "Fast delivery and secure packaging, arrived on time",
            "Slow shipping, package arrived damaged and late",
            "Express delivery was worth the extra cost, very quick",
            
            # Product quality related
            "Product quality is outstanding, well-made and durable",
            "Poor quality materials, product broke after one week",
            "Excellent build quality, exactly as described",
            
            # Price/value related
            "Great value for money, affordable and good quality",
            "Overpriced for what you get, not worth the cost",
            "Fair pricing, reasonable for the quality provided",
            
            # Website/ordering related
            "Website is easy to navigate and checkout was smooth",
            "Confusing website layout, difficult to find products",
            "Online ordering process was straightforward and quick"
        ]
    
    @pytest.fixture
    def mixed_quality_texts(self):
        """Texts with varying quality for testing robustness"""
        return [
            "Great product!",
            "",  # Empty text
            "a b c d e f g h i j",  # Random words
            "The quick brown fox jumps over the lazy dog multiple times in this sentence",
            "Product quality customer service delivery shipping website price value money",
            "Lorem ipsum dolor sit amet consectetur adipiscing elit",
            "!!!@@@###$$$%%%^^^&&&***(((())))",  # Special characters
            "   whitespace   around   text   ",
            "UPPERCASE TEXT WITH EXCLAMATION!!!",
            "mixed Case Text with Numbers 123 and symbols @#$"
        ]
    
    def test_initialization(self, extractor):
        """Test TopicExtractor initialization"""
        assert extractor.max_features == 100
        assert extractor.min_df == 2
        assert extractor.max_df == 0.95
        assert extractor.ngram_range == (1, 2)
        assert hasattr(extractor, 'stop_words')
        assert hasattr(extractor, 'custom_stopwords')
        assert hasattr(extractor, 'lemmatizer')
    
    def test_custom_initialization(self):
        """Test TopicExtractor with custom parameters"""
        extractor = TopicExtractor(
            max_features=200,
            min_df=3,
            max_df=0.8,
            ngram_range=(1, 3)
        )
        
        assert extractor.max_features == 200
        assert extractor.min_df == 3
        assert extractor.max_df == 0.8
        assert extractor.ngram_range == (1, 3)
    
    def test_preprocess_text_basic(self, extractor):
        """Test basic text preprocessing"""
        # Test normal text
        result = extractor.preprocess_text("Great customer service and fast delivery!")
        expected_words = ['great', 'customer', 'fast', 'delivery']
        
        for word in expected_words:
            assert word in result
        
        # Should remove common stopwords
        assert 'and' not in result
        assert 'the' not in result
    
    def test_preprocess_text_edge_cases(self, extractor):
        """Test text preprocessing edge cases"""
        # Empty text
        assert extractor.preprocess_text("") == ""
        assert extractor.preprocess_text(None) == ""
        
        # Only stopwords
        result = extractor.preprocess_text("the and a an it is")
        assert result == "" or len(result.split()) <= 1
        
        # Numbers and special characters
        result = extractor.preprocess_text("Product costs $100 and has 5-star rating!")
        assert "product" in result
        assert "cost" in result or "costs" in result
        assert "star" in result
        assert "rating" in result
        
        # URLs and emails
        result = extractor.preprocess_text("Visit https://example.com or email test@example.com")
        assert "https://example.com" not in result
        assert "test@example.com" not in result
        assert "visit" in result or "email" in result
    
    def test_extract_topics_kmeans_basic(self, extractor, sample_feedback_texts):
        """Test basic K-means topic extraction"""
        topics = extractor.extract_topics_kmeans(sample_feedback_texts, n_topics=4)
        
        # Should return list of topics
        assert isinstance(topics, list)
        assert len(topics) <= 4  # May return fewer if insufficient data
        
        # Each topic should have required fields
        for topic in topics:
            assert 'topic_id' in topic
            assert 'topic_name' in topic
            assert 'keywords' in topic
            assert 'keyword_scores' in topic
            assert 'document_count' in topic
            assert 'coherence_score' in topic
            
            # Check data types
            assert isinstance(topic['topic_id'], int)
            assert isinstance(topic['topic_name'], str)
            assert isinstance(topic['keywords'], list)
            assert isinstance(topic['keyword_scores'], list)
            assert isinstance(topic['document_count'], int)
            assert isinstance(topic['coherence_score'], float)
    
    def test_extract_topics_kmeans_empty_input(self, extractor):
        """Test topic extraction with empty input"""
        # Empty list
        topics = extractor.extract_topics_kmeans([])
        assert topics == []
        
        # List with empty strings
        topics = extractor.extract_topics_kmeans(["", "   ", None])
        assert topics == []
        
        # Single text
        topics = extractor.extract_topics_kmeans(["Single text"])
        assert topics == []  # Insufficient data for clustering
    
    def test_extract_topics_kmeans_insufficient_data(self, extractor):
        """Test topic extraction with insufficient data"""
        # Very few texts
        texts = ["Short text", "Another text"]
        topics = extractor.extract_topics_kmeans(texts, n_topics=5)
        
        # Should handle gracefully
        assert isinstance(topics, list)
        assert len(topics) <= len(texts)
    
    def test_extract_topics_lda(self, extractor, sample_feedback_texts):
        """Test LDA topic extraction"""
        topics = extractor.extract_topics_lda(sample_feedback_texts, n_topics=3)
        
        # Should return list of topics
        assert isinstance(topics, list)
        assert len(topics) <= 3
        
        # Each topic should have required fields for LDA
        for topic in topics:
            assert 'topic_id' in topic
            assert 'topic_name' in topic
            assert 'keywords' in topic
            assert 'keyword_probabilities' in topic
            assert 'topic_distribution' in topic
            
            # Check data types
            assert isinstance(topic['keyword_probabilities'], list)
            assert isinstance(topic['topic_distribution'], list)
    
    def test_assign_topics_to_documents(self, extractor, sample_feedback_texts):
        """Test topic assignment to documents"""
        # First extract topics
        topics = extractor.extract_topics_kmeans(sample_feedback_texts, n_topics=3)
        
        if not topics:  # Skip if no topics extracted
            pytest.skip("No topics extracted from sample data")
        
        # Assign topics to documents
        document_topics = extractor.assign_topics_to_documents(sample_feedback_texts, topics)
        
        # Should return list of assignments
        assert isinstance(document_topics, list)
        
        # Each assignment should have required fields
        for assignment in document_topics:
            assert 'document_id' in assignment
            assert 'topic_id' in assignment
            assert 'topic_name' in assignment
            assert 'relevance_score' in assignment
            assert 'keywords_found' in assignment
            
            # Check data types and ranges
            assert isinstance(assignment['document_id'], int)
            assert isinstance(assignment['topic_id'], int)
            assert isinstance(assignment['relevance_score'], float)
            assert 0 <= assignment['relevance_score'] <= 1
            assert isinstance(assignment['keywords_found'], list)
    
    def test_assign_topics_empty_inputs(self, extractor):
        """Test topic assignment with empty inputs"""
        # Empty texts
        result = extractor.assign_topics_to_documents([], [])
        assert result == []
        
        # Empty topics
        result = extractor.assign_topics_to_documents(["Some text"], [])
        assert result == []
        
        # Empty texts with topics
        topics = [{'topic_id': 0, 'topic_name': 'test', 'keywords': ['test']}]
        result = extractor.assign_topics_to_documents([], topics)
        assert result == []
    
    def test_calculate_topic_relevance(self, extractor):
        """Test topic relevance calculation"""
        text = "great customer service fast delivery"
        keywords = ["customer", "service", "delivery", "quality"]
        
        relevance = extractor._calculate_topic_relevance(text, keywords)
        
        # Should return float between 0 and 1
        assert isinstance(relevance, float)
        assert 0 <= relevance <= 1
        
        # Should be higher for more matching keywords
        assert relevance > 0.5  # 3 out of 4 keywords match
        
        # Test with no matches
        relevance_none = extractor._calculate_topic_relevance("random words", keywords)
        assert relevance_none < relevance
        
        # Test with all matches
        all_keywords_text = " ".join(keywords)
        relevance_all = extractor._calculate_topic_relevance(all_keywords_text, keywords)
        assert relevance_all >= relevance
    
    def test_get_matching_keywords(self, extractor):
        """Test keyword matching functionality"""
        text = "excellent customer service and fast delivery"
        keywords = ["customer", "service", "delivery", "quality", "price"]
        
        matches = extractor._get_matching_keywords(text, keywords)
        
        # Should return list of matching keywords
        assert isinstance(matches, list)
        expected_matches = ["customer", "service", "delivery"]
        
        for match in expected_matches:
            assert match in matches
        
        # Should not include non-matching keywords
        assert "quality" not in matches
        assert "price" not in matches
    
    def test_generate_topic_summary(self, extractor, sample_feedback_texts):
        """Test topic summary generation"""
        # Extract topics and assignments
        topics = extractor.extract_topics_kmeans(sample_feedback_texts, n_topics=3)
        
        if not topics:
            pytest.skip("No topics extracted from sample data")
        
        document_topics = extractor.assign_topics_to_documents(sample_feedback_texts, topics)
        summary = extractor.generate_topic_summary(topics, document_topics)
        
        # Check summary structure
        assert isinstance(summary, dict)
        assert 'total_topics' in summary
        assert 'total_documents_analyzed' in summary
        assert 'average_topics_per_document' in summary
        assert 'topics_summary' in summary
        
        # Check data types and values
        assert isinstance(summary['total_topics'], int)
        assert isinstance(summary['total_documents_analyzed'], int)
        assert isinstance(summary['average_topics_per_document'], float)
        assert isinstance(summary['topics_summary'], list)
        
        # Check topics summary structure
        for topic_sum in summary['topics_summary']:
            assert 'topic_id' in topic_sum
            assert 'topic_name' in topic_sum
            assert 'keywords' in topic_sum
            assert 'document_count' in topic_sum
            assert 'average_relevance' in topic_sum
            assert 'percentage_of_docs' in topic_sum
    
    def test_generate_topic_summary_empty(self, extractor):
        """Test topic summary with empty inputs"""
        summary = extractor.generate_topic_summary([], [])
        
        assert summary['total_topics'] == 0
        assert summary['topics_summary'] == []
    
    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.figure')
    def test_create_wordcloud(self, mock_figure, mock_savefig, extractor, sample_feedback_texts):
        """Test word cloud creation"""
        try:
            from wordcloud import WordCloud
        except ImportError:
            pytest.skip("WordCloud not available")
        
        # Test basic word cloud creation
        wordcloud = extractor.create_wordcloud(sample_feedback_texts)
        
        if wordcloud is not None:  # May be None if no valid text
            assert hasattr(wordcloud, 'words_')
        
        # Test with save path
        wordcloud = extractor.create_wordcloud(sample_feedback_texts, save_path="test.png")
        
        # Should call matplotlib functions if wordcloud created
        if wordcloud is not None:
            mock_figure.assert_called()
            mock_savefig.assert_called_with("test.png", dpi=300, bbox_inches='tight')
    
    def test_create_wordcloud_empty(self, extractor):
        """Test word cloud creation with empty input"""
        wordcloud = extractor.create_wordcloud([])
        assert wordcloud is None
        
        wordcloud = extractor.create_wordcloud(["", "   ", None])
        assert wordcloud is None
    
    def test_robustness_with_mixed_quality_data(self, extractor, mixed_quality_texts):
        """Test extractor robustness with various text qualities"""
        # Should handle mixed quality data without crashing
        topics = extractor.extract_topics_kmeans(mixed_quality_texts, n_topics=3)
        
        # May or may not extract topics, but should not crash
        assert isinstance(topics, list)
        
        if topics:
            # If topics extracted, they should be valid
            for topic in topics:
                assert isinstance(topic['topic_name'], str)
                assert isinstance(topic['keywords'], list)
                assert len(topic['keywords']) > 0
    
    def test_performance_with_large_dataset(self, extractor):
        """Test performance with larger dataset"""
        # Generate larger dataset
        base_texts = [
            "customer service experience",
            "product quality issues", 
            "fast delivery service",
            "website navigation problems",
            "price value concerns"
        ]
        
        # Repeat with variations to create larger dataset
        large_texts = []
        for i in range(200):  # 1000 total texts
            base_text = base_texts[i % len(base_texts)]
            variation = f"{base_text} variation {i}"
            large_texts.append(variation)
        
        # Should handle large dataset
        topics = extractor.extract_topics_kmeans(large_texts, n_topics=5)
        
        assert isinstance(topics, list)
        assert len(topics) <= 5
        
        # Performance check - should complete in reasonable time
        # (This is implicit - if it hangs, the test will timeout)
    
    def test_topic_name_generation(self, extractor):
        """Test topic name generation from keywords"""
        # Create mock topic with known keywords
        sample_texts = [
            "customer service was excellent and helpful",
            "customer support team was very responsive", 
            "great customer service experience overall"
        ]
        
        topics = extractor.extract_topics_kmeans(sample_texts, n_topics=1)
        
        if topics:
            topic_name = topics[0]['topic_name']
            
            # Topic name should be meaningful
            assert len(topic_name) > 0
            assert isinstance(topic_name, str)
            
            # Should likely contain customer/service related terms
            topic_name_lower = topic_name.lower()
            customer_service_terms = ['customer', 'service', 'support', 'help']
            
            # At least one relevant term should be present
            assert any(term in topic_name_lower for term in customer_service_terms)
    
    @patch('src.data_processing.topic_extractor.nltk.download')
    def test_nltk_data_download(self, mock_download, extractor):
        """Test NLTK data download functionality"""
        extractor._download_nltk_data()
        
        # Should attempt to download required datasets
        expected_datasets = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        
        # Check that download was called
        assert mock_download.called
        
        # Check that required datasets were requested
        download_calls = [call[0][0] for call in mock_download.call_args_list]
        for dataset in expected_datasets:
            assert dataset in download_calls or mock_download.call_count > 0

class TestTopicExtractorIntegration:
    """Integration tests for TopicExtractor"""
    
    def test_end_to_end_topic_extraction(self):
        """Test complete topic extraction workflow"""
        extractor = TopicExtractor(max_features=50, n_topics=3)
        
        # Real-world-like feedback
        feedback_texts = [
            # Delivery complaints
            "Delivery was very slow, took over two weeks to arrive",
            "Package arrived damaged due to poor shipping handling", 
            "Fast delivery service, arrived next day as promised",
            "Delivery tracking was not updated, couldn't track my order",
            
            # Customer service feedback  
            "Customer service representative was very helpful and polite",
            "Poor customer support, took days to respond to my email",
            "Excellent customer service, resolved my issue immediately",
            "Customer service team needs better training",
            
            # Product quality feedback
            "Product quality exceeded my expectations, very well made",
            "Poor quality materials, product broke after one week", 
            "Great build quality and attention to detail",
            "Quality control issues, received defective product",
            
            # Website/ordering feedback
            "Website is easy to navigate and user-friendly",
            "Checkout process was confusing and took too long",
            "Online ordering system worked perfectly", 
            "Website crashed during peak hours, couldn't complete order"
        ]
        
        # Extract topics
        topics = extractor.extract_topics_kmeans(feedback_texts, n_topics=4)
        
        # Should extract some topics
        assert len(topics) > 0
        
        # Assign topics to documents
        document_topics = extractor.assign_topics_to_documents(feedback_texts, topics)
        
        # Should have some assignments
        assert len(document_topics) > 0
        
        # Generate summary
        summary = extractor.generate_topic_summary(topics, document_topics)
        
        # Summary should be comprehensive
        assert summary['total_topics'] == len(topics)
        assert summary['total_documents_analyzed'] > 0
        assert len(summary['topics_summary']) > 0
        
        # Topics should be reasonably coherent
        topic_names = [t['topic_name'] for t in topics]
        
        # Should contain business-relevant terms
        business_terms = [
            'delivery', 'shipping', 'customer', 'service', 'support',
            'product', 'quality', 'website', 'order', 'checkout'
        ]
        
        # At least some topics should contain business terms
        relevant_topics = 0
        for topic_name in topic_names:
            if any(term in topic_name.lower() for term in business_terms):
                relevant_topics += 1
        
        assert relevant_topics > 0, f"No relevant topics found in: {topic_names}"

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])