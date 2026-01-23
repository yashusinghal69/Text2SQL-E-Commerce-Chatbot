import logging
from app.text_2_sql.core.state import AgentState
from app.text_2_sql.core.schema import SCHEMA_INFO
from app.text_2_sql.llm.client import gemini_client
from app.text_2_sql.prompts.agent_configs import AGENT_CONFIGS

logger = logging.getLogger(__name__)


async def error_agent(state: AgentState) -> AgentState:
    error = state["error"]
    sql_query = state["sql_query"]
    question = state["question"]
    iteration = state.get("iteration", 0)
    
    if iteration > 3:
        state["final_answer"] = f"I apologize, but I'm having trouble generating a correct SQL query for your question. Error: {error}"
        logger.error(f"Max retry attempts reached for question: {question}")
        return state
    
    prompt = f"""The following SQL query failed with an error. Please fix it.

{SCHEMA_INFO}

Original Question: {question}

Failed SQL Query: {sql_query}

Error: {error}

Generate a corrected SQL query that will work. Return ONLY the SQL query without any explanation or markdown formatting:"""

    try:
        system_prompt = AGENT_CONFIGS["error_agent"]["system_prompt"]
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await gemini_client.generate_content(full_prompt)
        
        corrected_query = response.strip()
        corrected_query = corrected_query.replace("```sql", "").replace("```", "").strip()
        
        state["sql_query"] = corrected_query
        state["error"] = ""
        state["iteration"] = iteration + 1
        
        logger.info(f"Error recovery attempt {iteration + 1}: Generated corrected SQL")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in error_agent: {e}")
        state["error"] = f"Failed to recover from error: {str(e)}"
        state["final_answer"] = "I encountered an error while trying to fix the query. Please try rephrasing your question."
        return state
