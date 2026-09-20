from openai import OpenAI
from app.knowledge import RAHUL_CONTEXT

client = OpenAI()


def ask_chatbot(question: str):

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=RAHUL_CONTEXT,
        input=question
    )

    return response.output_text