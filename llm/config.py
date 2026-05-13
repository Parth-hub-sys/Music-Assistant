import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from states.state import UserInput

# Load environment variables from .env file
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize the base LLM
llm = ChatGroq(
    api_key=groq_api_key,
    model="openai/gpt-oss-120b",
    # model="openai/gpt-oss-20b",
    # model="llama-3.1-8b-instant",
    temperature=0
)

# Initialize the structured LLM for user input parsing
structured_llm = llm.with_structured_output(schema=UserInput)
