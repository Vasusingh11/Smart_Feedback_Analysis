-- Smart Feedback Analysis Platform - Sample Data
-- Generate realistic sample data for testing and demonstration

USE feedback_analysis;
GO

-- Clear existing data (use with caution in production)
-- DELETE FROM topic_analysis;
-- DELETE FROM sentiment_analysis;
-- DELETE FROM satisfaction_metrics;
-- DELETE FROM feedback;
-- GO

-- Insert sample feedback data
-- This creates diverse, realistic feedback across different categories and sentiments

-- Positive feedback samples
INSERT INTO feedback (customer_id, feedback_text, source, product_category, rating, timestamp) VALUES
('CUST_0001', 'Absolutely love this product! The quality exceeded my expectations and delivery was super fast. Will definitely order again soon.', 'email', 'Electronics', 5, DATEADD(day, -1, GETDATE())),
('CUST_0002', 'Outstanding customer service! Sarah from support helped me resolve my issue within minutes. Very impressed with the response time.', 'survey', 'Customer Service', 5, DATEADD(day, -2, GETDATE())),
('CUST_0003', 'Great value for money. The product works exactly as described and the packaging was environmentally friendly. Highly recommend!', 'website', 'Home', 4, DATEADD(day, -3, GETDATE())),
('CUST_0004', 'Amazing user interface! So intuitive and easy to navigate. My whole family can use it without any problems.', 'social_media', 'Electronics', 5, DATEADD(day, -1, GETDATE())),
('CUST_0005', 'Fast shipping and excellent product quality. Arrived earlier than expected and in perfect condition.', 'email', 'Clothing', 4, DATEADD(day, -4, GETDATE())),
('CUST_0006', 'Wonderful experience from start to finish. The website is user-friendly and checkout was seamless.', 'website', 'Electronics', 5, DATEADD(day, -2, GETDATE())),
('CUST_0007', 'Perfect fit and great material quality. Exactly what I was looking for and at a reasonable price.', 'survey', 'Clothing', 4, DATEADD(day, -5, GETDATE())),
('CUST_0008', 'Excellent features and functionality. This has made my daily routine so much easier and more efficient.', 'email', 'Home', 5, DATEADD(day, -3, GETDATE())),
('CUST_0001', 'Second order and still impressed! Consistent quality and reliable service. Keep up the great work!', 'email', 'Electronics', 5, DATEADD(day, -6, GETDATE())),
('CUST_0009', 'Beautiful design and works perfectly. Installation was straightforward with clear instructions provided.', 'website', 'Home', 4, DATEADD(day, -7, GETDATE()));

-- Negative feedback samples
INSERT INTO feedback (customer_id, feedback_text, source, product_category, rating, timestamp) VALUES
('CUST_0010', 'Very disappointed with the product quality. It broke after just one week of normal use. Poor value for money.', 'email', 'Electronics', 1, DATEADD(day, -1, GETDATE())),
('CUST_0011', 'Terrible customer support experience. Waited on hold for over an hour and the representative was unhelpful and rude.', 'phone', 'Customer Service', 1, DATEADD(day, -2, GETDATE())),
('CUST_0012', 'Product arrived damaged and the return process is unnecessarily complicated. Very frustrating experience overall.', 'email', 'Home', 2, DATEADD(day, -3, GETDATE())),
('CUST_0013', 'Misleading product description. What I received was nothing like what was advertised on the website.', 'social_media', 'Clothing', 1, DATEADD(day, -1, GETDATE())),
('CUST_0014', 'Extremely slow delivery and poor packaging. The item was loose in a box with no protection.', 'survey', 'Electronics', 2, DATEADD(day, -4, GETDATE())),
('CUST_0015', 'Website is confusing and checkout process keeps failing. Tried multiple times with different browsers.', 'website', 'Technology', 2, DATEADD(day, -2, GETDATE())),
('CUST_0016', 'Overpriced for the quality provided. Similar products available elsewhere for much better value.', 'email', 'Home', 2, DATEADD(day, -5, GETDATE())),
('CUST_0017', 'Poor build quality and cheap materials. Expected much better given the price point and brand reputation.', 'survey', 'Electronics', 1, DATEADD(day, -3, GETDATE())),
('CUST_0018', 'Size was completely wrong despite following the size guide. Return shipping costs are unreasonably high.', 'email', 'Clothing', 2, DATEADD(day, -6, GETDATE())),
('CUST_0010', 'Still no response to my complaint from last week. This level of customer service is unacceptable.', 'email', 'Customer Service', 1, DATEADD(day, -7, GETDATE()));

