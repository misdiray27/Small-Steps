# Small Steps V3 — Wellness + Mental Fitness

This version includes: modern green UI, one-by-one onboarding, advanced Mio AI chat backend, password/account tools, 24 guided activities, 24 meditation sessions, 5 local ambient music tracks with user-controlled playback, and adult-friendly mental fitness mini-games.

## Run backend
`cd backend`
`pip install -r requirements.txt`
`uvicorn main:app --reload --port 8000`

## Frontend
Open `frontend/index.html` with VS Code Live Server. Change `const API` to the local backend while testing, then restore the Render URL before pushing.

## Render
Build: `pip install -r requirements.txt`
Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
Set `OPENAI_API_KEY` for real Mio AI responses.
