from typing import Annotated, List, Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.managed.is_last_step import RemainingSteps

class State(TypedDict):
    """Represents the state of our LangGraph agent."""
    customer_id: str
    messages: Annotated[list[AnyMessage], add_messages]
    loaded_memory: str
    remaining_steps: RemainingSteps
    next: list[str] # Added for supervisor routing

class UserInput(BaseModel):
    """Schema for parsing user-provided account information."""
    identifier: str = Field(description="Identifier, which can be a customer ID, email, or phone number.")

class UserProfile(BaseModel):
    """Schema for structured user music preferences."""
    customer_id: str = Field(description="The customer ID of the customer")
    music_preferences: List[str] = Field(description="The music preferences of the customer")
