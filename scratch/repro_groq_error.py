import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()

class Router(BaseModel):
    next: Literal["A", "B", "FINISH"]

def test_structured_output():
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="openai/gpt-oss-120b",
        temperature=0
    )
    
    # Test 1: Default (likely tool calling)
    print("Testing default with_structured_output...")
    try:
        structured_llm = llm.with_structured_output(Router)
        res = structured_llm.invoke("who are you?")
        print(f"Result: {res}")
    except Exception as e:
        print(f"Test 1 failed: {e}")

    # Test 2: JSON Mode
    print("\nTesting json_mode...")
    try:
        structured_llm_json = llm.with_structured_output(Router, method="json_mode")
        res = structured_llm_json.invoke("who are you? Please respond in JSON format matching the schema.")
        print(f"Result: {res}")
    except Exception as e:
        print(f"Test 2 failed: {e}")

if __name__ == "__main__":
    test_structured_output()
