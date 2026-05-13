import uuid
import sys
from langchain_core.messages import HumanMessage
from graph.workflow import graph

# Set default encoding to utf-8 for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_customer_query(query: str, thread_id: str = None):
    """Entry point to run a query through the multi-agent system."""
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"--- Processing Query (Thread: {thread_id}) ---")
    print(f"User: {query}")
    
    try:
        result = graph.invoke(
            {"messages": [HumanMessage(content=query)]}, 
            config=config
        )
        
        # Print results safely
        for message in result["messages"]:
            print("="*40)
            print(f"Role: {type(message).__name__}")
            print(message.content)
            if hasattr(message, "tool_calls") and message.tool_calls:
                print(f"Tool Calls: {message.tool_calls}")
            
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    # Persistence for the conversation session
    session_thread_id = str(uuid.uuid4())
    
    print("\n" + "="*50)
    print("Welcome to Music Assistance! (Type 'exit' to quit)")
    print("="*50 + "\n")
    
    # Run the sample query first as requested
    # sample_query = "My phone number is +55 (12) 3923-5555. How much was my most recent purchase? What albums do you have by the Rolling Stones?"
    # print(f"Running Initial Sample Query: {sample_query}\n")
    # run_customer_query(sample_query, thread_id=session_thread_id)
    print("\n" + "-"*40 + "\n")
    
    while True:
        try:
            user_input = input("User >> ").strip()
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nThank you for using Music Assistance. Goodbye!")
                break
                
            if not user_input:
                continue
                
            run_customer_query(user_input, thread_id=session_thread_id)
            print("\n" + "-"*40 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nSession terminated by user.")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
    
