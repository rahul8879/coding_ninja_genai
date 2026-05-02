
import os
import uuid
from fastapi import FastAPI, HTTPException
# from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
load_dotenv()

print(load_dotenv())
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, ToolMessage
from bajaj_tools import get_loan_status, get_emi_schedule, calculate_prepayment, process_refund_request


app = FastAPI()
# print(get_loan_status.invoke("BFL2024001"))

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

TOOLS = [get_loan_status, get_emi_schedule, calculate_prepayment, process_refund_request]

llm_with_tools = llm.bind_tools(TOOLS)

tool_map = {
    "get_loan_status":        get_loan_status,
    "get_emi_schedule":       get_emi_schedule,
    "calculate_prepayment":   calculate_prepayment,
    "process_refund_request": process_refund_request,
}


SYSTEM_PROMPT = """You are a professional Bajaj Finance customer support agent.

RULES:
- ALWAYS use the provided tools to fetch real loan data. Never guess or make up numbers.
- If the customer has not given a loan ID (format: BFL followed by digits), ask for it first.
- Format all amounts with ₹ and commas (e.g., ₹8,450).
- Be warm, concise, and professional.
- If a loan is not found, tell the customer and ask them to double-check the loan ID."""


store = {}

def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
    """Return existing chat history or create a new one for this session."""
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def run_chat_turn(user_message:str,session_id):
    history = get_session_history(session_id)
    messages = [{'role':"system","content":SYSTEM_PROMPT}]
    messages.extend(history.messages)
    messages.append(HumanMessage(content=user_message))
    tools_used = []

    response = llm_with_tools.invoke(messages)

    while response.tool_calls:
        messages.append(response)
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tools_used.append(tool_name)

            tool_fn = tool_map.get(tool_name)
            if tool_fn:
                result = tool_fn.invoke(tool_args)
            else:
                result = {"error":"tool is not available"}

            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]

            ))
        response = llm_with_tools.invoke(messages)

    history.add_user_message(user_message)
    history.add_ai_message(response.content)

    return response.content, tools_used


# Input ?? query --> messages --> return --> FE
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None  # None = new session

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    tools_called: list[str] = []


@app.post('/chat',response_model=ChatResponse)
def chat(req:ChatRequest):
    session_id = str(uuid.uuid4())
    reply, tool_called = run_chat_turn(req.message,req.session_id)
    return ChatResponse(reply=reply, session_id=session_id, tools_called=tool_called)
 
