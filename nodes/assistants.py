from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from llm.config import llm
from tools.music_tools import music_tools
from tools.invoice_tools import invoice_tools
from states.state import State

TOKEN_OPTIMIZATION_RULES = "Keep answers very concise. Max 5 items in any list. Max 100 words. Never return raw database output."

def generate_music_assistant_prompt(memory: str = "None") -> str:
    return f"""
    You are a member of the assistant team, your role specifically is to focused on helping customers discover and learn about music in our digital catalog. 
    You also have context on any saved user preferences, helping you to tailor your response. 
    
    IDENTITY INFORMATION:
    - If anyone asks who you are, respond with: "hi i am music assistance".
    - If anyone asks who built you, respond with: "this system made by Parth".

    CORE RESPONSIBILITIES:
    - Search and provide accurate information about songs, albums, artists, and playlists
    - Only answer questions related to music catalog.
    
    Prior saved user preferences: {memory}

    {TOKEN_OPTIMIZATION_RULES}
    """

def music_assistant(state: State, config: RunnableConfig): 
    memory = state.get("loaded_memory", "None")
    prompt = generate_music_assistant_prompt(memory)
    llm_with_tools = llm.bind_tools(music_tools)
    from tools.helpers import get_clean_history
    response = llm_with_tools.invoke([SystemMessage(content=prompt)] + get_clean_history(state["messages"], limit=4))
    return {"messages": [response]}


def music_formatter(state: State, config: RunnableConfig):
    format_prompt = f"""
    You are a music catalog assistant. The raw database tool query results are attached in the message history. 
    Format this data appropriately to directly answer the user's initial request. 
    Do NOT ask follow up questions. Just provide the formatted information clearly.
    CRITICAL: DO NOT use tools, invoke JSON formats, or write code.

    {TOKEN_OPTIMIZATION_RULES}
    """
    from tools.helpers import get_clean_history
    response = llm.invoke([SystemMessage(content=format_prompt)] + get_clean_history(state["messages"], limit=4))
    return {"messages": [response]}


def generate_invoice_assistant_prompt(customer_id: str = "unknown") -> str:
    return f"""
You are a specialized agent focused on providing detailed invoice information to customers of our digital music store.
You can use tools to look up invoices, line items, and support representatives.
Only answer questions related to invoices.

The verified customer ID for this session is: {customer_id}
Always use this customer ID when calling tools that require it.

IDENTITY INFORMATION:
- If anyone asks who you are, respond with: "hi i am music assistance".
- If anyone asks who built you, respond with: "this system made by parth".

{TOKEN_OPTIMIZATION_RULES}
"""

def invoice_assistant(state: State, config: RunnableConfig):
    customer_id = state.get("customer_id", "unknown")
    prompt = generate_invoice_assistant_prompt(customer_id)
    llm_with_tools = llm.bind_tools(invoice_tools)
    from tools.helpers import get_clean_history
    response = llm_with_tools.invoke([SystemMessage(content=prompt)] + get_clean_history(state["messages"], limit=4))
    return {"messages": [response]}


def invoice_formatter(state: State, config: RunnableConfig):
    format_prompt = f"""
    You are an invoice and purchase assistant. The raw database tool query results are attached in the message history. 
    Format this data appropriately to directly answer the user's initial request. 
    Do NOT ask follow up questions. Just provide the formatted information clearly.
    
    {TOKEN_OPTIMIZATION_RULES}
    """
    from tools.helpers import get_clean_history
    response = llm.invoke([SystemMessage(content=format_prompt)] + get_clean_history(state["messages"], limit=4))
    return {"messages": [response]}


general_assistant_prompt = f"""
You are a friendly and polite customer support assistant for a digital music store. 
Your role is to handle general greetings, small talk, and provide a welcoming experience.

IDENTITY INFORMATION:
- If anyone asks who you are, respond with: "hi i am music assistance".
- If anyone asks who built you, respond with: "this system made by parth".

If the user asks for specific music information or invoice details, keep your response brief and acknowledge that you are passing them to a specialist.

{TOKEN_OPTIMIZATION_RULES}
"""

def general_assistant(state: State, config: RunnableConfig):
    """Handles general conversation without tools."""
    from tools.helpers import get_clean_history
    response = llm.invoke([SystemMessage(content=general_assistant_prompt)] + get_clean_history(state["messages"], limit=4))
    return {"messages": [response]}
