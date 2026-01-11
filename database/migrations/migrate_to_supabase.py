import os
import pandas as pd
from app.text_2_sql.config import Config
import logging
from supabase import create_client, Client
from typing import List, Dict
import time


def get_supabase_client() -> Client:
    if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
        raise ValueError("Supabase credentials not configured.")
    return create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


DATA_FOLDER = "E-Commerce_Dataset"


# Tables with composite primary keys
COMPOSITE_PK_TABLES = {
    "order_items": "order_id,order_item_id",
    "order_payments": "order_id,payment_sequential"
}

# Migration order respecting foreign key dependencies
MIGRATION_ORDER = [
    ("product_category_name_translation.csv", "product_category_name_translation"),
    ("olist_sellers_dataset.csv", "sellers"),
    ("olist_customers_dataset.csv", "customers"),
    ("olist_products_dataset.csv", "products"),
    ("olist_orders_dataset.csv", "orders"),
    ("olist_order_items_dataset.csv", "order_items"),
    ("olist_order_payments_dataset.csv", "order_payments"),
    ("olist_order_reviews_dataset.csv", "order_reviews"),
    ("olist_geolocation_dataset.csv", "geolocation")
]


def clean_data(df: pd.DataFrame, table_name: str) -> pd.DataFrame:

    df = df.where(pd.notnull(df), None)
    
    # Convert timestamp/date columns to ISO format
    date_patterns = ['timestamp', 'date', '_at']
    for col in df.columns:
        if any(pattern in col.lower() for pattern in date_patterns):
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
    
    return df


def migrate_table(csv_name: str, table_name: str, batch_size: int = 1000):
 
    supabase = get_supabase_client()
    file_path = os.path.join(DATA_FOLDER, csv_name)
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return
    
    logger.info(f"Starting migration for {table_name} from {csv_name}...")
    
    total_rows = 0
    failed_batches = 0
    
    try:
        for chunk_num, chunk in enumerate(pd.read_csv(file_path, chunksize=batch_size), 1):
            chunk = clean_data(chunk, table_name)
            data = chunk.to_dict(orient='records')
            
            # Filter out completely empty rows
            data = [row for row in data if any(v is not None for v in row.values())]
            
            if not data:
                continue
            
            try:
                # Geolocation has no primary key, use insert
                if table_name == "geolocation":
                    response = supabase.table(table_name).insert(data).execute()
                
                # Tables with composite primary keys
                elif table_name in COMPOSITE_PK_TABLES:
                    response = supabase.table(table_name).upsert(
                        data, 
                        on_conflict=COMPOSITE_PK_TABLES[table_name]
                    ).execute()
                
       
                else:
                    response = supabase.table(table_name).upsert(data).execute()
                
                total_rows += len(data)
                logger.info(f"✓ Chunk {chunk_num}: {len(data)} records (Total: {total_rows})")
                
                time.sleep(0.1)   
                
            except Exception as e:
                failed_batches += 1
                logger.error(f"✗ Chunk {chunk_num} failed: {str(e)[:200]}")
                
                continue
        
        logger.info(f"✓ {table_name}: {total_rows} rows, {failed_batches} failed batches\n")
        
    except Exception as e:
        logger.error(f"✗ Critical error: {e}")

 

def run_migration():

    Config.validate()
    
    logger.info("=" * 60)
    logger.info("Starting Migration")
    logger.info("=" * 60)
    
    for csv_name, table_name in MIGRATION_ORDER:
        migrate_table(csv_name, table_name)
    
    logger.info("=" * 60)
    logger.info("Migration Completed")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_migration()
