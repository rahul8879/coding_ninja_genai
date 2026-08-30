# 🚀 Inventra – Application Run Guide

This document explains how to run the **Inventra application locally**.

The application consists of:

- Backend API
- MCP Server
- Frontend
- Database
- AI/Agent components

---

# 1. Project Structure

```text
inventra/
│
├── app/
│   └── Backend application code
│
├── architecture/
│   └── Architecture diagrams / documentation
│
├── data/
│   └── Application datasets
│
├── db/
│   └── Database-related code
│
├── frontend/
│   └── Frontend application
│
├── models/
│   └── Saved ML models
│
├── 01_eda.ipynb
│   └── Exploratory Data Analysis
│
├── 02_data_preprocessing.ipynb
│   └── Data preprocessing
│
├── 03_final_training.ipynb
│   └── Model training
│
├── feature_importance.png
│
├── forecast_model.pkl
│   └── Trained forecasting model
│
├── schema.sql
│   └── Database schema
│
├── requirements.txt
│   └── Python dependencies
│
└── readme.md
```

---

# 2. Prerequisites

Before running the application, make sure you have:

- Python 3.11+
- pip
- Node.js / npm (if required by frontend)
- VS Code
- Required API keys

Check Python:

```bash
python --version
```

Check pip:

```bash
pip --version
```

---

# 3. Create Virtual Environment

From the project root:

### Windows

```bash
python -m venv .venv
```

Activate:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
```

Activate:

```bash
source .venv/bin/activate
```

---

# 4. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure all dependencies are installed successfully before continuing.

---

# 5. Configure Environment Variables

Create a `.env` file in the project root.

Example:

```env
# LLM Configuration
OPENAI_API_KEY=your_api_key_here

# Database Configuration
DATABASE_URL=your_database_url

# Application
ENVIRONMENT=development
```

> ⚠️ Never commit your real `.env` file or API keys to GitHub.

---

# 6. Prepare the Database

The database schema is available in:

```text
schema.sql
```

Initialize/configure the database before starting the backend.

If the project already contains a prepared local database, this step may not be required.

---

# 7. Run the Backend

From the project root:

```bash
uvicorn app.main:app --reload
```

If your FastAPI entry point is different, use the appropriate module path.

Example:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Once the server starts successfully, you should see logs similar to:

```text
INFO: Application startup complete
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

# 8. Verify Backend Health

Open:

```text
http://127.0.0.1:8000/api/v1/health
```

Expected response:

```json
{
  "status": "ok"
}
```

You can also open FastAPI Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 9. MCP Server

Inventra uses an MCP server to expose application capabilities/tools.

When the backend starts successfully, you may see logs similar to:

```text
Starting MCP server 'inventra-inventory'
```

and:

```text
GET /api/v1/health 200 OK
```

This confirms that the application services are running.

---

# 10. Run the Frontend

Open a **new terminal**.

Do not stop the backend.

Navigate to the frontend:

```bash
cd frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The terminal will display the local frontend URL.

Example:

```text
http://localhost:5173
```

Open it in your browser.

---

# 11. Recommended Run Order

Always start the components in this order:

```text
1. Activate Virtual Environment
            ↓
2. Install / Verify Dependencies
            ↓
3. Configure .env
            ↓
4. Prepare Database
            ↓
5. Start Backend
            ↓
6. Verify Health Endpoint
            ↓
7. Verify MCP Server
            ↓
8. Start Frontend
            ↓
9. Open Application
            ↓
10. Test AI / Agent Queries
```

---

# 12. Quick Start

After the initial setup, you normally only need two terminals.

## Terminal 1 – Backend

```bash
# Activate environment first

uvicorn app.main:app --reload
```

## Terminal 2 – Frontend

```bash
cd frontend
npm run dev
```

Then open the frontend URL shown in Terminal 2.

---

# 13. ML Development Workflow

The project also contains the ML development lifecycle.

### Step 1 – EDA

```text
01_eda.ipynb
```

Understand:

- Dataset structure
- Missing values
- Trends
- Relationships
- Data quality

### Step 2 – Data Preprocessing

```text
02_data_preprocessing.ipynb
```

Handles:

- Cleaning
- Feature engineering
- Transformations
- Training data preparation

### Step 3 – Model Training

```text
03_final_training.ipynb
```

Responsible for:

- Training
- Validation
- Model comparison
- Final model selection

The final model is stored as:

```text
forecast_model.pkl
```

---

# 14. Application Flow

At a high level:

```text
User
  │
  ▼
Frontend
  │
  ▼
FastAPI Backend
  │
  ├──────────────► AI / Agent Layer
  │
  ├──────────────► MCP Tools
  │
  ├──────────────► Database
  │
  └──────────────► Forecast Model
                         │
                         ▼
                 forecast_model.pkl
```

The backend acts as the central orchestration layer between the UI,
AI agents, MCP tools, database, and ML model.

---

# 15. Troubleshooting

## `uvicorn` command not found

Run:

```bash
pip install uvicorn
```

---

## Module not found

Make sure the virtual environment is activated:

```bash
pip install -r requirements.txt
```

---

## Port already in use

Run the backend on another port:

```bash
uvicorn app.main:app --reload --port 8001
```

---

## Frontend cannot connect to backend

Check:

1. Backend is running
2. Correct backend URL is configured
3. Correct port is being used
4. CORS configuration allows the frontend
5. `/api/v1/health` returns successfully

---

## Environment variable error

Verify that:

```text
.env
```

exists and contains all required variables.

Restart the backend after modifying `.env`.

---

# 16. How to Stop the Application

For both backend and frontend terminals:

```text
CTRL + C
```

---

# 17. Classroom Demo Checklist

Before starting the live session:

```text
[ ] Virtual environment works
[ ] requirements.txt installs successfully
[ ] .env configured
[ ] Database available
[ ] Backend starts successfully
[ ] /api/v1/health returns 200
[ ] MCP server starts
[ ] Frontend starts
[ ] Frontend communicates with backend
[ ] Forecast model loads successfully
[ ] Sample AI/Agent queries tested
```

---

# 🎯 Final Application

Once everything is running:

```text
Frontend
   ↓
FastAPI
   ↓
Agent / AI Orchestration
   ↓
MCP Tools
   ↓
Business Data + ML Model
   ↓
Final Response
```

You now have the complete **Inventra application running locally**.