from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel
from langchain_core.messages import AIMessage
import uuid
import json
from app.agents.core.graph import build_graph
from app.agents.core.state import init_chatbot_state
from langgraph.types import Command

chatbot_router = APIRouter()

class UserInitInput(BaseModel):
    student_id: str
    student_name: str
    
class UserContinueInput(BaseModel):
    thread_id: str
    message: str

graph = build_graph()

async def stream_messages(events: Any, thread_id: str):
    seen_messages = set()  # Sử dụng set để kiểm tra tin nhắn trùng lặp nhanh hơn

    try:
        for event in events:  
            for node, value in event.items():
                if "messages" in value and value["messages"]:
                    message: AIMessage = value["messages"][-1]
                    message_tuple = (message.content, message.type)  # Tạo tuple để so sánh

                    # Kiểm tra tin nhắn trùng lặp
                    if message_tuple not in seen_messages:
                        seen_messages.add(message_tuple)
                        message_dict = {
                            "content": message.content,
                            "type": message.type,
                            "id": message.id,
                            "thread_id": thread_id
                        }
                        if message_dict["type"] == "ai":
                            yield f"data: {json.dumps(message_dict, ensure_ascii=False)}\n\n"

    except Exception as e:
        error_dict = {"error": str(e), "thread_id": thread_id}
        yield f"data: {json.dumps(error_dict, ensure_ascii=False)}\n\n"
        
        
@chatbot_router.post("/init_chatbot", summary="Init chatbot")
async def init_chatbot(user_input: UserInitInput):
    try:
        state = init_chatbot_state()
        state["student_name"] = user_input.student_name
        state["student_id"] = user_input.student_id
        
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Stream các tin nhắn từ graph
        events = graph.stream(state, config)
        return StreamingResponse(
            stream_messages(events, thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@chatbot_router.post("/interact", summary="Interact with chatbot with streaming")
async def interact(user_input: UserContinueInput):
    try:
        thread_id = user_input.thread_id
        if not thread_id:
            raise HTTPException(status_code=400, detail="Thread ID is required")

        config = {"configurable": {"thread_id": thread_id}}
        human_message = Command(resume=user_input.message)

        # Stream các tin nhắn từ graph
        events = graph.stream(human_message, config)
        return StreamingResponse(
            stream_messages(events, thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@chatbot_router.post("/restart", summary="Init chatbot")
async def restart_chatbot(user_input: UserInitInput):
    try:
        state = init_chatbot_state()
        state["student_name"] = user_input.student_name
        state["student_id"] = user_input.student_id
        
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # Stream các tin nhắn từ graph
        events = graph.stream(state, config)
        return StreamingResponse(
            stream_messages(events, thread_id),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))