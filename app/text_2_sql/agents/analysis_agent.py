import logging
from app.text_2_sql.core.state import AgentState
from app.text_2_sql.llm.client import gemini_client
from app.text_2_sql.prompts.agent_configs import AGENT_CONFIGS

logger = logging.getLogger(__name__)


async def analysis_agent(state: AgentState) -> AgentState:
    question = state["question"]
    sql_query = state["sql_query"]
    query_result = state["query_result"]
    
    prompt = f"""You are a helpful assistant that explains database query results in natural language.

Original Question: {question}

SQL Query Used: {sql_query}

Query Results:
{query_result}

Please provide a clear, concise answer to the original question based on the query results.
Format the answer in a user-friendly way. If the results contain numbers, present them clearly.
If there are multiple queries/results (for multi-part questions), address each part of the question separately.
Use bullet points or numbered lists for multiple answers.

Answer:"""

    try:
        system_prompt = AGENT_CONFIGS["analysis_agent"]["system_prompt"]
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await gemini_client.generate_content(full_prompt)
        
        final_answer = response.strip()
        state["final_answer"] = final_answer
        
        logger.info("Analysis completed successfully")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in analysis_agent: {e}")
        state["error"] = f"Failed to analyze results: {str(e)}"
        state["final_answer"] = "I encountered an error analyzing the results. Please try again."
        return state
