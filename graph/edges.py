from states.state import State

def should_interrupt(state: State):
    if state.get("customer_id"):
        return "continue"
    return "interrupt"

def should_continue(state: State):
    """
    Explicit tools condition to handle routing to tool nodes.
    """
    messages = state.get("messages", [])
    if not messages:
        return "end"
        
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "continue"
    return "end"
