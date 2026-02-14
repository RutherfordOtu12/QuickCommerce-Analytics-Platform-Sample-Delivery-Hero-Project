# Database Schema

The database follows third normal form (3NF) with eight core tables and six analytical views. The schema is designed to support both transactional queries and analytical workloads.

# Core Tables

local_shops: Partner store information including shop type, location, commission rates, and average preparation times. Tracks 150 shops across 10 German cities with partnership start dates and active status flags.

products: Product catalog with 179 items organized into eight categories (Fresh Produce, Dairy, Meat & Fish, Bakery, Beverages, Pantry, Snacks, Household). Each product has a base price and unit of measurement.

customers: Customer profiles with registration dates, city locations, and segment classifications (New, Regular, VIP, Churned). Includes aggregated metrics for total orders, total spend, and last order date.

orders: Order transactions with customer and shop references, timestamps, status tracking, pricing breakdown (subtotal, discount, delivery fee, total), and payment methods. Supports three status values: Delivered, Cancelled, In Progress.

order_items: Line-level order details linking products to orders with quantities, unit prices, and total prices. Enables basket analysis and product performance tracking.

deliveries: Delivery performance metrics including preparation time, delivery time, total time, and customer ratings (1-5 scale). Only created for successfully delivered orders.

inventory: Stock levels for each product-shop combination with reorder points, last restock dates, and availability flags. Supports inventory optimization and stockout prevention.

promotions: Marketing campaign tracking with promotion types (Percentage Discount, Fixed Amount, Free Delivery, BOGO), date ranges, minimum order values, usage counts, and revenue impact.

# Analytical Views

Six pre-aggregated views accelerate common analytics queries by materializing frequently accessed metrics:

•v_daily_gmv: Daily aggregates of orders, customers, GMV, AOV, and status breakdowns

•v_shop_performance: Shop-level KPIs including revenue, ratings, delivery times, and customer counts

•v_product_performance: Product metrics with order frequency, quantities sold, and revenue

•v_customer_cohorts: Cohort analysis by registration month and customer segment

•v_inventory_health: Stock availability rates and reorder needs by shop

•v_category_performance: Category-level sales and unit metrics


# SQL Analytics Capabilities

The SQL queries demonstrate proficiency across multiple complexity levels and business domains. Each query is documented with its purpose, complexity level, and business context.

Business Performance Metrics

These queries provide executive-level insights into overall business health. The GMV tracking query calculates total gross merchandise value, average order value, and completion rates with proper handling of cancelled orders. The monthly trend analysis uses date functions to aggregate metrics by month, enabling year-over-year and month-over-month comparisons. The moving average query implements a 7-day rolling window using window functions to smooth daily volatility and reveal underlying trends.

Customer Analytics

Customer analysis queries segment the user base and track behavior over time. The segmentation query distributes customers across four segments (New, Regular, VIP, Churned) and calculates lifetime value metrics for each group. The cohort retention analysis uses common table expressions to track customer activity by registration month, measuring retention at 30, 60, and 90-day intervals. The churn risk query identifies high-value customers who have been inactive for extended periods, enabling proactive retention campaigns.

Product & Category Analysis

Product queries identify best-sellers, slow-movers, and cross-sell opportunities. The top products query joins order items with products and orders, filtering for delivered status and ranking by revenue. The category performance comparison aggregates across product categories to show revenue share and basket contribution. The cross-sell analysis uses a self-join on order items to find products frequently purchased together, supporting recommendation engine development.

Shop & Geographic Performance

Shop-level queries enable performance benchmarking and geographic expansion planning. The shop leaderboard combines order, delivery, and rating data to rank partners by multiple dimensions. The geographic analysis aggregates by city to compare market performance and identify growth opportunities. The shop type comparison reveals which partner categories (Supermarket, Specialty Store, etc.) drive the most value.

Operational Efficiency

Operations queries monitor delivery performance and identify bottlenecks. The delivery time distribution buckets orders into time ranges and calculates rating correlations. The cancellation analysis tracks cancellation rates over time and quantifies lost revenue. The peak hours query aggregates by hour of day to optimize staffing and inventory placement.

Data Quality Monitoring

Quality queries ensure data integrity and completeness. The data quality dashboard uses UNION ALL to combine multiple validation checks into a single report. The inventory anomalies query identifies logical inconsistencies like products marked available with zero stock.


# Python Analysis Capabilities

The Python analysis suite implements five major analytical techniques, each producing both data outputs and visualizations.

Time Series Analysis

The time series module loads daily order data and calculates 7-day and 30-day moving averages to smooth volatility. Growth rates are computed using percentage change functions, and trend lines are fitted using linear regression. The output includes a dual-panel visualization showing GMV trends and order volume trends with multiple moving average overlays.

Customer Cohort Retention

Cohort analysis tracks customer retention by registration month. The script creates a cohort month field, calculates cohort index (months since registration), and builds a retention matrix showing what percentage of each cohort remains active over time. The heatmap visualization uses a color gradient to make retention patterns immediately visible, with warmer colors indicating higher retention.

RFM Segmentation

