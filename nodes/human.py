from langgraph.types import interrupt
from langchain_core.messages import HumanMessage
from states.state import State

def human_input(state: State):
    """Node that triggers an interrupt for human input when verification fails."""
    user_response = interrupt("Please provide your Customer ID, Email, or Phone number to verify your identity.")
    return {"messages": [HumanMessage(content=user_response)]}
