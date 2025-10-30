🛍️ Retail Sales & Inventory Intelligence System

Author: Shruti Sumadhur Ghosh
Organization: Labmentix
Tools Used: Excel | SQL (SQLite) | Python (pandas, scikit-learn) | Power BI

📘 Project Overview

This project analyzes retail sales and inventory data for a company selling mobile phones and laptops.
It provides an end-to-end data analytics solution — from raw data to actionable insights — through data cleaning, relational modeling, Python-based customer segmentation, and interactive Power BI dashboards.

🧩 Tech Stack

Excel – Data cleaning & preprocessing

SQLite – Database creation, schema design, and SQL querying

Python (pandas, scikit-learn) – Customer segmentation using KMeans clustering

Power BI – Interactive dashboards, KPIs, and dynamic tooltips

⚙️ Project Phases
Phase 1 – Data Cleaning

Removed duplicates and nulls

Standardized date formats and discount fields

Ensured product–category mapping consistency

Phase 2 – SQL Data Modeling

Built relational schema with 9 interconnected tables

Verified referential integrity using PRAGMA integrity_check

Created indexes on key columns to improve query performance

Phase 3 – Python Customer Segmentation (NEW)

Implemented customer-level feature aggregation using pandas

Performed KMeans clustering with scikit-learn to segment customers by purchase behavior

Calculated metrics:

Total Sales

Order Count

Average Order Value

Recency (days since last order)

Saved analytical outputs to python_analysis/:

customer_aggregates.csv — Customer-level metrics

customer_segments.csv — Cluster assignment per customer

segments_scatter.png and cluster_distribution.png — Visual cluster summaries

Phase 4 – Power BI Visualization

Built three Power BI dashboards:

Executive Sales Dashboard – Overall business performance

Inventory & Stock Overview – Stock health, product distribution, and store metrics

Customer Insights (NEW) – Cluster-wise customer behavior using Python segmentation

📊 Dashboards
1️⃣ Executive Sales Dashboard

KPIs: Total Sales, Orders, Customers, Average Order Value

Visuals: Sales by Category, Store, Brand, Staff, and Trends over Time

2️⃣ Inventory & Stock Overview

KPIs: Total Stock Quantity, Distinct Products, and Stores in Stock

Visuals: Inventory by Category, Store-level stock, and Top Products

3️⃣ Customer Insights (NEW)

Integrated Python segmentation outputs with Power BI visuals

KPIs:

Average Sales per Segment

Average Orders per Customer

Average Recency per Segment

Visuals:

Count of Customers by Cluster

Average Sales per Customer by Cluster

Segment-level summary table

Added a dedicated Tooltip Page (Tooltip_cluster_info) showing dynamic metrics per cluster when hovering over visuals.

💡 Key Insights
Sales & Inventory Insights

Trek brand and Mountain Bikes lead total sales.

Baldwin Bikes is the top-performing store.

Inventory levels are balanced across stores, ensuring stock availability.

Customer Segmentation Insights

Total 1,445 customers segmented into four clusters:

Loyal Customers (620): Largest base with steady repeat orders.

New Buyers (441): Recent acquisitions — opportunity to nurture.

Churn Risk (279): High-value but inactive — ideal for reactivation campaigns.

Low Value (105): Small group but high spend — potential premium customers.

Average Sales per Customer: 5.32K

Average Orders per Customer: 1.12

Average Recency: 6,134 days — highlights re-engagement potential.

📂 Project Deliverables
File	Description
Database/retail_sales.db	SQLite database with 9 normalized tables
python_analysis/retail_customer_segmentation.py	Python segmentation script
python_analysis/customer_segments.csv	Clustered customer output
Retail_Sales_Analytics.pbix	Power BI dashboards
Retail_Sales_Project_Report.pdf	Final project documentation
📹 Project Presentation

🎥 A 7–10 minute video walkthrough explaining data processing, dashboard design, and business insights.
👉 Watch here [https://drive.google.com/file/d/1WHf8Do6t2zK0UqjcbKOTw8N9w-pYVWd_/view?usp=sharing]

🧭 Future Enhancements

Integrate predictive analytics for sales forecasting

Add RFM (Recency-Frequency-Monetary) scoring in Python

Connect Power BI directly to Python outputs for automated refresh

📬 Contact

👩‍💻 Shruti Sumadhur Ghosh
📧 [shrutisghosh@outlook.com
]
🔗 LinkedIn

🏷️ Tags

#DataAnalytics #PowerBI #Python #CustomerSegmentation #SQL #RetailAnalytics #BusinessIntelligence #DataVisualization

