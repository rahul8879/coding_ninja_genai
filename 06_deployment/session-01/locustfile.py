
import os
from locust import HttpUser, between, task
REAL_LLM = os.getenv("LOCUST_REAL_LLM", "true").lower() == "true"


class PolicyAssistantUser(HttpUser):
    wait_time = between(1, 3)
    @task(4)
    def supported_question(self):
        self.client.post(
            "/chat",
            json={
                "question": "How many annual leave days are available?",
                "prompt_version": "v2",
                "generate_answer": REAL_LLM,
            },
            name="POST /chat supported",
        )

    @task(1)
    def unsupported_question(self):
        self.client.post(
            "/chat",
            json={
                "question": "Is an INR 200,000 relocation benefit available?",
                "prompt_version": "v2",
                "generate_answer": REAL_LLM,
            },
            name="POST /chat unsupported",
        )
