-- QuickShop Analytics Platform - MySQL Database Schema
-- Created for Delivery Hero Working Student, Data Analyst Application
-- Database: MySQL 8.0+

-- Drop existing database if exists and create new one
DROP DATABASE IF EXISTS quickshop;
CREATE DATABASE quickshop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE quickshop;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Customers Table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    registration_date DATETIME NOT NULL,
    city VARCHAR(50) NOT NULL,
    customer_segment VARCHAR(20) NOT NULL,
    total_orders INT DEFAULT 0,
    total_spent DECIMAL(10, 2) DEFAULT 0.00,
    last_order_date DATETIME,
    days_since_last_order INT,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_city (city),
    INDEX idx_segment (customer_segment),
    INDEX idx_registration_date (registration_date),
    INDEX idx_last_order (last_order_date)
) ENGINE=InnoDB;

-- Local Shops Table
CREATE TABLE local_shops (
    shop_id INT PRIMARY KEY,
    shop_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    shop_type VARCHAR(50) NOT NULL,
    opening_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    total_orders INT DEFAULT 0,
    avg_preparation_time INT,
    INDEX idx_city (city),
    INDEX idx_shop_type (shop_type),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- Products Table
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_category (category),
    INDEX idx_active (is_active)
) ENGINE=InnoDB;

-- Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    shop_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    delivery_fee DECIMAL(10, 2) DEFAULT 0.00,
    payment_method VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (shop_id) REFERENCES local_shops(shop_id),
    INDEX idx_customer (customer_id),
    INDEX idx_shop (shop_id),
    INDEX idx_order_date (order_date),
    INDEX idx_status (status),
    INDEX idx_composite (order_date, status)
) ENGINE=InnoDB;

-- Order Items Table
CREATE TABLE order_items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_order (order_id),
    INDEX idx_product (product_id)
) ENGINE=InnoDB;

-- Deliveries Table
CREATE TABLE deliveries (
    delivery_id INT PRIMARY KEY,
    order_id INT NOT NULL,
    courier_id INT,
    pickup_time DATETIME,
    delivery_time DATETIME,
    estimated_time INT,
    actual_time INT,
    total_time_minutes INT,
    distance_km DECIMAL(5, 2),
    delivery_rating DECIMAL(3, 2),
    delivery_status VARCHAR(20),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    INDEX idx_order (order_id),
    INDEX idx_courier (courier_id),
    INDEX idx_status (delivery_status),
    INDEX idx_rating (delivery_rating)
) ENGINE=InnoDB;

-- Inventory Table
CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    shop_id INT NOT NULL,
    product_id INT NOT NULL,
    stock_level INT NOT NULL,
    reorder_point INT NOT NULL,
    last_restocked DATETIME,
    FOREIGN KEY (shop_id) REFERENCES local_shops(shop_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_shop (shop_id),
    INDEX idx_product (product_id),
    INDEX idx_stock_level (stock_level),
    UNIQUE KEY unique_shop_product (shop_id, product_id)
) ENGINE=InnoDB;

-- Promotions Table
CREATE TABLE promotions (
    promotion_id INT PRIMARY KEY,
    promotion_name VARCHAR(100) NOT NULL,
    promotion_type VARCHAR(50) NOT NULL,
    discount_percentage DECIMAL(5, 2),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_usage INT DEFAULT 0,
    total_discount_given DECIMAL(10, 2) DEFAULT 0.00,
    INDEX idx_dates (start_date, end_date),
    INDEX idx_type (promotion_type)
) ENGINE=InnoDB;

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Daily Metrics View
CREATE OR REPLACE VIEW daily_metrics AS
SELECT 
    DATE(order_date) as date,
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT CASE WHEN status = 'Delivered' THEN order_id END) as delivered_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(CASE WHEN status = 'Delivered' THEN total_amount ELSE 0 END) as gmv,
    AVG(CASE WHEN status = 'Delivered' THEN total_amount END) as avg_order_value,
    ROUND(COUNT(DISTINCT CASE WHEN status = 'Delivered' THEN order_id END) * 100.0 / 
          NULLIF(COUNT(DISTINCT order_id), 0), 2) as completion_rate
FROM orders
GROUP BY DATE(order_date);

-- Shop Performance View
CREATE OR REPLACE VIEW shop_performance AS
SELECT 
    s.shop_id,
    s.shop_name,
    s.city,
    s.shop_type,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END) as total_revenue,
    AVG(CASE WHEN o.status = 'Delivered' THEN o.total_amount END) as avg_order_value,
    ROUND(COUNT(DISTINCT CASE WHEN o.status = 'Delivered' THEN o.order_id END) * 100.0 / 
          NULLIF(COUNT(DISTINCT o.order_id), 0), 2) as completion_rate,
    AVG(d.delivery_rating) as avg_delivery_rating,
    AVG(d.total_time_minutes) as avg_delivery_time
