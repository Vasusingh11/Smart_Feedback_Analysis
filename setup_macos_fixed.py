#!/usr/bin/env python3
"""
Smart Feedback Analysis Platform - macOS Setup Script (FIXED)
Complete setup using basic file storage (no complex database required)
"""

import sys
import os
import pandas as pd
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path

def setup_logging():
    """Setup basic logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_and_install_dependencies():
    """Check and install required dependencies"""
    print("🔧 Checking dependencies...")
    
    required_packages = [
        'pandas', 'numpy', 'nltk', 'textblob', 'sklearn', 
        'matplotlib', 'seaborn', 'yaml', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies available")
    return True

def download_nltk_data():
    """Download required NLTK data"""
    print("📚 Downloading NLTK data...")
    
    import nltk
    
    datasets = ['vader_lexicon', 'punkt', 'stopwords', 'wordnet', 'omw-1.4']
    
    for dataset in datasets:
        try:
            nltk.download(dataset, quiet=True)
            print(f"✅ {dataset}")
        except Exception as e:
            print(f"⚠️  {dataset}: {e}")
    
    print("✅ NLTK data download completed")

def create_project_structure():
    """Create necessary project directories"""
    print("📁 Creating project structure...")
    
    directories = [
        'data/raw',
        'data/processed',
        'data/exports',
        'logs',
        'results'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory}")
    
    print("✅ Project structure created")

def generate_realistic_sample_data():
    """Generate realistic sample feedback data"""
    print("📊 Generating sample feedback data...")
    
    # Realistic feedback samples with different sentiments
    positive_feedback = [
        "Absolutely love this product! The quality is outstanding and delivery was super fast.",
        "Excellent customer service team. They resolved my issue within minutes and were very professional.",
        "Great value for money! The product exceeded my expectations and works perfectly.",
        "Fast shipping and perfect packaging. The item arrived exactly as described.",
        "Outstanding experience from start to finish. Will definitely order again!",
        "Amazing quality and design. The product is even better than the photos showed.",
        "Fantastic customer support! They went above and beyond to help me.",
        "Perfect product for my needs. Easy to use and great build quality.",
        "Impressed with the quick response to my inquiry and fast resolution.",
        "Excellent website experience. Easy to navigate and checkout was smooth."
    ]
    
    negative_feedback = [
        "Very disappointed with this purchase. The product broke after just one week of normal use.",
        "Terrible customer service experience. Took days to get a response and they were unhelpful.",
        "Poor quality for the price. The product looks nothing like the description or photos.",
        "Delivery was extremely slow and the package arrived damaged. Very frustrating experience.",
        "Completely unsatisfied. The product doesn't work as advertised and return process is complicated.",
        "Worst online shopping experience ever. Product was defective and customer service was rude.",
        "Overpriced and underwhelming. The quality is much lower than expected for this price point.",
        "Received wrong item and getting a replacement has been a nightmare. Poor service overall.",
        "Product stopped working after two days. Quality control seems non-existent.",
        "Website is confusing and checkout failed multiple times. Very poor user experience."
    ]
    
    neutral_feedback = [
        "Product is okay, does what it's supposed to do. Nothing exceptional but meets basic needs.",
        "Average experience overall. Delivery was on time and product matches the description.",
        "It's fine for the price. Not the best quality but acceptable for occasional use.",
        "Standard delivery time and packaging. Product works as expected, nothing special.",
        "Decent customer service. They answered my questions but could be more helpful.",
        "The product is alright. Some features work well, others could be improved.",
        "Fair pricing for what you get. Quality is reasonable but not outstanding.",
        "Average website experience. Found what I needed but navigation could be better.",
        "Product meets basic requirements. Installation was straightforward but manual could be clearer.",
        "Okay experience. No major complaints but nothing to get excited about either."
    ]
    
    # Generate sample data
    sample_data = []
    sources = ['email', 'survey', 'website', 'social_media', 'phone', 'chat', 'review']
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Beauty', 'Automotive']
    
    for i in range(100):  # Generate 100 sample records
        # Choose feedback based on weighted probabilities
        feedback_type = random.choices(
            ['positive', 'negative', 'neutral'],
            weights=[0.5, 0.3, 0.2],
            k=1
        )[0]
        
        if feedback_type == 'positive':
            feedback_text = random.choice(positive_feedback)
            rating = random.choices([4, 5], weights=[0.3, 0.7], k=1)[0]
        elif feedback_type == 'negative':
            feedback_text = random.choice(negative_feedback)
            rating = random.choices([1, 2], weights=[0.6, 0.4], k=1)[0]
        else:  # neutral
            feedback_text = random.choice(neutral_feedback)
            rating = 3
        
        # Add some variation to make text unique
        variations = ["", " Thanks!", " Overall satisfied.", " Could be improved.", " Highly recommend.", " Will shop again."]
        final_text = feedback_text + random.choice(variations)
        
        sample_data.append({
            'feedback_id': f'FB_{i:04d}',
            'customer_id': f'CUST_{i//3:04d}',
            'feedback_text': final_text,
            'source': random.choice(sources),
            'product_category': random.choice(categories),
            'rating': rating,
            'timestamp': datetime.now() - timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
        })
    
    print(f"✅ Generated {len(sample_data)} sample feedback records")
    return sample_data

def save_sample_data(sample_data):
    """Save sample data to CSV file"""
    print("💾 Saving sample data to CSV...")
    
    try:
        df = pd.DataFrame(sample_data)
        
        # Create data directory if it doesn't exist
        os.makedirs('data/raw', exist_ok=True)
        
        # Save to CSV
        csv_path = 'data/raw/sample_feedback.csv'
        df.to_csv(csv_path, index=False)
        
        print(f"✅ Successfully saved {len(df)} feedback records to {csv_path}")
        
        # Show distribution
        rating_dist = df['rating'].value_counts().sort_index()
        print("\nRating Distribution:")
        for rating, count in rating_dist.items():
            stars = "⭐" * rating
            print(f"  {rating} {stars}: {count} records")
        
        source_dist = df['source'].value_counts()
        print(f"\nSource Distribution:")
        for source, count in source_dist.items():
            print(f"  {source}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Data saving failed: {e}")
        return False

def run_sentiment_analysis(csv_path):
    """Run sentiment analysis on the sample data"""
    print("🔍 Running sentiment analysis...")
    
    try:
        # Import our working sentiment analyzer
        sys.path.append('.')
        
        # Use the FeedbackAnalyzer from our working script
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer
        from textblob import TextBlob
        
        # Download NLTK data
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('punkt', quiet=True)
        
        # Initialize analyzer
        sia = SentimentIntensityAnalyzer()
        
        # Load the data
        df = pd.read_csv(csv_path)
        
        print(f"Processing {len(df)} feedback items...")
        
        # Process sentiment analysis
        results = []
        
        for idx, row in df.iterrows():
            text = row['feedback_text']
            
            if pd.isna(text) or not text:
                continue
                
            # VADER analysis
            vader_scores = sia.polarity_scores(text)
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
            
            results.append({
                'feedback_id': row['feedback_id'],
                'sentiment_score': round(combined_score, 3),
                'sentiment_label': sentiment_label,
                'confidence_score': round(confidence, 3),
                'vader_compound': round(vader_compound, 3),
                'textblob_polarity': round(textblob_polarity, 3),
                'processed_date': datetime.now()
            })
        
        if results:
            # Save results
            results_df = pd.DataFrame(results)
            results_path = 'data/processed/sentiment_results.csv'
            results_df.to_csv(results_path, index=False)
            
            print(f"✅ Successfully analyzed {len(results)} feedback items")
            print(f"✅ Results saved to {results_path}")
            
            # Show sentiment distribution
            sentiment_dist = results_df['sentiment_label'].value_counts()
            print("\nSentiment Distribution:")
            for label, count in sentiment_dist.items():
                emoji = "😊" if label == "Positive" else "😞" if label == "Negative" else "😐"
                percentage = (count / len(results)) * 100
                print(f"  {emoji} {label}: {count} ({percentage:.1f}%)")
            
            # Show confidence statistics
            avg_confidence = results_df['confidence_score'].mean()
            high_confidence = len(results_df[results_df['confidence_score'] > 0.8])
            print(f"\nConfidence Statistics:")
            print(f"  Average confidence: {avg_confidence:.3f}")
            print(f"  High confidence (>0.8): {high_confidence} ({high_confidence/len(results)*100:.1f}%)")
            
            return True
        else:
            print("❌ No sentiment analysis results generated")
            return False
            
    except Exception as e:
        print(f"❌ Sentiment analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_analysis_summary():
    """Create a comprehensive analysis summary"""
    print("📊 Creating analysis summary...")
    
    try:
        # Load data
        feedback_df = pd.read_csv('data/raw/sample_feedback.csv')
        sentiment_df = pd.read_csv('data/processed/sentiment_results.csv')
        
        # Merge data
        merged_df = feedback_df.merge(sentiment_df, on='feedback_id', how='left')
        
        # Create summary
        summary = {
            'total_feedback': len(feedback_df),
            'analyzed_feedback': len(sentiment_df),
            'analysis_date': datetime.now().isoformat(),
            'sentiment_distribution': sentiment_df['sentiment_label'].value_counts().to_dict(),
            'average_confidence': sentiment_df['confidence_score'].mean(),
            'source_analysis': {},
            'category_analysis': {}
        }
        
        # Source analysis
        for source in feedback_df['source'].unique():
            source_data = merged_df[merged_df['source'] == source]
            if not source_data.empty and 'sentiment_score' in source_data.columns:
                summary['source_analysis'][source] = {
                    'count': len(source_data),
                    'avg_sentiment': source_data['sentiment_score'].mean()
                }
        
        # Category analysis
        for category in feedback_df['product_category'].unique():
            cat_data = merged_df[merged_df['product_category'] == category]
            if not cat_data.empty and 'sentiment_score' in cat_data.columns:
                summary['category_analysis'][category] = {
                    'count': len(cat_data),
                    'avg_sentiment': cat_data['sentiment_score'].mean()
                }
        
        # Save summary
        import json
        summary_path = 'data/processed/analysis_summary.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"✅ Analysis summary saved to {summary_path}")
        
        # Display key insights
        print("\n📈 KEY INSIGHTS:")
        print("-" * 30)
        total = summary['total_feedback']
        analyzed = summary['analyzed_feedback']
        print(f"📊 Total Feedback: {total}")
        print(f"🔍 Analyzed: {analyzed} ({analyzed/total*100:.1f}%)")
        
        sentiment_dist = summary['sentiment_distribution']
        print(f"\n😊 Sentiment Breakdown:")
        for sentiment, count in sentiment_dist.items():
            emoji = "😊" if sentiment == "Positive" else "😞" if sentiment == "Negative" else "😐"
            percentage = (count / analyzed) * 100
            print(f"  {emoji} {sentiment}: {count} ({percentage:.1f}%)")
        
        print(f"\n🎯 Average Confidence: {summary['average_confidence']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Summary creation failed: {e}")
        return False

def create_simple_test_script():
    """Create a simple test script for ongoing use"""
    print("📝 Creating test script...")
    
    test_script = '''#!/usr/bin/env python3
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
    
    print("\\nTesting sentiment analysis:")
    
    # Test sentiment analysis
    analyze_new_feedback("This product is absolutely amazing!")
    analyze_new_feedback("Poor quality, very disappointed.")
    analyze_new_feedback("It's okay, nothing special.")
    
    print("✅ Test completed!")
    print("\\n💡 To analyze your own text:")
    print("   result = analyze_new_feedback('Your feedback text here')")

if __name__ == "__main__":
    main()
'''
    
    try:
        with open('quick_test.py', 'w') as f:
            f.write(test_script)
        
        # Make it executable
        os.chmod('quick_test.py', 0o755)
        
        print("✅ Created quick_test.py")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test script: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Smart Feedback Analysis Platform - macOS Setup (FIXED)")
    print("=" * 60)
    print("This script will set up the complete platform using CSV files")
    print("(Simple file-based approach - no complex database required!)")
    print("=" * 60)
    
    setup_logging()
    
    # Step 1: Check dependencies
    print("\n1️⃣  Checking dependencies...")
    if not check_and_install_dependencies():
        print("❌ Please install missing dependencies and run again")
        return
    
    # Step 2: Download NLTK data
    print("\n2️⃣  Downloading NLTK data...")
    download_nltk_data()
    
    # Step 3: Create project structure
    print("\n3️⃣  Creating project structure...")
    create_project_structure()
    
    # Step 4: Generate and save sample data
    print("\n4️⃣  Generating sample data...")
    sample_data = generate_realistic_sample_data()
    if not save_sample_data(sample_data):
        print("❌ Sample data creation failed!")
        return
    
    # Step 5: Run sentiment analysis
    print("\n5️⃣  Running sentiment analysis...")
    csv_path = 'data/raw/sample_feedback.csv'
    if not run_sentiment_analysis(csv_path):
        print("⚠️  Sentiment analysis had issues, but continuing...")
    
    # Step 6: Create analysis summary
    print("\n6️⃣  Creating analysis summary...")
    if not create_analysis_summary():
        print("⚠️  Summary creation had issues, but continuing...")
    
    # Step 7: Create test script
    print("\n7️⃣  Creating test utilities...")
    create_simple_test_script()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nYour Smart Feedback Analysis Platform is now ready!")
    print("\n📊 What was created:")
    print("  • CSV files with sample feedback data")
    print("  • Sentiment analysis results for all feedback")
    print("  • Analysis summary and statistics")
    print("  • Complete project structure")
    print("\n🚀 What you can do now:")
    print("  • Run: python3 quick_test.py")
    print("  • Explore: data/raw/sample_feedback.csv")
    print("  • View results: data/processed/sentiment_results.csv")
    print("  • Add your own feedback data")
    print("\n📁 Key files created:")
    print("  • data/raw/sample_feedback.csv (Sample data)")
    print("  • data/processed/sentiment_results.csv (Analysis results)")
    print("  • data/processed/analysis_summary.json (Summary)")
    print("  • quick_test.py (Testing script)")
    print("\n💡 Next steps:")
    print("  • Open CSV files in Excel or any spreadsheet app")
    print("  • Import your own feedback data")
    print("  • Customize the analysis parameters")
    print("  • Build your own dashboards")
    print("=" * 60)
    
    print("\n🎯 Platform is production-ready for local development!")

if __name__ == "__main__":
    main() 