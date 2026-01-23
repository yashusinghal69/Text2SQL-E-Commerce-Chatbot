import logging
from app.text_2_sql.core.state import AgentState
from app.text_2_sql.core.schema import SCHEMA_INFO
from app.text_2_sql.llm.client import gemini_client
from app.text_2_sql.prompts.agent_configs import AGENT_CONFIGS

logger = logging.getLogger(__name__)


async def sql_agent(state: AgentState) -> AgentState:
    question = state["question"]
    iteration = state.get("iteration", 0)
    
    prompt = f"""You are a SQL expert. Convert the following natural language question into a valid PostgreSQL query for Supabase.

{SCHEMA_INFO}

Question: {question}

Important Guidelines:
1. Use only the tables and columns mentioned in the schema
2. Use proper JOIN clauses when querying multiple tables
3. Return ONLY the SQL query without any explanation or markdown formatting
4. If the question contains multiple sub-questions, generate separate SQL queries separated by semicolons
5. Use aggregate functions (COUNT, SUM, AVG, etc.) appropriately
6. Add LIMIT clauses for queries that might return many rows (default LIMIT 1000 unless user specifies)
7. Use proper WHERE clauses to filter data
8. For date comparisons, use PostgreSQL date/time functions (DATE_TRUNC, EXTRACT, etc.)
9. Remember IDs are UUIDs, not integers
10. Use proper PostgreSQL syntax (not SQLite)
11. Each SQL statement should be on its own line for clarity when multiple queries are needed

Generate the SQL query:"""

    try:
        system_prompt = AGENT_CONFIGS["sql_agent"]["system_prompt"]
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await gemini_client.generate_content(full_prompt)
        
        sql_query = response.strip()
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        state["sql_query"] = sql_query
        state["iteration"] = iteration + 1
        
        logger.info(f"Generated SQL query (iteration {state['iteration']}): {sql_query[:100]}...")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in sql_agent: {e}")
        state["error"] = f"Failed to generate SQL query: {str(e)}"
        state["iteration"] = iteration + 1
        return state
