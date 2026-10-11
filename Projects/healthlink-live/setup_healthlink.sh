#!/usr/bin/env bash
# Run: bash setup_healthlink.sh [new-project-folder]
# Creates infrastructure only. You write backend/app/main.py yourself.
set -euo pipefail

project_dir="${1:-healthlink-live}"
python_bin="${PYTHON_BIN:-python3.12}"

if ! command -v "$python_bin" >/dev/null 2>&1; then
  echo "Python 3.12 is required. Install it, or set PYTHON_BIN to its executable."
  exit 1
fi
"$python_bin" -c 'import sys; assert sys.version_info[:2] == (3, 12), "Use Python 3.12 to match Docker"'
if [[ -e "$project_dir" ]]; then
  echo "Folder already exists: $project_dir. Choose a NEW folder; nothing was overwritten."
  exit 1
fi

mkdir -p "$project_dir"/{backend/app,backend/tests,frontend,data,evaluations,.github/workflows}
cd "$project_dir"
touch backend/app/__init__.py
cat > backend/app/main.py <<'EOF'
# Step 1: write your FastAPI application here, following the instructions.
EOF

cat > backend/requirements.txt <<'EOF'
# Direct dependencies for step 1 only.
fastapi>=0.115,<1.0
uvicorn>=0.30,<1.0
EOF

cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.env
.env.*
!.env.example
node_modules/
dist/
.DS_Store
*.db
EOF

cat > .dockerignore <<'EOF'
.venv
.git
.env
.env.*
**/__pycache__
**/.pytest_cache
**/node_modules
frontend
data
evaluations
EOF

cat > Dockerfile <<'EOF'
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# Copy dependencies first to reuse Docker's cache when application code changes.
COPY backend/requirements.lock.txt ./requirements.lock.txt
RUN pip install --no-cache-dir -r requirements.lock.txt
RUN useradd --create-home --uid 10001 appuser
COPY --chown=appuser:appuser backend/app ./app
USER appuser
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > compose.yaml <<'EOF'
# Step 1: API only. PostgreSQL is added when we implement persistence.
services:
  api:
    build: .
    ports:
      - "127.0.0.1:8000:8000"
EOF

echo "Creating isolated Python environment..."
"$python_bin" -m venv .venv
echo "Installing step 1 dependencies (internet required)..."
.venv/bin/python -m pip install -r backend/requirements.txt
# Keep Docker on the same resolved package versions as this local environment.
.venv/bin/python -m pip freeze > backend/requirements.lock.txt

cat > README.md <<'EOF'
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
EOF

echo "Setup complete in: $PWD"
echo "Next: open backend/app/main.py and write the health endpoint."
echo "The application will not start until you write that code."
