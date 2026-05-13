from sqlalchemy import text
from retrieval.db_engine import engine

def get_customer_id_from_identifier(identifier: str) -> str:
    """Helper to find customer_id based on Email, Phone, or CustomerId string."""
    query = text("""
        SELECT customer_id FROM customer 
        WHERE email = :id OR phone = :id OR CAST(customer_id AS TEXT) = :id
    """)
    with engine.connect() as connection:
        result = connection.execute(query, {"id": identifier})
        row = result.fetchone()
        return str(row[0]) if row else None

from langchain_core.messages import SystemMessage, AIMessage, HumanMessage

def get_clean_history(messages, limit=None):
    """Converts ToolMessages and AIMessages-with-tools into clean strings to prevent backend API renderer crashes on OSS models."""
    clean = []
    sliced = messages[-limit:] if limit else messages
    for msg in sliced:
        if isinstance(msg, AIMessage):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                clean.append(AIMessage(content="[Used internal tool to fetch data]"))
            else:
                clean.append(msg)
        elif getattr(msg, "type", "") == "tool":
            # ToolMessages
            clean.append(SystemMessage(content=f"[Tool Result]: {msg.content}"))
        else:
            clean.append(msg)
    return clean
