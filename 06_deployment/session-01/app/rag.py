from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from config import Settings
from prompts import get_prompt

def load_policy_documents(data_dir: Path = Path("data/policies")) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(data_dir.glob("*.txt")):
        documents.extend(TextLoader(str(path), encoding="utf-8").load())
    if not documents:
        raise RuntimeError(f"No .txt policy documents found in {data_dir}")
    return documents


def build_vector_store(settings: Settings, rebuild: bool = False) -> Chroma:
    embeddings = OpenAIEmbeddings(model=settings.openai_embedding_model, openai_api_key=settings.openai_api_key)
    collection = "employee-policies"

    if rebuild and settings.chroma_directory.exists():
        # Chroma recreates collection contents; files are preserved intentionally.
        existing = Chroma(
            collection_name=collection,
            persist_directory=str(settings.chroma_directory),
            embedding_function=embeddings,
        )
        existing.delete_collection()

    store = Chroma(
        collection_name=collection,
        persist_directory=str(settings.chroma_directory),
        embedding_function=embeddings,
    )
    if store._collection.count() == 0:
        splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        chunks = splitter.split_documents(load_policy_documents())
        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk"] = index
            chunk.metadata["source"] = Path(chunk.metadata["source"]).name
        store.add_documents(chunks)
    return store



def format_documents(documents: list[Document], max_chars: int) -> str:
    parts = [f"SOURCE: {doc.metadata.get('source')}\n{doc.page_content}" for doc in documents]
    return "\n\n---\n\n".join(parts)[:max_chars]


class PolicyRAG:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.store = build_vector_store(settings)
        self.retriever = self.store.as_retriever(search_kwargs={"k": settings.retrieval_k})
        self.llm = ChatOpenAI(model=settings.openai_model, temperature=0)

    def retrieve(self, question: str) -> list[Document]:
        return self.retriever.invoke(question, config={"run_name": "retrieve_policy_chunks"})
    
    def answer(self, question: str, prompt_version: str) -> tuple[str, list[Document]]:
        documents = self.retrieve(question)
        context = format_documents(documents, self.settings.max_context_chars)
        chain = get_prompt(prompt_version) | self.llm | StrOutputParser()
        
        answer = chain.invoke(
            {"context": context, "question": question},
            config={
                "run_name": f"policy_rag_{prompt_version}",
                "tags": ["session-1", prompt_version],
                "metadata": {"prompt_version": prompt_version},
            },
        )
        return answer, documents



# rag = PolicyRAG(Settings())

# print(rag.answer("How many paid annual leave days do employees receive?", "v1"))




