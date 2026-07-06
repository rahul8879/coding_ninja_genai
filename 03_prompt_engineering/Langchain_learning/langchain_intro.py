import langchain
import langchain_openai
import langchain_core

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# from langchain_gemini import ChatGeminiAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
import os
load_dotenv()
chat = ChatOpenAI(model="gpt-4o-mini")
# model_2 = ChatGeminiAI()
result = chat.invoke('What was my last questions')

hf_llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-72B-Instruct",
    provider = 'novita'

)

llm = ChatHuggingFace(llm=hf_llm)

llm.invoke("Hello, how are you?")