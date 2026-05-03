# import bunch of libraries??
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.prompts.registry import prompt_registry
from app.core.config import get_settings

settings = get_settings()

from app.schemas.response import ScamResult


def build_chain(prompt_version:str):
    # step 1 : define your parser
    parser = PydanticOutputParser(pydantic_object=ScamResult)

    # Steo 2 - chatprompt 
    # System message ??
    # Human message
    template_str = prompt_registry.get_template(prompt_version)
    prompt = ChatPromptTemplate([
        ('system',template_str),
        ("human","{message}")
    ]).partial(
        format_instuctions= parser.get_format_instructions()
    )

    # step 3 : defien your llm 
    llm = ChatOpenAI(
        model=settings.openai_model

    )

    # step 4 : LCEL
    chain = prompt | llm | parser

    return chain 


def run_chain(message: str, prompt_version: str = None) -> ScamResult:
    """
    Entry point for single message analysis.
    Resolves version → builds chain → invokes → returns ScamResult.
    """
    version = prompt_version or settings.default_prompt_version

    chain = build_chain(version)

    result: ScamResult = chain.invoke({"message": message})

    # Attach version for traceability
    result.prompt_version_used = version

    return result

