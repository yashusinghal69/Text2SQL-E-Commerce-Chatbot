import logging
import json
from app.text_2_sql.core.state import AgentState
from app.text_2_sql.llm.client import gemini_client

logger = logging.getLogger(__name__)


async def decide_graph_need(state: AgentState) -> AgentState:
    question = state["question"]
    query_result = state["query_result"]
    
    if not query_result or query_result == "No results found." or state.get("error"):
        state["needs_graph"] = False
        state["graph_type"] = ""
        return state
    
    response_schema = {
        "type": "object",
        "properties": {
            "needs_graph": {"type": "boolean"},
            "graph_type": {"type": "string", "enum": ["bar", "line", "pie", "scatter", "none"]},
            "reason": {"type": "string"}
        },
        "required": ["needs_graph", "graph_type", "reason"]
    }
    
    prompt = f"""Analyze the following question and query results to determine if a graph visualization would be helpful.

Question: {question}

Query Results Sample:
{query_result[:500]}...

Determine:
1. Would a graph be helpful for this data? (YES/NO)
2. If yes, what type of graph? (bar, line, pie, scatter)

Consider:
- Trends over time → line chart
- Comparisons between categories → bar chart
- Proportions/percentages → pie chart
- Correlations → scatter plot
- Simple counts or single values → NO graph needed

Respond with:
- needs_graph: true/false
- graph_type: "bar"/"line"/"pie"/"scatter"/"none"
- reason: brief explanation
"""

    try:
        system_prompt = "You are a data visualization expert. Analyze queries and determine if visualization would add value."
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await gemini_client.generate_content(full_prompt, response_schema=response_schema)
        
        decision = json.loads(response)
        state["needs_graph"] = decision.get("needs_graph", False)
        state["graph_type"] = decision.get("graph_type", "none")
        
        logger.info(f"Graph decision: needs_graph={state['needs_graph']}, type={state['graph_type']}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in decide_graph_need: {e}")
        state["needs_graph"] = False
        state["graph_type"] = ""
        return state
