from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.prebuilt import ToolNode
from langgraph.types import Send

from states.state import State
from nodes.verification import verify_info
from nodes.human import human_input
from nodes.memory import load_memory, create_memory
from nodes.assistants import (
    music_assistant, invoice_assistant, general_assistant,
    music_formatter, invoice_formatter
)
from nodes.supervisor import supervisor_node
from tools.music_tools import music_tools
from tools.invoice_tools import invoice_tools
from graph.edges import should_interrupt, should_continue

# Initialize checkers and stores
checkpointer = MemorySaver()
in_memory_store = InMemoryStore()

builder = StateGraph(State)

# Add Nodes
builder.add_node("verify_info", verify_info)
builder.add_node("human_input", human_input)
builder.add_node("load_memory", load_memory)
builder.add_node("supervisor", supervisor_node)
builder.add_node("music_assistant", music_assistant)
builder.add_node("music_formatter", music_formatter)
builder.add_node("invoice_assistant", invoice_assistant)
builder.add_node("invoice_formatter", invoice_formatter)
builder.add_node("general_assistant", general_assistant)
builder.add_node("create_memory", create_memory)

_music_tool_node = ToolNode(music_tools)
_invoice_tool_node = ToolNode(invoice_tools)

def call_music_tools(state: State, config):
    target_msg = None
    for m in reversed(state["messages"]):
        if getattr(m, "type", "") == "human":
            break
        if hasattr(m, "tool_calls") and getattr(m, "tool_calls", []):
            if any(c["name"] in [t.name for t in music_tools] for c in m.tool_calls):
                target_msg = m
                break
    if target_msg:
        return _music_tool_node.invoke({"messages": [target_msg]}, config)
    return {"messages": []}

def call_invoice_tools(state: State, config):
    target_msg = None
    for m in reversed(state["messages"]):
        if getattr(m, "type", "") == "human":
            break
        if hasattr(m, "tool_calls") and getattr(m, "tool_calls", []):
            if any(c["name"] in [t.name for t in invoice_tools] for c in m.tool_calls):
                target_msg = m
                break
    if target_msg:
        return _invoice_tool_node.invoke({"messages": [target_msg]}, config)
    return {"messages": []}

# Add Tool Nodes
builder.add_node("music_tool_node", call_music_tools)
builder.add_node("invoice_tool_node", call_invoice_tools)

# Define Edges
builder.add_edge(START, "verify_info")

builder.add_conditional_edges(
    "verify_info",
    should_interrupt,
    {
        "continue": "load_memory",
        "interrupt": "human_input",
    },
)

builder.add_edge("human_input", "verify_info")
builder.add_edge("load_memory", "supervisor")

_VALID_ASSISTANTS = {"music_assistant", "invoice_assistant", "general_assistant"}

def route_supervisor(state: State):
    targets = state.get("next", [])
    assistants = [t for t in targets if t in _VALID_ASSISTANTS]
    if not assistants:
        return "create_memory"
    if len(assistants) == 1:
        return assistants[0]
    # Multi-intent: fan out to all matched assistants in parallel
    return [Send(t, state) for t in assistants]

# Supervisor Routing
builder.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "music_assistant": "music_assistant",
        "invoice_assistant": "invoice_assistant",
        "general_assistant": "general_assistant",
        "create_memory": "create_memory",
    },
)

# Music Linear Pipeline
# If the intent detector triggered a tool, go to tool node. Otherwise go to create_memory.
builder.add_conditional_edges(
    "music_assistant",
    should_continue,
    {
        "continue": "music_tool_node",
        "end": "create_memory",
    },
)
# Once tool is executed, format the result linearly
builder.add_edge("music_tool_node", "music_formatter")
builder.add_edge("music_formatter", "create_memory")

# Invoice Linear Pipeline
builder.add_conditional_edges(
    "invoice_assistant",
    should_continue,
    {
        "continue": "invoice_tool_node",
        "end": "create_memory",
    },
)
# Once tool is executed, format the result linearly
builder.add_edge("invoice_tool_node", "invoice_formatter")
builder.add_edge("invoice_formatter", "create_memory")

builder.add_edge("general_assistant", "create_memory")

builder.add_edge("create_memory", END)

# Compile the graph
graph = builder.compile(
    checkpointer=checkpointer,
    store=in_memory_store
)
