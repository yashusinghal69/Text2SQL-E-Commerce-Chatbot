import logging
import json
from app.text_2_sql.config import Config
from app.text_2_sql.core.state import AgentState
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from urllib.parse import urlparse
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class PostgresClient:
    
    _instance = None
    _pool = None
    _executor = ThreadPoolExecutor(max_workers=10)
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        if not Config.SUPABASE_URL or not Config.SUPABASE_DB_PASSWORD:
            raise ValueError("SUPABASE_URL or SUPABASE_DB_PASSWORD not found in environment variables")
        
        parsed_url = urlparse(Config.SUPABASE_URL)
        project_ref = parsed_url.netloc.split('.')[0]
        
        user = f"postgres.{project_ref}"
        host = "aws-1-ap-south-1.pooler.supabase.com"
        conn_str = f"postgresql://{user}:{Config.SUPABASE_DB_PASSWORD}@{host}:5432/postgres"
        
        self._pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=20,
            dsn=conn_str
        )
        
        logger.info("PostgreSQL connection pool initialized")
    
    def _execute_sync(self, sql_query: str):
        conn = self._pool.getconn()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(sql_query)
            
            if cursor.description:
                results = cursor.fetchall()
                conn.commit()
                return [dict(row) for row in results]
            else:
                conn.commit()
                return []
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
            self._pool.putconn(conn)
    
    async def execute_query(self, sql_query: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self._execute_sync, sql_query)


postgres_client = PostgresClient()


async def execute_sql(state: AgentState) -> AgentState:
    sql_query = state["sql_query"]
    
    if not sql_query:
        state["error"] = "No SQL query to execute"
        state["query_result"] = ""
        return state
    
    try:
        sql_statements = [stmt.strip() for stmt in sql_query.split(';') if stmt.strip()]
        
        all_results = []
        
        for i, statement in enumerate(sql_statements):
            logger.info(f"Executing SQL statement {i+1}/{len(sql_statements)}: {statement[:100]}...")
            
            results = await postgres_client.execute_query(statement)
            
            results_limited = results[:100]
            
            if len(sql_statements) > 1:
                all_results.append({
                    f"query_{i+1}": results_limited,
                    f"query_{i+1}_sql": statement
                })
            else:
                all_results = results_limited
        
        if not all_results:
            state["query_result"] = "No results found."
        else:
            state["query_result"] = json.dumps(all_results, indent=2)
        
        state["error"] = ""
        
        logger.info(f"Query executed successfully")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"SQL Execution Error: {error_msg}")
        state["error"] = f"SQL Execution Error: {error_msg}"
        state["query_result"] = ""
    
    return state
