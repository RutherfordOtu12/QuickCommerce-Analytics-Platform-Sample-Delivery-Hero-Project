-- QuickShop Analytics - SQL Queries Collection

-- Demonstrates SQL proficiency

-- =============================================================================
-- 1. BUSINESS PERFORMANCE METRICS
-- =============================================================================

-- Overall GMV and Order Metrics
-- Purpose: Track key business metrics over time
SELECT 
    'Overall Business Metrics' as metric_category,
    COUNT(DISTINCT order_id) as total_orders,
    COUNT(DISTINCT customer_id) as unique_customers,
    ROUND(SUM(CASE WHEN status = 'Delivered' THEN total_amount ELSE 0 END), 2) as total_gmv,
    ROUND(AVG(CASE WHEN status = 'Delivered' THEN total_amount END), 2) as avg_order_value,
    ROUND(CAST(SUM(CASE WHEN status = 'Delivered' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as order_completion_rate,
    ROUND(CAST(SUM(CASE WHEN status = 'Cancelled' THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as cancellation_rate
FROM orders;


-- =============================================================================
-- 2. CUSTOMER ANALYTICS
-- =============================================================================

-- Customer Segmentation Analysis
-- Purpose: Understand customer distribution and value by segment
SELECT 
    customer_segment,
    COUNT(customer_id) as customer_count,
    ROUND(CAST(COUNT(customer_id) AS REAL) / (SELECT COUNT(*) FROM customers) * 100, 2) as pct_of_total,
    ROUND(AVG(total_orders), 2) as avg_orders_per_customer,
    ROUND(AVG(total_spent), 2) as avg_lifetime_value,
    ROUND(SUM(total_spent), 2) as total_segment_revenue
FROM customers
GROUP BY customer_segment
ORDER BY total_segment_revenue DESC;

-- =============================================================================
-- 3. PRODUCT & CATEGORY ANALYTICS
-- =============================================================================
-- Top Performing Products
-- Purpose: Identify best-selling products
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    COUNT(DISTINCT oi.order_id) as times_ordered,
    SUM(oi.quantity) as total_units_sold,
    ROUND(SUM(oi.total_price), 2) as total_revenue,
    ROUND(AVG(oi.unit_price), 2) as avg_price
FROM products p
INNER JOIN order_items oi ON p.product_id = oi.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category, p.subcategory
ORDER BY total_revenue DESC
LIMIT 50;

-- 3.2 Category Performance Comparison
-- Purpose: Compare performance across product categories
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) as product_count,
    COUNT(DISTINCT oi.order_id) as order_count,
    SUM(oi.quantity) as units_sold,
    ROUND(SUM(oi.total_price), 2) as revenue,
    ROUND(AVG(oi.total_price), 2) as avg_basket_contribution,
    ROUND(SUM(oi.total_price) / (SELECT SUM(total_price) FROM order_items) * 100, 2) as revenue_share_pct
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.category
ORDER BY revenue DESC;

-- 3.3 Product Availability Analysis
-- Purpose: Monitor stock availability across shops
SELECT 
    p.category,
    COUNT(DISTINCT i.product_id) as products_in_inventory,
    ROUND(AVG(i.stock_level), 2) as avg_stock_level,
    SUM(CASE WHEN i.is_available = 1 THEN 1 ELSE 0 END) as available_count,
    SUM(CASE WHEN i.stock_level <= i.reorder_point THEN 1 ELSE 0 END) as needs_restock,
    ROUND(CAST(SUM(CASE WHEN i.is_available = 1 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100, 2) as availability_rate
FROM products p
INNER JOIN inventory i ON p.product_id = i.product_id
GROUP BY p.category
ORDER BY availability_rate ASC;

-- 3.4 Cross-Sell Analysis (Products Frequently Bought Together)
-- Purpose: Identify product combinations for recommendations
SELECT 
    p1.product_name as product_a,
    p2.product_name as product_b,
    COUNT(DISTINCT oi1.order_id) as times_bought_together,
    ROUND(AVG(oi1.total_price + oi2.total_price), 2) as avg_combined_value
FROM order_items oi1
INNER JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
INNER JOIN products p1 ON oi1.product_id = p1.product_id
INNER JOIN products p2 ON oi2.product_id = p2.product_id
GROUP BY p1.product_name, p2.product_name
HAVING times_bought_together >= 10
ORDER BY times_bought_together DESC
LIMIT 20;

-- =============================================================================
-- 4. LOCAL SHOPS PERFORMANCE
-- =============================================================================

-- 4.1 Shop Performance Leaderboard
-- Purpose: Rank shops by key performance metrics
SELECT 
    s.shop_id,
    s.shop_name,
    s.shop_type,
    s.city,
    s.district,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END), 2) as revenue,
    ROUND(AVG(CASE WHEN o.status = 'Delivered' THEN o.total_amount END), 2) as aov,
    ROUND(AVG(d.total_time_minutes), 2) as avg_delivery_time,
    ROUND(AVG(d.delivery_rating), 2) as avg_rating,
    COUNT(DISTINCT o.customer_id) as unique_customers
FROM local_shops s
LEFT JOIN orders o ON s.shop_id = o.shop_id
LEFT JOIN deliveries d ON o.order_id = d.order_id
WHERE s.is_active = 1
GROUP BY s.shop_id, s.shop_name, s.shop_type, s.city, s.district
HAVING total_orders > 0
ORDER BY revenue DESC
LIMIT 20;

-- 4.2 Geographic Performance Analysis
-- Purpose: Compare performance across cities
SELECT 
    s.city,
    COUNT(DISTINCT s.shop_id) as active_shops,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT o.customer_id) as unique_customers,
    ROUND(SUM(CASE WHEN o.status = 'Delivered' THEN o.total_amount ELSE 0 END), 2) as gmv,
    ROUND(AVG(CASE WHEN o.status = 'Delivered' THEN o.total_amount END), 2) as aov,
    ROUND(AVG(d.total_time_minutes), 2) as avg_delivery_time
FROM local_shops s
LEFT JOIN orders o ON s.shop_id = o.shop_id
LEFT JOIN deliveries d ON o.order_id = d.order_id
WHERE s.is_active = 1
GROUP BY s.city
ORDER BY gmv DESC;

-- =============================================================================
-- 5. DATA QUALITY CHECKS
-- =============================================================================

-- 5.1 Data Quality Dashboard
-- Purpose: Monitor data completeness and integrity
SELECT 
    'Orders with missing customer' as check_name,
    COUNT(*) as issue_count
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT 
    'Orders with missing shop' as check_name,
    COUNT(*) as issue_count
FROM orders o
LEFT JOIN local_shops s ON o.shop_id = s.shop_id
WHERE s.shop_id IS NULL

UNION ALL

SELECT 
    'Delivered orders without delivery record' as check_name,
    COUNT(*) as issue_count
FROM orders o
LEFT JOIN deliveries d ON o.order_id = d.order_id
WHERE o.status = 'Delivered' AND d.delivery_id IS NULL

UNION ALL

SELECT 
    'Orders with negative amounts' as check_name,
    COUNT(*) as issue_count
FROM orders
WHERE total_amount < 0

UNION ALL

SELECT 
    'Products with zero price' as check_name,
    COUNT(*) as issue_count
FROM products
WHERE base_price <= 0;

-- 5.2 Inventory Anomalies
-- Purpose: Detect inventory data issues
SELECT 
    'Negative stock levels' as anomaly_type,
    COUNT(*) as count
FROM inventory
WHERE stock_level < 0

UNION ALL

SELECT 
    'Available but zero stock' as anomaly_type,
    COUNT(*) as count
FROM inventory
WHERE is_available = 1 AND stock_level = 0

UNION ALL

SELECT 
    'Not available but has stock' as anomaly_type,
    COUNT(*) as count
FROM inventory
WHERE is_available = 0 AND stock_level > 0;
