from langchain_core.prompts import ChatPromptTemplate

PROMPT_V1 = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful employee-policy assistant. Answer the question using the context."),
        ("human", "Context:\n{context}\n\nQuestion: {question}"),
    ]
)

PROMPT_V2 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an employee-policy assistant. Use ONLY the supplied context. "
            "Never invent limits, eligibility, dates, or benefits. If the answer is "
            "not supported, reply exactly: 'I do not know based on the available policy documents.' "
            "Keep the answer concise and mention the source filename in square brackets.",
        ),
        ("human", "Policy context:\n{context}\n\nEmployee question: {question}"),
    ]
)



PROMPT_V3 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an employee-policy assistant. Use ONLY the supplied context. "
            "Never invent limits, eligibility, dates, or benefits. If the answer is "
            "not supported, reply exactly: 'I do not know based on the available policy documents.' "
            "Keep the answer concise and mention the source filename in square brackets.",
        ),
        ("human", "Policy context:\n{context}\n\nEmployee question: {question}"),
    ]
)
def get_prompt(version: str) -> ChatPromptTemplate:
    if version == "v1":
        return PROMPT_V1
    elif version == "v2":
        return PROMPT_V2
    elif version == "v3":
        return PROMPT_V3
    else:
        raise ValueError(f"Unknown prompt version: {version}")