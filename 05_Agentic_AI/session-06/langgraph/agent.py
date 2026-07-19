import os
import json
import requests
from typing import TypedDict, Annotated, List, Literal
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO  = "rahul8879/e-comm-agentic-demo"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
BASE_URL = f"https://api.github.com/repos/{GITHUB_REPO}"

llm = ChatOpenAI(model="gpt-4o", temperature=0)

r = requests.get(BASE_URL, headers=HEADERS)
print(f"Repo: {r.json().get('full_name')}")
print(f"Status: {r.status_code}")


