"""Agent state schema for LangGraph."""

from typing import TypedDict, List, Optional, Dict, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """State schema for the customer support agent."""

    # Conversation messages
    messages: Annotated[List[BaseMessage], add_messages]

    # Customer identification
    customer_id: Optional[int]

    # Current ticket being worked on
    current_ticket_id: Optional[int]

    # History of tool calls
    tool_calls: List[Dict[str, Any]]

    # Additional context
    context: Dict[str, Any]

    # Intent classification
    intent: Optional[str]

    # Confidence score for the current response
    confidence: float

    # Whether to escalate to human
    should_escalate: bool
