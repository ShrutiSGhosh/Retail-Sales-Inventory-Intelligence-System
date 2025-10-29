# retail_customer_segmentation.py
# Place this file at:
# D:\DA Projects\Retail Sales & Inventory Intelligence System\python_analysis\retail_customer_segmentation.py
#
# Requires packages: pandas sqlalchemy scikit-learn matplotlib seaborn
# Install with (in your activated venv): pip install pandas sqlalchemy scikit-learn matplotlib seaborn

import os
import sys
import traceback
from datetime import datetime
import warnings

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")
sns.set(style="whitegrid")

# ---------- CONFIG ----------
DB_PATH = r"D:\DA Projects\Retail Sales & Inventory Intelligence System\Database\retail_sales.db"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))  # output in python_analysis folder
N_CLUSTERS = 4
RANDOM_STATE = 42
# ----------------------------

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def safe_read_sql(sql, engine, name):
    try:
        df = pd.read_sql(sql, engine)
        log(f"Loaded {len(df):,} rows from '{name}'.")
        return df
    except Exception as e:
        log(f"ERROR reading '{name}': {e}")
        return None

def pick_date_column(df_columns):
    candidates = ['order_date', 'orderdate', 'date', 'order_date_placed', 'created_at', 'order_datetime', 'shipped_date']
    for c in candidates:
        if c in df_columns:
            return c
    for c in df_columns:
        if 'date' in c.lower() or 'dt' in c.lower() or 'time' in c.lower():
            return c
    return None

