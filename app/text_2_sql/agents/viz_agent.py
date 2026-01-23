import logging
import json
from app.text_2_sql.core.state import AgentState
from app.text_2_sql.llm.client import gemini_client
from app.text_2_sql.prompts.agent_configs import AGENT_CONFIGS
import pandas as pd

logger = logging.getLogger(__name__)


async def viz_agent(state: AgentState) -> AgentState:
    query_result = state["query_result"]
    graph_type = state["graph_type"]
    question = state["question"]
    
    try:
        results = json.loads(query_result)
        if not results or len(results) == 0:
            state["graph_json"] = ""
            logger.info("No data to visualize")
            return state
        
        df = pd.DataFrame(results)
        columns = df.columns.tolist()
        sample_data = df.head(5).to_dict('records')
        
        prompt = f"""Generate Python code using Plotly to visualize the following data.

Question: {question}
Graph Type: {graph_type}
Columns: {columns}
Sample Data (first 5 rows): {json.dumps(sample_data, indent=2)}
Total Rows: {len(df)}

Requirements:
1. Use plotly.graph_objects or plotly.express
2. The data is already loaded as 'df' (a pandas DataFrame)
3. Create an appropriate {graph_type} chart
4. Limit data to top 20 rows if there are many rows
5. Add proper titles, labels, and formatting
6. The figure variable must be named 'fig'
7. Return ONLY the Python code, no explanations or markdown
8. Do NOT include any import statements
9. Do NOT include code to show the figure (no fig.show())
10. Make the visualization visually appealing with appropriate colors and layout
11. Update the layout for better interactivity (hover info, responsive sizing)

Generate the Plotly code:"""

        system_prompt = AGENT_CONFIGS["viz_agent"]["system_prompt"]
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await gemini_client.generate_content(full_prompt)
        
        plotly_code = response.strip()
        plotly_code = plotly_code.replace("```python", "").replace("```", "").strip()
        
        exec_globals = {
            'df': df,
            'pd': pd,
            'json': json
        }
        
        try:
            import plotly.graph_objects as go
            import plotly.express as px
            exec_globals['go'] = go
            exec_globals['px'] = px
        except ImportError:
            logger.error("Plotly not installed")
            state["graph_json"] = ""
            return state
        
        exec(plotly_code, exec_globals)
        
        fig = exec_globals.get('fig')
        
        if fig is None:
            raise ValueError("Generated code did not create a 'fig' variable")
        
        graph_json = fig.to_json()
        state["graph_json"] = graph_json
        
        logger.info(f"Generated {graph_type} chart successfully")
        
    except Exception as e:
        logger.error(f"Graph generation error: {e}")
        if 'plotly_code' in locals():
            logger.error(f"Generated code:\n{plotly_code}")
        state["graph_json"] = ""
    
    return state
