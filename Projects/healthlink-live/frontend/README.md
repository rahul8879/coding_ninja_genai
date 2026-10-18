# HealthLink frontend

A React/Vite care-navigation interface for the existing HealthLink Stage 2 backend. Frontend only. No login, fabricated doctors, mock chat or bundled API credentials.

## Run locally

1. Start your existing backend on `http://127.0.0.1:8000` with its database and OpenAI configuration.
2. Extract this ZIP. Open a terminal inside this folder (the folder with package.json).
3. Use Node.js 22.12 or later on a supported Node release. Check `node --version`.
4. Run:

```bash
npm ci
npm run dev
```

5. Open `http://localhost:5173`. Use **Start a conversation**.

If replacing an existing frontend: stop its Vite process, keep a backup of that frontend folder, and use this folder as the replacement. Do not copy node_modules from the old folder. The backend is unchanged.

## API contract

Browser requests use `/api`. The Vite development proxy forwards them to port 8000 and removes `/api`.

| Request | Expected result |
|---|---|
| POST /conversations | `{ "id": "conversation-uuid" }` |
| GET /conversations/{id}/messages | `{ "messages": [{ "id": 1, "role": "user", "content": "...", "status": "completed", "created_at": "..." }] }` |
| POST /conversations/{id}/messages | Body `{ "message": "..." }`; response `{ "reply": "...", "booking_proposal": null }` or a proposal |
| POST /appointments | Booking receipt including `appointment_id`; 201 for a new booking or 200 for an idempotent replay |

Proposal fields: `proposal_id`, `doctor_id`, `doctor_name`, `starts_at`, `ends_at`. Datetimes must contain a timezone. Booking sends `conversation_id`, `doctor_id`, `starts_at`, and `idempotency_key` equal to `proposal_id`.

To change backend host/port, edit `target` in `vite.config.js`. Keep secrets in the backend. Do not place OpenAI/Langfuse secret keys in VITE_ variables.

## Booking behaviour

- A real `booking_proposal` response creates the appointment card.
- Chat sending and new-conversation creation pause while the card is open. This makes the required button action clear and avoids the “yes / confirm?” chat loop.
- Click **Confirm booking** to call the booking API. The UI does not invent a confirmation based on assistant text.
- Success displays the returned appointment ID. Close the receipt to continue chatting.
- Dismiss an unsubmitted proposal to choose another time.
- A network/server failure is treated as uncertain. Retry uses the exact same idempotency key. Chat/card dismissal stays blocked until the result is resolved.
- Session storage retains the active conversation, proposal and confirmation receipt across reloads in that tab when browser storage is available. It is not the database, not an audit log and not cross-device history. Clearing storage/closing the browser tab can remove it.
- The displayed receipt reflects the successful booking response. There is no status-refresh endpoint in this frontend contract.

Frontend cannot fix incorrect tool selection, hallucinated doctor details or backend conversation-memory errors. If the assistant says “review the card” but the card does not appear, inspect the message response for `booking_proposal`.

The current backend may not know that a button booking succeeded when answering a later chat question. The receipt is authoritative evidence of the API response; add a backend booking-status tool to answer those questions reliably.

## Files

- src/App.jsx: layout, chat history, API calls and proposal handling.
- src/BookingConfirmation.jsx: booking request, retry and receipt states.
- src/api.js: HTTP requests.
- src/storage.js: browser-session convenience persistence.
- src/MessageContent.jsx: safe basic text/bold/bullet rendering. Not a full Markdown parser.
- src/Icon.jsx: inline SVG icons, no external icon/font dependency.
- src/index.css: responsive light-theme styling.

## Build and hosting

```bash
npm run build
```

Build output is `dist/`. Production hosting must route `/api/*` to the backend with the same prefix removal. The development proxy is not a production deployment configuration. `npm run preview` is for checking the built static assets, not a substitute for configuring the production API route.

## Student demonstration

1. Start conversation, ask “Show me dermatologists.”
2. Select a returned doctor and a concrete date within the backend booking window.
3. Choose a returned available slot and explicitly ask to book it.
4. Check that the confirmation card appears.
5. Confirm using the button; inspect the appointment ID and database record.
6. Reload the tab to inspect retained UI state; dismiss/close the card before continuing chat.

The UI labels the single demo patient and care-navigation limitations. It has no fake online status or claims of medical certification. Use synthetic data for demonstrations.

## Verification supplied with this package

The production build was verified with `npm run build`. Live backend/LLM calls were not run for this delivery. Automated browser verification could not be completed because a browser binary could not be downloaded in the build environment. Use the demonstration checklist above to verify against your running backend before your session.