def main():
    try:
        log("Starting customer segmentation script.")
        if not os.path.exists(DB_PATH):
            log(f"Database file not found at: {DB_PATH}")
            log("Please update DB_PATH at the top of the script and re-run.")
            sys.exit(1)

        engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
        log(f"Connected to database: {DB_PATH}")

        # load tables - safe read
        orders = safe_read_sql("SELECT * FROM orders", engine, "orders")
        order_items = safe_read_sql("SELECT * FROM order_items", engine, "order_items")
        customers = safe_read_sql("SELECT * FROM customers", engine, "customers")

        if orders is None or order_items is None or customers is None:
            log("One or more required tables not available. Exiting.")
            sys.exit(1)

        # find an order date column
        date_col = pick_date_column(list(orders.columns))
        if date_col is None:
            log("No obvious date column found in 'orders' table. Columns: " + ", ".join(orders.columns))
            sys.exit(1)
        log(f"Using orders date column: '{date_col}'")

        # parse date column
        orders[date_col] = pd.to_datetime(orders[date_col], errors='coerce')
        if orders[date_col].isnull().all():
            log(f"All values in {date_col} parsed as NaT. Please check date format.")
            sys.exit(1)

        # build order-level totals from order_items
        if 'total_price' in order_items.columns:
            oi_totals = order_items.groupby('order_id', as_index=False).agg({
                'total_price': 'sum',
                'quantity': 'sum'
            }).rename(columns={'total_price': 'order_total', 'quantity': 'order_quantity'})
            log("Aggregated order-level totals from order_items.")
        else:
            if {'list_price', 'quantity'}.issubset(order_items.columns):
                order_items['calc_total_price'] = order_items['list_price'] * order_items['quantity'] * (1 - order_items.get('discount', 0))
                oi_totals = order_items.groupby('order_id', as_index=False).agg({
                    'calc_total_price': 'sum',
                    'quantity': 'sum'
                }).rename(columns={'calc_total_price': 'order_total', 'quantity': 'order_quantity'})
                log("Computed order_total from list_price * quantity (with discount if present).")
            else:
                log("Cannot compute order totals (missing columns). Exiting.")
                sys.exit(1)

        # ensure order_id exists
        if 'order_id' not in orders.columns:
            possible_id = [c for c in orders.columns if 'id' in c.lower()]
            if possible_id:
                orders = orders.rename(columns={possible_id[0]: 'order_id'})
                log(f"Renamed {possible_id[0]} to order_id")
            else:
                log("No order id column available in orders. Exiting.")
                sys.exit(1)

        merged = pd.merge(orders[['order_id', date_col, *( ['customer_id'] if 'customer_id' in orders.columns else [])]],
                          oi_totals, on='order_id', how='left')
        log(f"Merged orders and order totals: {len(merged):,} rows")

        if 'customer_id' not in merged.columns or merged['customer_id'].isnull().all():
            log("orders table does not have a usable 'customer_id' column. Exiting.")
            sys.exit(1)

        max_order_date = merged[date_col].max()
        log(f"Max order date in dataset: {max_order_date}")

        cust_agg = merged.groupby('customer_id').agg(
            total_orders=('order_id', 'nunique'),
            total_sales=('order_total', 'sum'),
            total_quantity=('order_quantity', 'sum'),
            last_order_date=(date_col, 'max')
        ).reset_index()

        cust_agg['avg_order_value'] = cust_agg['total_sales'] / cust_agg['total_orders'].replace(0, np.nan)
        cust_agg['recency_days'] = (max_order_date - cust_agg['last_order_date']).dt.days

        cust_agg['total_sales'] = cust_agg['total_sales'].fillna(0)
        cust_agg['total_quantity'] = cust_agg['total_quantity'].fillna(0)
        cust_agg['avg_order_value'] = cust_agg['avg_order_value'].replace([np.inf, -np.inf], 0).fillna(0)
        cust_agg['recency_days'] = cust_agg['recency_days'].fillna(9999)

        if 'customer_id' in customers.columns:
            cust_details = customers.copy()
            if 'customer_id' not in cust_details.columns:
                possible = [c for c in cust_details.columns if 'id' in c.lower()]
                if possible:
                    cust_details = cust_details.rename(columns={possible[0]: 'customer_id'})
            cust_final = pd.merge(cust_agg, cust_details, on='customer_id', how='left')
            log("Joined customer details (if available).")
        else:
            cust_final = cust_agg

        agg_csv = os.path.join(OUT_DIR, "customer_aggregates.csv")
        cust_final.to_csv(agg_csv, index=False)
        log(f"Wrote customer aggregates to: {agg_csv}")

        # ---------- segmentation ----------
        features = ['total_orders', 'total_sales', 'avg_order_value', 'total_quantity', 'recency_days']
        seg_df = cust_final[features].copy().fillna(0)

        seg_df = seg_df[(seg_df[features].sum(axis=1) > 0) | (seg_df['recency_days'] < 9999)]

        scaler = StandardScaler()
        X = scaler.fit_transform(seg_df)

        kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_STATE, n_init=10)
        labels = kmeans.fit_predict(X)
        seg_df['cluster'] = labels
        cust_final = cust_final.loc[seg_df.index].copy()
        cust_final['cluster'] = labels

        cluster_summary = cust_final.groupby('cluster').agg(
            n_customers=('customer_id', 'count'),
            avg_total_orders=('total_orders', 'mean'),
            avg_total_sales=('total_sales', 'mean'),
            avg_order_value=('avg_order_value', 'mean'),
            avg_recency_days=('recency_days', 'mean')
        ).reset_index()

        summary_csv = os.path.join(OUT_DIR, "cluster_summary.csv")
        cluster_summary.to_csv(summary_csv, index=False)
        log(f"Wrote cluster summary to: {summary_csv}")

        segments_csv = os.path.join(OUT_DIR, "customer_segments.csv")
        cust_final.to_csv(segments_csv, index=False)
        log(f"Wrote customer segments to: {segments_csv}")

        # ---------- charts ----------
        try:
            plt.figure(figsize=(8,6))
            palette = sns.color_palette("tab10", n_colors=N_CLUSTERS)
            sns.scatterplot(x=X[:,0], y=X[:,1], hue=labels, palette=palette, s=40)
            plt.title("Customer segments (scaled projection)")
            plt.xlabel("component 1 (scaled)")
            plt.ylabel("component 2 (scaled)")
            plt.legend(title='cluster')
            scatter_png = os.path.join(OUT_DIR, "segments_scatter.png")
            plt.tight_layout()
            plt.savefig(scatter_png, dpi=150)
            plt.close()
            log(f"Wrote cluster scatter plot to: {scatter_png}")

            plt.figure(figsize=(7,4))
            sns.countplot(x='cluster', data=cust_final, palette=palette)
            plt.title("Customers per cluster")
            plt.xlabel("cluster")
            plt.ylabel("count")
            dist_png = os.path.join(OUT_DIR, "cluster_distribution.png")
            plt.tight_layout()
            plt.savefig(dist_png, dpi=150)
            plt.close()
            log(f"Wrote cluster distribution plot to: {dist_png}")
        except Exception as e:
            log(f"Warning: failed to save charts: {e}")

        log("✅ Customer segmentation complete.")
        log("Files created:")
        log(f" - {agg_csv}")
        log(f" - {segments_csv}")
        log(f" - {summary_csv}")
        log(f" - segments scatter and distribution PNGs (if generated)")

    except Exception as exc:
        log("FATAL ERROR:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