FROM local_shops s
LEFT JOIN orders o ON s.shop_id = o.shop_id
LEFT JOIN deliveries d ON o.order_id = d.order_id
GROUP BY s.shop_id, s.shop_name, s.city, s.shop_type;

-- Customer Segments View
CREATE OR REPLACE VIEW customer_segments_summary AS
SELECT 
    customer_segment,
    COUNT(DISTINCT customer_id) as customer_count,
    AVG(total_orders) as avg_orders_per_customer,
    AVG(total_spent) as avg_lifetime_value,
    SUM(total_spent) as total_segment_revenue,
    ROUND(SUM(total_spent) * 100.0 / (SELECT SUM(total_spent) FROM customers), 2) as revenue_share_pct
FROM customers
GROUP BY customer_segment;

-- Product Performance View
CREATE OR REPLACE VIEW product_performance AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.base_price,
    COUNT(DISTINCT oi.order_id) as times_ordered,
    SUM(oi.quantity) as total_units_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_selling_price,
    ROUND((AVG(oi.unit_price) - p.cost_price) / NULLIF(p.cost_price, 0) * 100, 2) as avg_margin_pct
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, p.category, p.base_price, p.cost_price;

-- City Performance View
CREATE OR REPLACE VIEW city_performance AS
SELECT 
    c.city,
    COUNT(DISTINCT c.customer_id) as total_customers,
    COUNT(DISTINCT s.shop_id) as total_shops,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END) as total_gmv,
    AVG(CASE WHEN o.status = 'Delivered' THEN o.total_amount END) as avg_order_value,
    ROUND(COUNT(DISTINCT CASE WHEN o.status = 'Delivered' THEN o.order_id END) * 100.0 / 
          NULLIF(COUNT(DISTINCT o.order_id), 0), 2) as completion_rate
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN local_shops s ON c.city = s.city
GROUP BY c.city;

-- Delivery Performance View
CREATE OR REPLACE VIEW delivery_performance AS
SELECT 
    delivery_status,
    COUNT(*) as delivery_count,
    AVG(total_time_minutes) as avg_delivery_time,
    AVG(distance_km) as avg_distance,
    AVG(delivery_rating) as avg_rating,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM deliveries), 2) as percentage
FROM deliveries
GROUP BY delivery_status;

-- ============================================================================
-- STORED PROCEDURES (Optional but impressive)
-- ============================================================================

DELIMITER //

-- Procedure to calculate customer RFM scores
CREATE PROCEDURE calculate_rfm_scores()
BEGIN
    -- Create temporary table for RFM analysis
    DROP TEMPORARY TABLE IF EXISTS rfm_temp;
    CREATE TEMPORARY TABLE rfm_temp AS
    SELECT 
        c.customer_id,
        DATEDIFF(CURDATE(), MAX(o.order_date)) as recency_days,
        COUNT(DISTINCT o.order_id) as frequency,
        SUM(o.total_amount) as monetary
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id;
    
    -- Display RFM scores with quartiles
    SELECT 
        customer_id,
        recency_days,
        frequency,
        monetary,
        NTILE(4) OVER (ORDER BY recency_days DESC) as R_score,
        NTILE(4) OVER (ORDER BY frequency ASC) as F_score,
        NTILE(4) OVER (ORDER BY monetary ASC) as M_score
    FROM rfm_temp
    ORDER BY customer_id;
END //

DELIMITER ;

-- ============================================================================
-- SAMPLE QUERIES FOR TESTING
-- ============================================================================

-- Test query: Top 10 customers by revenue
-- SELECT customer_id, total_spent, total_orders 
-- FROM customers 
-- ORDER BY total_spent DESC 
-- LIMIT 10;

-- Test query: Daily GMV trend
-- SELECT * FROM daily_metrics 
-- ORDER BY date DESC 
-- LIMIT 30;

-- Test query: Shop performance ranking
-- SELECT shop_name, city, total_revenue, completion_rate 
-- FROM shop_performance 
-- ORDER BY total_revenue DESC 
-- LIMIT 20;

-- ============================================================================
-- NOTES
-- ============================================================================

-- This schema is optimized for:
-- 1. Quick commerce analytics queries
-- 2. Tableau dashboard connections
-- 3. Business intelligence reporting
-- 4. Performance with proper indexing

-- Key differences from SQLite:
-- - Uses InnoDB engine for ACID compliance and foreign keys
-- - Proper DATETIME types instead of TEXT
-- - DECIMAL for monetary values (precise)
-- - AUTO_INCREMENT for surrogate keys
-- - Optimized indexes for common query patterns
-- - Views for frequently accessed aggregations
-- - Stored procedures for complex calculations

-- To load data after creating schema:
-- Use the load_data_mysql.py script

-- For Tableau connection:
-- Host: localhost (or your MySQL server)
-- Port: 3306 (default)
-- Database: quickshop
-- Username: your_mysql_user
-- Password: your_mysql_password
