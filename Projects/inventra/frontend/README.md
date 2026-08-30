# Inventra AI — React Frontend

A configurable React + Vite frontend for the Inventra FastAPI/LangGraph backend.

## Features

- Clean responsive dashboard
- Chat/copilot interface
- Conversation memory via `thread_id`
- API health indicator
- Reorder status card
- Live-looking agent-flow indicator
- Starter test questions
- Mobile responsive
- Centralized configuration
- No backend URL hardcoding in components

## 1. Install

```bash
npm install
```

## 2. Configure

Copy:

```bash
cp .env.example .env
```

Default:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_API_CHAT_PATH=/api/v1/chat
VITE_API_HEALTH_PATH=/api/v1/health
VITE_APP_NAME=Inventra AI
VITE_APP_SUBTITLE=Weather-aware Inventory Intelligence
```

For another backend, only change `.env`.

## 3. Run backend

From your Inventra Python project:

```bash
uvicorn app.api.main:app --reload
```

## 4. Run frontend

```bash
npm run dev
```

Open:

```text
http://localhost:5173
```

## API contract

The app expects:

```http
POST /api/v1/chat
```

Request:

```json
{
  "message": "Should we reorder SKU001 tomorrow in North?",
  "thread_id": "session-id"
}
```

Response:

```json
{
  "thread_id": "session-id",
  "answer": "....",
  "intent": "reorder_decision",
  "reorder_needed": true,
  "sku": "SKU001",
  "region": "North",
  "target_date": "2026-08-24"
}
```

Health:

```http
GET /api/v1/health
```

## Configuration

All app configuration lives in:

```text
src/config/appConfig.js
```

API calls live in:

```text
src/services/api.js
```

So UI components do not contain backend URLs.

## Project structure

```text
inventra_react_app/
├── src/
│   ├── components/
│   │   ├── ChatBubble.jsx
│   │   ├── FlowStep.jsx
│   │   ├── MetricCard.jsx
│   │   └── StatusPill.jsx
│   │
│   ├── config/
│   │   └── appConfig.js
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── styles.css
│
├── .env.example
├── package.json
└── vite.config.js
```

## Important: CORS

Your FastAPI backend must allow the React dev URL.

For local development, add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, replace the localhost origin with your deployed frontend URL.
