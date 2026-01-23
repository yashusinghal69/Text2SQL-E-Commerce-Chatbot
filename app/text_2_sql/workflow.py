from langgraph.graph import StateGraph, END
from app.text_2_sql.core.state import AgentState
from app.text_2_sql.agents.guardrails_agent import guardrails_agent
from app.text_2_sql.agents.sql_agent import sql_agent
from app.text_2_sql.agents.execute_sql import execute_sql
from app.text_2_sql.agents.analysis_agent import analysis_agent
from app.text_2_sql.agents.error_agent import error_agent
from app.text_2_sql.agents.decide_graph_need import decide_graph_need
from app.text_2_sql.agents.viz_agent import viz_agent
from app.text_2_sql.utils.routing import should_retry, should_generate_graph, check_scope


def create_text2sql_graph():
    
    """Create the LangGraph state graph for Text2SQL with graph generation"""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("guardrails_agent", guardrails_agent)
    workflow.add_node("sql_agent", sql_agent)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("analysis_agent", analysis_agent)
    workflow.add_node("error_agent", error_agent)
    workflow.add_node("decide_graph_need", decide_graph_need)
    workflow.add_node("viz_agent", viz_agent)
    
    workflow.set_entry_point("guardrails_agent")
    
    workflow.add_conditional_edges(
        "guardrails_agent",
        check_scope,
        {
            "in_scope": "sql_agent",
            "out_of_scope": END
        }
    )
    
    workflow.add_edge("sql_agent", "execute_sql")
    
    workflow.add_conditional_edges(
        "execute_sql",
        should_retry,
        {
            "success": "analysis_agent",
            "retry": "error_agent",
            "end": "analysis_agent"
        }
    )
    
    workflow.add_edge("error_agent", "execute_sql")
    workflow.add_edge("analysis_agent", "decide_graph_need")
    
    workflow.add_conditional_edges(
        "decide_graph_need",
        should_generate_graph,
        {
            "viz_agent": "viz_agent",
            "skip_graph": END
        }
    )
    
    workflow.add_edge("viz_agent", END)
    
    return workflow.compile()


text2sql_graph = create_text2sql_graph()


# def save_workflow_diagram(output_path: str = "workflow_diagram.png"):
#     """Save the workflow diagram as a PNG image"""
#     try:
#         graph_image = text2sql_graph.get_graph().draw_mermaid_png()
        
#         with open(output_path, "wb") as f:
#             f.write(graph_image)
        
#         print(f"Workflow diagram saved to: {output_path}")
#     except Exception as e:
#         print(f"Error saving workflow diagram: {e}")


# # Automatically save diagram on module import
# try:
#     import os
#     diagram_path = os.path.join(os.path.dirname(__file__), "workflow_diagram.png")
#     save_workflow_diagram(diagram_path)
# except Exception as e:
#     print(f"Could not auto-generate workflow diagram: {e}")
