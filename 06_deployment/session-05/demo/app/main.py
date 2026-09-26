from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS
import os
from contextlib import asynccontextmanager

VECTOR_STORE = None
RAG_CHAIN = None


class ChatRequest(BaseModel):
    question: str

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)



def build_rag():
    docs = TextLoader("data/company_policy.md", encoding="utf-8").load()
    chunks = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=120).split_documents(docs)
    store = FAISS.from_documents(chunks, OpenAIEmbeddings(model="text-embedding-3-small"))
    retriever = store.as_retriever(search_kwargs={"k": 4})

    prompt = ChatPromptTemplate.from_template(
                    """You are a company policy assistant. Answer ONLY from the context.
            If the answer is not present, say: \"I could not find that information in the policy.\"

            Context:
            {context}

            Question:
            {question}
            """)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = ({"context": retriever | format_docs, "question": RunnablePassthrough()} | prompt | llm)

    return store, chain


@asynccontextmanager
async def lifespan(app: FastAPI):
    global VECTOR_STORE, RAG_CHAIN
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured")
    VECTOR_STORE, RAG_CHAIN = build_rag()
    yield


app = FastAPI(title="Production RAG Policy Assistant", version="1.0.0", lifespan=lifespan)

@app.get("/")
def root():
    return {"service": "Production RAG Policy Assistant", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "healthy", "rag_ready": RAG_CHAIN is not None}


@app.post("/chat")
def chat(request: ChatRequest):
    if RAG_CHAIN is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not ready")
    result = RAG_CHAIN.invoke(request.question)
    return {"question": request.question, "answer": result.content}









        





