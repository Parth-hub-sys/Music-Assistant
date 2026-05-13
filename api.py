from dotenv import load_dotenv
load_dotenv()

import uuid
from typing import Optional
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from graph.workflow import graph

app = FastAPI(title="Music Store Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None


@app.post("/api/chat")
async def chat(request: ChatRequest):
    thread_id = request.thread_id or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    try:
        prev_state = graph.get_state(config)
        existing_count = len(prev_state.values.get("messages", [])) if prev_state.values else 0
        is_interrupted = "human_input" in (prev_state.next or [])

        if is_interrupted:
            result = graph.invoke(Command(resume=request.message), config)
        else:
            result = graph.invoke(
                {"messages": [HumanMessage(content=request.message)]},
                config,
            )

        all_messages = result.get("messages", [])
        new_messages = all_messages[existing_count:]

        tool_calls_made = []
        response_parts = []

        for msg in new_messages:
            if isinstance(msg, AIMessage):
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        name = tc["name"]
                        if name not in tool_calls_made:
                            tool_calls_made.append(name)
                elif msg.content:
                    response_parts.append(str(msg.content))

        new_state = graph.get_state(config)
        now_interrupted = bool(new_state.next)

        content = "\n\n".join(response_parts) if response_parts else "Processing your request..."

        return {
            "thread_id": thread_id,
            "content": content,
            "tool_calls": [{"name": n} for n in tool_calls_made],
            "interrupted": now_interrupted,
            "success": True,
        }

    except Exception as e:
        return {
            "thread_id": thread_id,
            "content": f"Something went wrong: {str(e)}",
            "tool_calls": [],
            "interrupted": False,
            "success": False,
        }


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Music Store Assistant"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
