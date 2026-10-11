# HealthLink — incremental build

This scaffold contains no chatbot implementation. Write backend/app/main.py first.

From this project root:

    source .venv/bin/activate
    python -m uvicorn app.main:app --app-dir backend --reload --port 8000

After writing the health endpoint, visit http://127.0.0.1:8000/health
and http://127.0.0.1:8000/docs.

Stop the local server before running Docker on the same port:

    docker compose up --build

Stop containers with: docker compose down

requirements.txt declares direct dependencies. requirements.lock.txt records
resolved versions; commit both when you initialize Git. On adding dependencies,
install them in .venv and refresh the lock using pip freeze.

Folders for upcoming stages are empty: frontend, data, evaluations,
backend/tests, .github/workflows. Add their contents when teaching those stages.
Docker currently runs ONLY the API, not the future React UI or database.

If dependency installation fails, fix connectivity and resume from this folder:

    .venv/bin/python -m pip install -r backend/requirements.txt
    .venv/bin/python -m pip freeze > backend/requirements.lock.txt