The RFM (Recency, Frequency, Monetary) analysis segments customers based on three dimensions. Recency measures days since last order, frequency counts total orders, and monetary sums total spend. Each dimension is scored 1-5 using quantile-based binning, and customers are classified into segments (Champions, Loyal Customers, Potential Loyalists, At Risk, Lost) based on combined scores. The output includes both a segment distribution pie chart and a revenue-by-segment bar chart.

Product Basket Analysis

Basket analysis examines order composition and category performance. The script calculates average basket size (items per order), average basket value, and category mix. A basket size distribution histogram reveals purchasing patterns, while a category revenue bar chart identifies top-performing product groups. The analysis supports inventory planning and promotional strategy.

Geographic Performance

Geographic analysis aggregates metrics by city to identify regional variations. The script produces four visualizations: GMV by city, order volume by city, average order value by city, and average delivery time by city. These multi-panel charts enable quick identification of high-performing markets and operational challenges.

All Python scripts follow a consistent structure with configuration variables at the top, modular analysis sections, automatic output saving, and comprehensive logging. The code is production-ready with error handling and type hints.


# AI & Automation Features

The automation layer demonstrates how analytics can move from reactive reporting to proactive decision-making. Two independent systems run automated analyses and generate actionable recommendations.

Anomaly Detection System

The anomaly detection engine uses statistical methods to identify unusual patterns across five business domains. Revenue anomalies are detected using a two-standard-deviation threshold, flagging days with unusually high or low GMV. Order volume anomalies apply the same statistical approach to daily order counts. Customer behavior anomalies identify high-value customers with low order frequency (potential VIPs) and previously active customers at churn risk. Inventory anomalies flag shops with out-of-stock rates exceeding 20%. Delivery performance anomalies detect shops with significantly slower delivery times or low customer ratings.

Each detected anomaly is classified by severity (Critical, Warning) and type, then compiled into a structured JSON report with automated recommendations. The system prioritizes issues as High or Medium based on business impact and provides specific action items for each category.

Demand Forecasting System

The forecasting engine predicts product demand using time series analysis. For the top 20 products by volume, the system calculates 7-day moving averages, detects linear trends, and projects demand for the next 7 and 30 days. Volatility is measured using the coefficient of variation, and confidence levels (High, Medium, Low) are assigned based on demand stability.

The system generates reorder recommendations by comparing forecasted demand against current inventory levels. A safety factor (1.2x to 1.5x depending on volatility) ensures adequate stock to handle demand fluctuations. Products below their reorder point are flagged as urgent. The output includes category-level forecasts, product-specific predictions, and automated reorder quantities.

Both automation systems output structured JSON reports that can be consumed by the dashboard or integrated into operational workflows. The reports include executive summaries, detailed findings, and prioritized action items.


# Interactive Dashboard

The web dashboard provides a modern interface for exploring the analytics platform. Built with a data brutalism design philosophy, the interface prioritizes clarity, contrast, and function over decoration.

Design System

The visual design uses a high-contrast color palette with charcoal (#1a1a1a) and crisp white (#ffffff) as the base, accented by electric blue (#0066ff) for primary actions, success green (#00c853) for positive metrics, and warning amber (#ff9500) for alerts. Typography combines three fonts: Space Grotesk (700) for headings, Inter (400-600) for body text, and JetBrains Mono (500) for data values and code. The layout employs an asymmetric grid with a prominent sidebar and minimal border radius (0.25rem) for a brutalist aesthetic.

Dashboard Pages

Overview: The landing page displays six key metric cards (Total GMV, Total Orders, Average Order Value, Completion Rate, Active Shops, Total Customers) with monospaced values and trend indicators. Below the metrics, five visualization cards show GMV trends, cohort retention, RFM segments, basket analysis, and geographic performance. An about section explains the project context and technical stack.

AI Insights: This page showcases the automation capabilities with three summary cards (anomalies detected, products forecasted, automated recommendations). The anomaly detection section breaks down findings by category and displays prioritized recommendations with visual severity indicators. The demand forecasting section shows 7-day and 30-day forecasts with forecast insights. A methodology section explains the statistical techniques used.

SQL Queries: The queries page organizes 20+ SQL queries into six tabs (Business Metrics, Customer Analytics, Product Performance, Shop Analytics, Operations, Data Quality). Each query is presented with a title, description, complexity badge, and formatted SQL code. A skills summary highlights the SQL techniques demonstrated.

Documentation: The documentation page provides a comprehensive project overview including technical stack, dataset details, database schema, analytics capabilities, skills demonstrated, and project structure. The page is designed to serve as both a technical reference and a portfolio piece.

Technical Implementation

The dashboard uses React functional components with TypeScript for type safety. State management relies on React hooks (useState, useEffect) with no external state library needed for this project's scope. Data fetching uses the native Fetch API to load JSON reports and CSV files. The routing layer (Wouter) provides client-side navigation without page reloads.

The UI components come from shadcn/ui, a collection of accessible, customizable primitives built on Radix UI. Custom components (MetricCard, DashboardLayout) extend the base components with project-specific styling and behavior. The entire application is statically generated, requiring no backend server for deployment.

