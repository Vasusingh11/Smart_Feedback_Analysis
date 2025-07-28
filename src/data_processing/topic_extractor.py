"""
Topic Extraction Module
Extracts topics and themes from customer feedback using TF-IDF and clustering
"""

import pandas as pd
import numpy as np
import re
import string
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk
import logging
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

class TopicExtractor:
    """
    Advanced topic extraction using TF-IDF vectorization and K-means clustering
    Also supports LDA topic modeling for alternative topic discovery
    """
    
    def __init__(self, max_features: int = 100, min_df: int = 2, 
                 max_df: float = 0.95, ngram_range: Tuple[int, int] = (1, 2)):
        """
        Initialize topic extractor
        
        Args:
            max_features (int): Maximum number of features for TF-IDF
            min_df (int): Minimum document frequency
            max_df (float): Maximum document frequency ratio
            ngram_range (tuple): N-gram range for feature extraction
        """
        self._download_nltk_data()
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.ngram_range = ngram_range
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.logger = logging.getLogger(__name__)
        
        # Custom stopwords for feedback analysis
        self.custom_stopwords = {
            'product', 'service', 'company', 'customer', 'experience',
            'good', 'bad', 'great', 'terrible', 'amazing', 'awful',
            'like', 'love', 'hate', 'really', 'very', 'quite', 'pretty',
            'would', 'could', 'should', 'will', 'can', 'get', 'use', 'used'
        }
        self.stop_words.update(self.custom_stopwords)
        
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        required_datasets = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
        
        for dataset in required_datasets:
            try:
                nltk.data.find(f'tokenizers/{dataset}' if dataset == 'punkt' 
                              else f'corpora/{dataset}')
            except LookupError:
                nltk.download(dataset)
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for topic extraction
        
        Args:
            text (str): Raw text input
            
        Returns:
            str: Preprocessed text
        """
        if pd.isna(text) or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, emails, mentions
        text = re.sub(r'http\S+|www\.\S+|\S+@\S+|@\w+|#\w+', '', text)
        
        # Remove numbers but keep text like "5-star"
        text = re.sub(r'\b\d+\b', '', text)
        
        # Remove punctuation but keep meaningful separators
        text = text.translate(str.maketrans('', '', string.punctuation.replace('-', '').replace('_', '')))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Tokenize and lemmatize
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_topics_kmeans(self, texts: List[str], n_topics: int = 10) -> List[Dict[str, Any]]:
        """
        Extract topics using TF-IDF vectorization and K-means clustering
        
        Args:
            texts (List[str]): List of text documents
            n_topics (int): Number of topics to extract
            
        Returns:
            List[Dict[str, Any]]: List of extracted topics with keywords and metadata
        """
        if not texts or len(texts) < 2:
            self.logger.warning("Insufficient texts for topic extraction")
            return []
        
        # Preprocess texts
        self.logger.info("Preprocessing texts for topic extraction...")
        cleaned_texts = [self.preprocess_text(text) for text in texts]
        cleaned_texts = [text for text in cleaned_texts if text.strip()]
        
        if len(cleaned_texts) < 2:
            self.logger.warning("No valid texts after preprocessing")
            return []
        
        try:
            # TF-IDF Vectorization
            self.logger.info("Performing TF-IDF vectorization...")
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                ngram_range=self.ngram_range,
                stop_words='english'
            )
            
            tfidf_matrix = vectorizer.fit_transform(cleaned_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # K-means clustering
            self.logger.info(f"Performing K-means clustering with {n_topics} clusters...")
            n_clusters = min(n_topics, len(cleaned_texts))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Extract topics from clusters
            topics = []
            for cluster_id in range(n_clusters):
                # Get cluster center
                center = kmeans.cluster_centers_[cluster_id]
                
                # Get top terms for this cluster
                top_indices = center.argsort()[-10:][::-1]  # Top 10 terms
                top_terms = [feature_names[idx] for idx in top_indices]
                top_scores = [center[idx] for idx in top_indices]
                
                # Count documents in this cluster
                cluster_size = np.sum(cluster_labels == cluster_id)
                
                # Create topic name from top 2-3 terms
                topic_name = ' + '.join(top_terms[:3])
                
                # Calculate average TF-IDF score for topic coherence
                coherence_score = np.mean(top_scores[:5])
                
                topics.append({
                    'topic_id': cluster_id,
                    'topic_name': topic_name,
                    'keywords': top_terms,
                    'keyword_scores': top_scores,
                    'document_count': int(cluster_size),
                    'coherence_score': float(coherence_score),
                    'cluster_center': center.tolist()
                })
            
            # Sort topics by document count (most common first)
            topics.sort(key=lambda x: x['document_count'], reverse=True)
            
            self.logger.info(f"Successfully extracted {len(topics)} topics")
            return topics
            
        except Exception as e:
            self.logger.error(f"Topic extraction failed: {e}")
            return []
    
    def extract_topics_lda(self, texts: List[str], n_topics: int = 10) -> List[Dict[str, Any]]:
        """
        Extract topics using Latent Dirichlet Allocation (LDA)
        
        Args:
            texts (List[str]): List of text documents
            n_topics (int): Number of topics to extract
            
        Returns:
            List[Dict[str, Any]]: List of extracted topics with keywords and probabilities
        """
        if not texts or len(texts) < 2:
            return []
        
        # Preprocess texts
        cleaned_texts = [self.preprocess_text(text) for text in texts]
        cleaned_texts = [text for text in cleaned_texts if text.strip()]
        
        if len(cleaned_texts) < 2:
            return []
        
        try:
            # Use CountVectorizer for LDA (works better than TF-IDF)
            vectorizer = CountVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                ngram_range=self.ngram_range,
                stop_words='english'
            )
            
            doc_term_matrix = vectorizer.fit_transform(cleaned_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # LDA topic modeling
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=10,
                learning_method='online'
            )
            
            lda.fit(doc_term_matrix)
            
            # Extract topics
            topics = []
            for topic_idx, topic in enumerate(lda.components_):
                # Get top words for this topic
                top_indices = topic.argsort()[-10:][::-1]
                top_words = [feature_names[idx] for idx in top_indices]
                top_probabilities = [topic[idx] for idx in top_indices]
                
                # Create topic name
                topic_name = ' + '.join(top_words[:3])
                
                topics.append({
                    'topic_id': topic_idx,
                    'topic_name': topic_name,
                    'keywords': top_words,
                    'keyword_probabilities': top_probabilities,
                    'topic_distribution': topic.tolist()
                })
            
            return topics
            
        except Exception as e:
            self.logger.error(f"LDA topic extraction failed: {e}")
            return []
    
    def assign_topics_to_documents(self, texts: List[str], topics: List[Dict[str, Any]], 
                                  method: str = 'kmeans') -> List[Dict[str, Any]]:
        """
        Assign topics to individual documents
        
        Args:
            texts (List[str]): Original text documents
            topics (List[Dict[str, Any]]): Extracted topics
            method (str): Method used for topic extraction ('kmeans' or 'lda')
            
        Returns:
            List[Dict[str, Any]]: Document-topic assignments with relevance scores
        """
        if not texts or not topics:
            return []
        
        document_topics = []
        
        for doc_idx, text in enumerate(texts):
            if not text:
                continue
                
            cleaned_text = self.preprocess_text(text)
            if not cleaned_text:
                continue
            
            doc_topic_scores = []
            
            # Calculate relevance for each topic
            for topic in topics:
                relevance_score = self._calculate_topic_relevance(cleaned_text, topic['keywords'])
                
                if relevance_score > 0.1:  # Minimum relevance threshold
                    doc_topic_scores.append({
                        'document_id': doc_idx,
                        'topic_id': topic['topic_id'],
                        'topic_name': topic['topic_name'],
                        'relevance_score': relevance_score,
                        'keywords_found': self._get_matching_keywords(cleaned_text, topic['keywords'])
                    })
            
            # Sort by relevance and keep top 3 topics per document
            doc_topic_scores.sort(key=lambda x: x['relevance_score'], reverse=True)
            document_topics.extend(doc_topic_scores[:3])
        
        return document_topics
    
    def _calculate_topic_relevance(self, text: str, keywords: List[str]) -> float:
        """Calculate relevance score between text and topic keywords"""
        if not text or not keywords:
            return 0.0
        
        text_words = set(text.lower().split())
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_words)
        
        # Calculate relevance as ratio of matched keywords with length bonus
        relevance = keyword_matches / len(keywords)
        
        # Bonus for longer text (more context)
        length_bonus = min(len(text_words) / 50, 0.2)  # Max 20% bonus
        
        return min(relevance + length_bonus, 1.0)
    
    def _get_matching_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Get list of keywords that match in the text"""
        text_words = set(text.lower().split())
        return [keyword for keyword in keywords if keyword.lower() in text_words]
    
    def generate_topic_summary(self, topics: List[Dict[str, Any]], 
                              document_topics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive topic analysis summary
        
        Args:
            topics (List[Dict[str, Any]]): Extracted topics
            document_topics (List[Dict[str, Any]]): Document-topic assignments
            
        Returns:
            Dict[str, Any]: Topic analysis summary
        """
        if not topics:
            return {'total_topics': 0, 'topics_summary': []}
        
        # Count document assignments per topic
        topic_doc_counts = Counter(dt['topic_id'] for dt in document_topics)
        
        # Calculate average relevance per topic
        topic_relevances = {}
        for dt in document_topics:
            topic_id = dt['topic_id']
            if topic_id not in topic_relevances:
                topic_relevances[topic_id] = []
            topic_relevances[topic_id].append(dt['relevance_score'])
        
        # Create summary
        topics_summary = []
        for topic in topics:
            topic_id = topic['topic_id']
            doc_count = topic_doc_counts.get(topic_id, 0)
            avg_relevance = np.mean(topic_relevances.get(topic_id, [0]))
            
            topics_summary.append({
                'topic_id': topic_id,
                'topic_name': topic['topic_name'],
                'keywords': topic['keywords'][:5],  # Top 5 keywords
                'document_count': doc_count,
                'average_relevance': round(avg_relevance, 3),
                'percentage_of_docs': round((doc_count / len(set(dt['document_id'] for dt in document_topics))) * 100, 1) if document_topics else 0
            })
        
        # Sort by document count
        topics_summary.sort(key=lambda x: x['document_count'], reverse=True)
        
        return {
            'total_topics': len(topics),
            'total_documents_analyzed': len(set(dt['document_id'] for dt in document_topics)),
            'average_topics_per_document': round(len(document_topics) / len(set(dt['document_id'] for dt in document_topics)), 2) if document_topics else 0,
            'topics_summary': topics_summary
        }
    
    def create_wordcloud(self, texts: List[str], save_path: str = None) -> WordCloud:
        """
        Create word cloud from texts
        
        Args:
            texts (List[str]): List of text documents
            save_path (str): Optional path to save word cloud image
            
        Returns:
            WordCloud: Generated word cloud object
        """
        # Combine and preprocess all texts
        combined_text = ' '.join([self.preprocess_text(text) for text in texts if text])
        
        if not combined_text:
            self.logger.warning("No valid text for word cloud generation")
            return None
        
        # Create word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            max_words=100,
            stopwords=self.stop_words,
            collocations=False
        ).generate(combined_text)
        
        if save_path:
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Customer Feedback Word Cloud')
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return wordcloud

# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize extractor
    extractor = TopicExtractor()
    
    # Sample feedback texts
    sample_texts = [
        "The delivery was very slow and the packaging was damaged",
        "Great customer service team, they resolved my issue quickly",
        "Product quality is excellent, highly recommend",
        "Website is difficult to navigate, needs improvement",
        "Fast shipping and good packaging, very satisfied",
        "Poor customer support, took days to respond",
        "Love the product features, exactly what I needed",
        "Return process was complicated and frustrating",
        "Great value for money, will buy again",
        "Product arrived broken, very disappointed"
    ]
    
    # Extract topics using K-means
    print("Extracting topics using K-means...")
    kmeans_topics = extractor.extract_topics_kmeans(sample_texts, n_topics=5)
    
    print(f"\nFound {len(kmeans_topics)} topics:")
    for topic in kmeans_topics:
        print(f"Topic {topic['topic_id']}: {topic['topic_name']}")
        print(f"Keywords: {', '.join(topic['keywords'][:5])}")
        print(f"Documents: {topic['document_count']}")
        print("-" * 50)
    
    # Assign topics to documents
    print("\nAssigning topics to documents...")
    doc_topics = extractor.assign_topics_to_documents(sample_texts, kmeans_topics)
    
    for dt in doc_topics[:5]:  # Show first 5 assignments
        print(f"Document {dt['document_id']}: {dt['topic_name']} (relevance: {dt['relevance_score']:.3f})")
    
    # Generate summary
    print("\nTopic Analysis Summary:")
    summary = extractor.generate_topic_summary(kmeans_topics, doc_topics)
    print(f"Total topics: {summary['total_topics']}")
    print(f"Documents analyzed: {summary['total_documents_analyzed']}")
    
    for topic_sum in summary['topics_summary']:
        print(f"- {topic_sum['topic_name']}: {topic_sum['document_count']} docs ({topic_sum['percentage_of_docs']}%)")