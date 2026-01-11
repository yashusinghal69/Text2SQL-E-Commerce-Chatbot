import os
import psycopg2
from app.text_2_sql.config import Config
from urllib.parse import urlparse

def get_connection():
 
    if not Config.SUPABASE_URL or not Config.SUPABASE_DB_PASSWORD:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_DB_PASSWORD in .env")

    parsed_url = urlparse(Config.SUPABASE_URL)
    project_ref = parsed_url.netloc.split('.')[0]
    
    user = f"postgres.{project_ref}"  
    conn_str = f"postgresql://{user}:{Config.SUPABASE_DB_PASSWORD}@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
    
    return psycopg2.connect(conn_str)

def setup_schema():
    schema_file = "database/schema.sql"
    if not os.path.exists(schema_file):
        print(f"Error: {schema_file} not found.")
        return

    print("Connecting to Supabase PostgreSQL...")
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        with open(schema_file, 'r') as f:
            sql = f.read()
            
        print("Executing schema script...")
        cur.execute(sql)
        conn.commit()
        
        print("Schema setup successfully!")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error setting up schema: {e}")

if __name__ == "__main__":
    Config.validate()
    setup_schema()
