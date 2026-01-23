from app.text_2_sql.core.state import AgentState
import logging

logger = logging.getLogger(__name__)


def should_retry(state: AgentState) -> str:
    """Decide whether to retry after an error"""
    error = state.get("error")
    iteration = state.get("iteration", 0)
    
    logger.info(f"should_retry: error='{error}', iteration={iteration}")
    
    if error:
        if iteration <= 3:
            logger.info(f"Retrying (attempt {iteration})")
            return "retry"
        else:
            logger.info(f"Max retries reached, ending")
            return "end"
    logger.info("No error, continuing to success")
    return "success"


def should_generate_graph(state: AgentState) -> str:
    """Decide whether to generate a graph"""
    needs_graph = state.get("needs_graph", False)
    graph_type = state.get("graph_type", "")
    
    logger.info(f"should_generate_graph: needs_graph={needs_graph}, graph_type={graph_type}")
    
    if needs_graph:
        logger.info("Generating visualization")
        return "viz_agent"
    logger.info("Skipping visualization")
    return "skip_graph"


def check_scope(state: AgentState) -> str:
    """Check if question is in scope to continue processing"""
    is_in_scope = state.get("is_in_scope", True)
    question = state.get("question", "")
    
    logger.info(f"check_scope: is_in_scope={is_in_scope}, question='{question[:50]}'")
    
    if is_in_scope:
        logger.info("Question is in scope, continuing")
        return "in_scope"
    logger.info("Question is out of scope, ending")
    return "out_of_scope"