-- Neutral feedback samples
INSERT INTO feedback (customer_id, feedback_text, source, product_category, rating, timestamp) VALUES
('CUST_0019', 'Average product that does the job. Nothing special but works as expected. Delivery was on time.', 'survey', 'Home', 3, DATEADD(day, -1, GETDATE())),
('CUST_0020', 'Okay experience overall. Product is functional but could use some improvements in design and usability.', 'website', 'Electronics', 3, DATEADD(day, -2, GETDATE())),
('CUST_0021', 'Standard quality for the price range. No major complaints but nothing particularly impressive either.', 'email', 'Clothing', 3, DATEADD(day, -3, GETDATE())),
('CUST_0022', 'Decent customer service response time. Issue was resolved but took longer than I would have preferred.', 'phone', 'Customer Service', 3, DATEADD(day, -1, GETDATE())),
('CUST_0023', 'Fair pricing and reasonable quality. Product meets basic requirements but lacks premium features.', 'survey', 'Electronics', 3, DATEADD(day, -4, GETDATE())),
('CUST_0024', 'Normal delivery time and standard packaging. Product condition was acceptable upon arrival.', 'website', 'Home', 3, DATEADD(day, -2, GETDATE())),
('CUST_0025', 'Basic functionality works fine. User interface could be more intuitive but manageable with practice.', 'email', 'Technology', 3, DATEADD(day, -5, GETDATE())),
('CUST_0026', 'Average shopping experience. Website navigation is okay but could be more streamlined and efficient.', 'website', 'General', 3, DATEADD(day, -3, GETDATE())),
('CUST_0027', 'Product arrived as described. Quality is acceptable for the price point but room for improvement.', 'survey', 'Clothing', 3, DATEADD(day, -6, GETDATE())),
('CUST_0028', 'Standard customer service interaction. Representative was polite but couldn''t fully resolve my concern.', 'chat', 'Customer Service', 3, DATEADD(day, -7, GETDATE()));

-- Additional diverse feedback samples
INSERT INTO feedback (customer_id, feedback_text, source, product_category, rating, timestamp) VALUES
-- More positive feedback
('CUST_0029', 'Exceptional build quality and attention to detail. This product clearly shows superior craftsmanship and engineering.', 'email', 'Electronics', 5, DATEADD(day, -8, GETDATE())),
('CUST_0030', 'Love the eco-friendly packaging and sustainable materials. Great to see a company caring about the environment.', 'social_media', 'Home', 4, DATEADD(day, -9, GETDATE())),
('CUST_0031', 'Quick and easy installation process. The instruction manual was clear and all necessary tools were included.', 'website', 'Home', 4, DATEADD(day, -10, GETDATE())),
('CUST_0032', 'Fantastic color options and stylish design. Looks great and functions even better than I expected.', 'survey', 'Clothing', 5, DATEADD(day, -8, GETDATE())),

-- More negative feedback
('CUST_0033', 'Battery life is much shorter than advertised. Needs charging constantly which defeats the purpose of portability.', 'email', 'Electronics', 2, DATEADD(day, -9, GETDATE())),
('CUST_0034', 'Size runs very small compared to other brands. Had to return and reorder which caused unnecessary delay.', 'survey', 'Clothing', 2, DATEADD(day, -10, GETDATE())),
('CUST_0035', 'Missing parts in the package and customer service was slow to respond. Very frustrating experience.', 'email', 'Home', 1, DATEADD(day, -11, GETDATE())),
('CUST_0036', 'Poor value proposition. Competitors offer better features for the same price point.', 'social_media', 'Electronics', 2, DATEADD(day, -9, GETDATE())),

-- Mixed sentiment feedback
('CUST_0037', 'Great product design but delivery was delayed. Happy with the item once it finally arrived.', 'email', 'Home', 4, DATEADD(day, -12, GETDATE())),
('CUST_0038', 'Good quality materials but assembly instructions could be clearer. Took longer than expected to set up.', 'survey', 'Home', 3, DATEADD(day, -11, GETDATE())),
('CUST_0039', 'Excellent customer service but the product itself has some minor design flaws that should be addressed.', 'phone', 'Electronics', 3, DATEADD(day, -10, GETDATE())),
('CUST_0040', 'Fast shipping and good packaging but the product color doesn''t match what was shown on the website.', 'website', 'Clothing', 3, DATEADD(day, -13, GETDATE()));

-- Historical data (older timestamps for trend analysis)
INSERT INTO feedback (customer_id, feedback_text, source, product_category, rating, timestamp) VALUES
-- 30 days ago
('CUST_0041', 'Outstanding performance and reliability. This has become an essential part of my daily workflow.', 'email', 'Electronics', 5, DATEADD(day, -30, GETDATE())),
('CUST_0042', 'Poor customer service response. Took three days to get a reply to my urgent query.', 'email', 'Customer Service', 1, DATEADD(day, -31, GETDATE())),
('CUST_0043', 'Average product quality. Works fine but nothing revolutionary or particularly noteworthy.', 'survey', 'Home', 3, DATEADD(day, -32, GETDATE())),

