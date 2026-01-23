import asyncio
from app.text_2_sql.workflow import text2sql_graph
from app.text_2_sql.core.state import AgentState


async def run_query(question: str):

    initial_state = AgentState(question=question)
    
    # Add recursion limit config to prevent GraphRecursionError
    config = {"recursion_limit": 50}
    
    result = await text2sql_graph.ainvoke(initial_state, config)
    return result


async def main():

    questions = [
        "Hello!",   
        "How many orders were placed?",   
        "Show me the top 5 products by sales",  
    ]
    
    for question in questions:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print('='*60)
        
        result = await run_query(question)
        
        print(f"\nFinal Answer: {result.get('final_answer', 'No answer')}")
        print(f"SQL Query: {result.get('sql_query', 'No SQL')}")
        print(f"Needs Graph: {result.get('needs_graph', False)}")
        print(f"Graph Type: {result.get('graph_type', 'None')}")
        print(f"Iteration: {result.get('iteration', 0)}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    asyncio.run(main())
