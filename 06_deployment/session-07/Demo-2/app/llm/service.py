from fastapi import HTTPException


def generate_answer(llm, prompt: str, generate: bool = True) -> str:
    if not generate:
        return (
            "LLM generation disabled. "
            "Relevant policy documents were retrieved successfully."
        )

    if llm is None:
        return (
            "OPENAI_API_KEY is not configured. "
            "Run with generate_answer=false or configure the API key."
        )

    try:
        response = llm.invoke(prompt)
        return response.content

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider error: {str(exc)}",
        )
