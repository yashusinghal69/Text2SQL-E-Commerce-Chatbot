import json
import logging
from app.text_2_sql.core.state import AgentState
from app.text_2_sql.llm.client import gemini_client
from app.text_2_sql.prompts.agent_configs import AGENT_CONFIGS

logger = logging.getLogger(__name__)


async def guardrails_agent(state: AgentState) -> AgentState:
    question = state["question"]
    
    response_schema = {
        "type": "object",
        "properties": {
            "is_in_scope": {"type": "boolean"},
            "is_greeting": {"type": "boolean"},
            "reason": {"type": "string"}
        },
        "required": ["is_in_scope", "is_greeting", "reason"]
    }
    
    prompt = f"""You are a guardrails system for an e-commerce database chatbot. Your job is to determine if a user's question is related to e-commerce data, if it's a greeting, or if it's out of scope.

The chatbot has access to an e-commerce database with information about:
- Customers and their locations
- Orders and order status (data from 2016-2018)
- Products and categories
- Sellers
- Payments
- Reviews
- Shipping and delivery information

Examples of GREETING messages:
- "Hi", "Hello", "Hey"
- "Good morning", "Good afternoon"
- "How are you?"
- Any casual greeting or introduction

Examples of IN-SCOPE questions:
- "How many orders were placed last month?"
- "What are the top selling products?"
- "Show me customer distribution by state"
- "What is the average order value?"
- "Which sellers have the highest ratings?"

Examples of OUT-OF-SCOPE questions:
- Personal questions (e.g., "What is my wife's name?", "Where do I live?")
- Political questions (e.g., "Who should I vote for?", "What do you think about the president?")
- General knowledge (e.g., "What is the capital of France?", "How does photosynthesis work?")
- Unrelated topics (e.g., "Tell me a joke", "What's the weather like?")

User Question: {question}

Analyze the question and respond with:
- is_in_scope: true if about e-commerce data, false otherwise
- is_greeting: true if it's a greeting, false otherwise
- reason: brief explanation

If the question is a greeting, mark is_greeting as true and is_in_scope as false.
If the question is ambiguous but could potentially relate to the e-commerce data, mark it as in_scope."""

    try:
        system_prompt = AGENT_CONFIGS["guardrails_agent"]["system_prompt"]
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = await gemini_client.generate_content(full_prompt, response_schema=response_schema)
        
        result = json.loads(response)
        state["is_in_scope"] = result.get("is_in_scope", False)
        is_greeting = result.get("is_greeting", False)
        
        if is_greeting:
            state["final_answer"] = "Hi! I am your e-commerce assistant. I can answer all the queries related to orders, customers, products, sellers, payments, and reviews between 2016-2018. How can I help you today?"
            logger.info(f"Greeting detected: {question}")
            return state
        
        if not state["is_in_scope"]:
            state["final_answer"] = "I apologize, but your question appears to be out of scope. I can only answer questions about the e-commerce data, including:\n\n- Customer information and locations\n- Orders and order status\n- Products and categories\n- Sellers and their performance\n- Payment information\n- Reviews and ratings\n- Shipping and delivery data\n\nPlease ask a question related to the e-commerce database."
            logger.warning(f"Out of scope question: {question}")
        else:
            logger.info(f"In-scope question: {question}")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in guardrails_agent: {e}")
        state["is_in_scope"] = False
        state["error"] = str(e)
        state["final_answer"] = "I encountered an error processing your request. Please try again."
        return state
