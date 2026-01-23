from pydantic import BaseModel, Field
from typing import Optional, Any


class AgentState(BaseModel):
    question: str
    sql_query: str = ""
    query_result: str = ""
    final_answer: str = ""
    error: str = ""
    iteration: int = Field(default=0, ge=0, le=10)
    needs_graph: bool = False
    graph_type: str = ""
    graph_json: str = ""
    is_in_scope: bool = True
    
    class Config:
        validate_assignment = True
    
    def __getitem__(self, key: str) -> Any:
        """Support dictionary-style access for LangGraph compatibility"""
        return getattr(self, key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Support dictionary-style assignment for LangGraph compatibility"""
        setattr(self, key, value)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Support dict.get() method for LangGraph compatibility"""
        return getattr(self, key, default)
