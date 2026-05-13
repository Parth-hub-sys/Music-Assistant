import re
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnableConfig
from llm.config import llm
from tools.helpers import get_customer_id_from_identifier
from states.state import State

verify_info_system_instructions = """
You are a music store agent, where you are trying to verify the customer identity 
as the first step of the customer support process. 
Only after their account is verified, you would be able to support them on resolving the issue. 
In order to verify their identity, one of their customer ID, email, or phone number needs to be provided.
If the customer has not provided the information yet, please ask them for it.
If they have provided the identifier but cannot be found, please ask them to revise it.
"""

structured_system_prompt = """You are a customer service representative responsible for extracting customer identifier.
Only extract the customer's account information from the message history. 
Respond with EXACTLY: IDENTIFIER: [value] or IDENTIFIER: NONE if not provided.
"""

def verify_info(state: State, config: RunnableConfig):
    """Verify the customer's account by parsing their input using manual extraction."""
    if state.get("customer_id") is not None and state.get("customer_id") != "":
        return {"messages": []}

    user_input = state["messages"][-1]
    
    # Manual extraction instead of with_structured_output
    response = llm.invoke([SystemMessage(content=structured_system_prompt)] + [user_input])
    content = response.content.strip()
    
    # Use a regex that allows spaces for phone numbers etc.
    match = re.search(r"IDENTIFIER:\s*(.+)", content)
    identifier = match.group(1).strip() if match else None
    
    if identifier == "NONE":
        identifier = None

    customer_id = None
    if identifier:
        customer_id = get_customer_id_from_identifier(identifier)

    if customer_id:
        from langchain_core.messages import AIMessage
        intent_message = AIMessage(
            content=f"Thank you for providing your information! I was able to verify your account with customer id {customer_id}."
        )
        return {
            "customer_id": str(customer_id),
            "messages": [intent_message]
        }
    else:
        # Ask for info using the standard persona
        response = llm.invoke([SystemMessage(content=verify_info_system_instructions)] + state["messages"])
        return {"messages": [response]}
