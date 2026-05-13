import uuid
import sys
import io
from langchain_core.messages import HumanMessage
from graph.workflow import graph

# Set default encoding to utf-8 for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_identity():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    # Test "who are you"
    print("\n--- Testing: 'who are you' ---")
    query1 = "who are you"
    # We skip verification for this test by manually setting a dummy customer_id if needed, 
    # but the graph starts at verify_info.
    # Actually, the identity question should work even if not verified if the LLM answers.
    # But currently verify_info forces an identifier.
    
    # Let's provide a phone number first to get past verification
    graph.invoke({"messages": [HumanMessage(content="My phone number is +55 (12) 3923-5555")]}, config=config)
    
    result = graph.invoke({"messages": [HumanMessage(content=query1)]}, config=config)
    print(f"Response: {result['messages'][-1].content}")

    # Test "who build you"
    print("\n--- Testing: 'who build you' ---")
    query2 = "who build you"
    result = graph.invoke({"messages": [HumanMessage(content=query2)]}, config=config)
    print(f"Response: {result['messages'][-1].content}")

if __name__ == "__main__":
    test_identity()
