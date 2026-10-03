from app.retrieval.data import POLICY_DOCUMENTS


def retrieve_documents(question: str, top_k: int = 2):
    query_terms = {
        word.strip(".,?!").lower()
        for word in question.split()
        if len(word.strip(".,?!")) > 2
    }

    scored = []

    for document in POLICY_DOCUMENTS:
        content = f"{document['title']} {document['text']}".lower()
        score = sum(term in content for term in query_terms)
        scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)

    matches = [
        document
        for score, document in scored
        if score > 0
    ]

    return matches[:top_k]
