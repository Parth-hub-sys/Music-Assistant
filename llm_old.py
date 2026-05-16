from langchain_groq import ChatGroq

import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    api_key="",
    model="openai/gpt-oss-120b",
    temperature=0
)


def answer(query):
    

    response = llm.invoke(query).content
    return response

print(answer("hi"))
