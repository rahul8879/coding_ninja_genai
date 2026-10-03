def build_prompt(question: str, documents: list[dict]) -> str:
    if not documents:
        context = "No relevant company policy was found."
    else:
        context = "\n\n".join(
            f"[{doc['title']}]\n{doc['text']}"
            for doc in documents
        )

    return f"""
You are an employee policy assistant.

Rules:
1. Answer only from the supplied context.
2. If the context does not contain the answer, say:
   "I could not find this information in the available policy documents."
3. Do not invent company policy.
4. Keep the answer concise.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
""".strip()
