from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.store.base import BaseStore
from llm.config import llm
from states.state import State, UserProfile

def load_memory(state: State, config: RunnableConfig, store: BaseStore):
    user_id = str(state.get("customer_id"))
    if not user_id:
        return {"loaded_memory": "None"}
    
    namespace = ("memory_profile", user_id)
    existing_memory = store.get(namespace, "user_memory")
    
    if existing_memory and existing_memory.value:
        profile = existing_memory.value.get("memory")
        if profile:
            formatted = f"Music Preferences: {', '.join(profile.music_preferences)}"
            return {"loaded_memory": formatted}
            
    return {"loaded_memory": "None"}

create_memory_prompt = """You are an expert analyst that is observing a conversation that has taken place between a customer and a customer support assistant. The customer support assistant works for a digital music store, and has utilized a multi-agent team to answer the customer's request. 

You specifically care about saving any music interest the customer has shared about themselves, particularly their music preferences to their memory profile.

The conversation to analyze:
{conversation}

The existing memory profile:
{memory_profile}

Ensure your response is exactly a JSON string with no markdown formatting or extra text. Format:
{{
  "customer_id": "the_id",
  "music_preferences": ["genre1", "artist2"]
}}
"""

def create_memory(state: State, config: RunnableConfig, store: BaseStore):
    user_id = str(state.get("customer_id"))
    if not user_id:
        return
        
    namespace = ("memory_profile", user_id)
    existing_memory_str = state.get("loaded_memory", "None")
    
    from tools.helpers import get_clean_history
    formatted_system_message = SystemMessage(
        content=create_memory_prompt.format(
            conversation=get_clean_history(state["messages"], limit=2), 
            memory_profile=existing_memory_str
        )
    )
    
    import json
    import re
    
    response = llm.invoke([formatted_system_message])
    content = response.content.strip()
    
    # Try to extract json if it hallucinated markdown blocks
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        content = match.group(0)
        
    try:
        updated_memory = json.loads(content)
        updated_memory = UserProfile(**updated_memory)
        store.put(namespace, "user_memory", {"memory": updated_memory})
    except (json.JSONDecodeError, ValueError) as e:
        import warnings
        warnings.warn(f"Memory update skipped for user {user_id}: {e}")

