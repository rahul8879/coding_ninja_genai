def log_request(
    question: str,
    documents_found: int,
    latency_ms: float,
):
    print(
        {
            "question": question,
            "documents_found": documents_found,
            "latency_ms": round(latency_ms, 2),
        }
    )
