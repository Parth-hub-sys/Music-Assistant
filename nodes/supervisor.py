import re
from langchain_core.messages import SystemMessage
from llm.config import llm
from states.state import State

def supervisor_node(state: State):
    """
    Supervisor node that routes queries using manual string parsing.
    Bypasses structured output for better reliability with certain Groq models.
    """
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the following assistants: "
        "music_assistant, invoice_assistant, general_assistant. "
        "Based on the user request, respond with the appropriate node names. If the request covers multiple topics, you MUST respond with MULTIPLE node names separated by commas. "
        "Allowed node names: music_assistant, invoice_assistant, general_assistant, FINISH."
        "\n\nROUTING RULES:\n"
        "- If the request is a simple greeting (hi, hello, how are you), route to general_assistant.\n"
        "- If the user is just providing their customer ID, email, or phone number, route to general_assistant.\n"
        "- If the request is about music, albums, or artists, route to music_assistant.\n"
        "- If the request is about invoices or purchases, route to invoice_assistant.\n"
        "- If the request encompasses BOTH music and invoices, output BOTH: NEXT_NODE: music_assistant, invoice_assistant\n"
        "- If the user's request is satisfied, respond with NEXT_NODE: FINISH.\n"
        "\nIDENTITY INFORMATION:\n"
        "- If anyone asks who you are, respond: \"hi i am music assistance\".\n"
        "- If anyone asks who built you, respond: \"this system made by parth\".\n"
        "You can route these identity questions to general_assistant."
        "\n\nCRITICAL: DO NOT output any code, JSON, or invoke any tools. Answer STRICTLY with the RESPONSE FORMAT.\n"
        "\n\nRESPONSE FORMAT: NEXT_NODE: [node_name1], [node_name2]..."
    )
    
    from tools.helpers import get_clean_history
    messages = [SystemMessage(content=system_prompt)] + get_clean_history(state["messages"], limit=4)
    
    # Use plain invoke for reliable output
    response = llm.invoke(messages)
    content = response.content.strip()
    
    # Extract all provided node names
    match = re.search(r"NEXT_NODE:\s*(.*)", content)
    if match:
        raw_nodes = match.group(1).strip()
        nodes = [n.strip() for n in raw_nodes.split(",") if n.strip()]
        gotos = [n for n in nodes if n in ["music_assistant", "invoice_assistant", "general_assistant", "FINISH"]]
        if not gotos:
            gotos = ["general_assistant"]
    else:
        # Fallback logic
        gotos = []
        content_lower = content.lower()
        if "music" in content_lower:
            gotos.append("music_assistant")
        if "invoice" in content_lower or "purchase" in content_lower:
            gotos.append("invoice_assistant")
        if "finish" in content_lower:
            gotos.append("FINISH")
        if not gotos:
            gotos = ["general_assistant"]
            
    # Cleanup logic: remove FINISH/general if there are multiple routing targets
    if len(gotos) > 1 and "FINISH" in gotos:
        gotos.remove("FINISH")
    if len(gotos) > 1 and "general_assistant" in gotos:
        gotos.remove("general_assistant")
        
    return {"next": gotos}