-- 60 days ago  
('CUST_0044', 'Excellent value and superior functionality. Highly recommend this to anyone looking for reliability.', 'website', 'Electronics', 5, DATEADD(day, -60, GETDATE())),
('CUST_0045', 'Disappointing quality for the premium price. Expected much better materials and construction.', 'email', 'Home', 2, DATEADD(day, -61, GETDATE())),
('CUST_0046', 'Decent product but delivery time was longer than promised. Communication could be improved.', 'survey', 'General', 3, DATEADD(day, -62, GETDATE())),

-- 90 days ago
('CUST_0047', 'Amazing innovation and forward-thinking design. This company is clearly ahead of the competition.', 'social_media', 'Electronics', 5, DATEADD(day, -90, GETDATE())),
('CUST_0048', 'Website checkout process is buggy and caused multiple failed transactions. Very frustrating.', 'website', 'Technology', 1, DATEADD(day, -91, GETDATE())),
('CUST_0049', 'Standard quality and reasonable pricing. Does what it''s supposed to do without any major issues.', 'email', 'General', 3, DATEADD(day, -92, GETDATE())),
('CUST_0050', 'Phenomenal customer support! They went above and beyond to ensure my satisfaction.', 'phone', 'Customer Service', 5, DATEADD(day, -93, GETDATE()));

-- Insert some repeat customers with different experiences over time
INSERT INTO feedback (customer_id, feedback_text, source, product_category, rating, timestamp) VALUES
('CUST_0001', 'Third purchase and quality seems to be declining. Not as impressed as with my previous orders.', 'email', 'Electronics', 3, DATEADD(day, -30, GETDATE())),
('CUST_0010', 'Giving you another chance after my bad experience. This order was much better - thanks for the improvement!', 'email', 'Electronics', 4, DATEADD(day, -15, GETDATE())),
('CUST_0002', 'Consistent excellent service! Always a pleasure doing business with this company.', 'survey', 'Customer Service', 5, DATEADD(day, -45, GETDATE()));

-- Add some recent high-volume days for testing alerts
DECLARE @i INT = 1;
WHILE @i <= 20
BEGIN
    INSERT INTO feedback (customer_id, feedback_text, source, product_category, rating, timestamp) 
    VALUES 
    (CONCAT('CUST_', FORMAT(50 + @i, '0000')), 
     'Sample feedback for volume testing purposes. This represents typical customer feedback.',
     CASE (@i % 4) 
        WHEN 0 THEN 'email'
        WHEN 1 THEN 'survey' 
        WHEN 2 THEN 'website'
        ELSE 'social_media'
     END,
     CASE (@i % 5)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Clothing'
        WHEN 2 THEN 'Home'
        WHEN 3 THEN 'Books'
        ELSE 'Sports'
     END,
     ((@i % 5) + 1), -- Rating between 1-5
     DATEADD(minute, -(@i * 30), GETDATE()) -- Spread throughout the day
    );
    
    SET @i = @i + 1;
END;

-- Insert sample satisfaction metrics for the last 30 days
DECLARE @date DATE = DATEADD(day, -30, GETDATE());
WHILE @date <= CAST(GETDATE() AS DATE)
BEGIN
    INSERT INTO satisfaction_metrics (date_period, avg_sentiment, total_feedback_count, positive_count, negative_count, neutral_count, top_topics)
    SELECT 
        @date,
        ROUND(RAND() * 0.6 - 0.1, 3), -- Random sentiment between -0.1 and 0.5
        FLOOR(RAND() * 50) + 10, -- Random feedback count between 10-60
        FLOOR(RAND() * 30) + 15, -- Random positive count
        FLOOR(RAND() * 10) + 2,  -- Random negative count  
        FLOOR(RAND() * 15) + 5,  -- Random neutral count
        'delivery, quality, service, pricing, support'; -- Sample topics
    
    SET @date = DATEADD(day, 1, @date);
END;

PRINT 'Sample data inserted successfully!';
PRINT 'Inserted:';
PRINT '- 70+ feedback records across different categories and time periods';
PRINT '- 30 days of satisfaction metrics';
PRINT '- Mix of positive, negative, and neutral sentiments';
PRINT '- Various sources: email, survey, website, social_media, phone, chat';
PRINT '- Multiple product categories: Electronics, Clothing, Home, Books, Sports';
PRINT '- Repeat customers with different experiences';
PRINT '- Historical data for trend analysis';
PRINT '';
PRINT 'Next steps:';
PRINT '1. Run sentiment analysis: python scripts/run_analysis.py run';
PRINT '2. Check data: SELECT COUNT(*) FROM feedback;';
PRINT '3. Verify processing: SELECT COUNT(*) FROM sentiment_analysis;';