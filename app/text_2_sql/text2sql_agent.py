from __future__ import annotations

from typing import Any, AsyncGenerator, Dict

from app.text_2_sql.core.state import AgentState
from app.text_2_sql.workflow import text2sql_graph


STREAMABLE_NODES = {
    "guardrails_agent",
    "sql_agent",
    "execute_sql",
    "analysis_agent",
    "error_agent",
    "decide_graph_need",
    "viz_agent",
    # Backward-compatible aliases in case node names change in future tutorials.
    "check_guardrails",
    "generate_sql",
    "generate_answer",
    "handle_error",
    "generate_graph",
}


def _state_to_dict(state: Any) -> Dict[str, Any]:
    """Normalize AgentState/dict-like state objects to plain dictionaries."""
    if isinstance(state, AgentState):
        return state.model_dump()

    if hasattr(state, "model_dump"):
        return state.model_dump()

    if isinstance(state, dict):
        return dict(state)

    return {
        "question": "",
        "sql_query": "",
        "query_result": "",
        "final_answer": "",
        "error": str(state),
        "iteration": 0,
        "needs_graph": False,
        "graph_type": "",
        "graph_json": "",
        "is_in_scope": True,
    }


async def process_question_stream(question: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process a natural language question and stream node execution events.

    Yields:
        dict: Event payload with type in {node_start, node_end, error, final}
    """
    initial_state = AgentState(
        question=question,
        sql_query="",
        query_result="",
        final_answer="",
        error="",
        iteration=0,
        needs_graph=False,
        graph_type="",
        graph_json="",
        is_in_scope=True,
    )

    current_state: Dict[str, Any] = _state_to_dict(initial_state)

    try:
        async for event in text2sql_graph.astream_events(
            initial_state,
            config={"recursion_limit": 5},
            version="v1",
        ):
            event_type = event.get("event")
            node_name = event.get("name", "")

            if node_name not in STREAMABLE_NODES:
                continue

            if event_type == "on_chain_start":
                yield {
                    "type": "node_start",
                    "node": node_name,
                    "input": dict(current_state),
                }

            elif event_type == "on_chain_end":
                output = event.get("data", {}).get("output")
                output_dict = _state_to_dict(output)
                current_state.update(output_dict)

                yield {
                    "type": "node_end",
                    "node": node_name,
                    "output": output_dict,
                    "state": dict(current_state),
                }

        yield {
            "type": "final",
            "result": dict(current_state),
        }

    except Exception as exc:
        yield {
            "type": "error",
            "error": str(exc),
            "state": dict(current_state),
        }


if __name__ == "__main__":
    print("=" * 80)
    print("Text2SQL Agent - stream processor module")
    print("=" * 80)
    print("\nThis module is meant to be imported and consumed by a UI/service layer.")
    print("Use process_question_stream(question) for node-by-node async updates.")
