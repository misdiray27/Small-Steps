# Small Steps

**“One small step can change how you feel.”**

Small Steps is a presentation-ready student wellness and mood-based activity MVP. It deliberately stays focused: account creation/login, a transparent prototype mood classifier, mood-specific activity recommendations, genuinely playable mini-games, SQLite persistence, and a simple progress view.

## Features

- Create account and login with full name, email, password, confirmation, and optional student/user type.
- Passwords are hashed before storage.
- FastAPI REST backend + SQLite.
- Mood check-in and transparent keyword/context classifier.
- 100 seeded activity records across the supported moods.
- Randomized mood-appropriate recommendations.
- 12 playable mini-games:
  - Memory Match
  - Reaction Rush
  - Target Blitz
  - Brain Rot Tap
  - Odd One Out
  - Color Clash
  - Number Recall
  - Math Sprint
  - Word Scramble
  - Pattern Rush
  - Rock Paper Scissors
  - Tic-Tac-Toe vs computer
- Game scores and durations are persisted.
- Mood and activity history are retrieved from the backend.
- Safety handling for explicit immediate self-harm/danger language.
- No application data is stored in browser localStorage.

## Technology

- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: Python, FastAPI
- Database: SQLite
- Password hashing: Passlib/bcrypt

## Architecture

```text
Browser / VS Code Live Server
        |
        | REST / JSON
        v
FastAPI (backend/main.py)
        |
        +--> mood_engine.py
        +--> activities.py
        +--> database.py
        |
        v
SQLite (backend/small_steps.db)
```

## How mood analysis works

The prototype uses a transparent keyword/context approach. It checks the user's text against small keyword sets for moods such as angry, sad, stressed, confused, lonely, bored, tired, anxious, and happy. The strongest matching category is returned. If there is no useful match, the mood is `neutral`.

The response includes `"confidence": "prototype"` so the UI does not imply clinical or production-grade AI. Small Steps does not diagnose mental-health conditions.

## How activities are selected

The backend seeds at least 100 records into `activities`. Each activity has a mood, category, description, duration, and a game key. After mood detection, activities are filtered to that mood and shuffled before returning a small recommendation set. This means the same mood does not always produce the same ordering.

## Installation

From the `small-steps/backend` directory:

```powershell
python -m venv .venv
```

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run backend

```powershell
uvicorn main:app --reload --port 8000
```

The API is available at:

`http://127.0.0.1:8000`

FastAPI docs:

`http://127.0.0.1:8000/docs`

## Run frontend

Open `frontend/index.html` using the **VS Code Live Server** extension.

The frontend expects the API at:

`http://127.0.0.1:8000`

If you use another backend port, update the `API` constant near the top of the JavaScript in `frontend/index.html`.

## API endpoints

- `GET /`
- `GET /api/health`
- `POST /api/register`
- `POST /api/login`
- `GET /api/users/{user_id}`
- `POST /api/analyze`
- `POST /api/mood`
- `GET /api/mood/{user_id}`
- `POST /api/game`
- `GET /api/activities/{mood}`

## Database structure

### users
- id
- full_name
- email
- password_hash
- user_type
- created_at

### mood_checkins
- id
- user_id
- mood
- message
- created_at

### activities
- id
- name
- mood
- category
- description
- duration
- game_key

### game_sessions
- id
- user_id
- activity_id
- game_name
- score
- duration
- created_at

The SQLite database is created automatically on backend startup.

## Presentation demo

1. Open Small Steps.
2. Create an account using a full name, email, and password.
3. Enter: `I am extremely angry and frustrated today.`
4. Click **Analyze My Mood**.
5. Show **Detected mood: Angry**.
6. Show the dynamically selected activities.
7. Open **Animal Helper** or **Smash the Stress**.
8. Play the game.
9. Show the score/result.
10. Return to activities.
11. Open **My Progress**.
12. Show the stored mood check-in and game result.

## Limitations

- Authentication is intentionally lightweight for an MVP. There is no JWT/session-token system yet; the frontend keeps the returned user object only in runtime memory.
- The mood classifier is a transparent prototype, not a clinical model.
- The games are intentionally small so the live demonstration remains reliable.
- CORS is permissive for local development.

## Future scope

- Secure JWT or server-side session authentication.
- Email verification and password reset.
- Better accessibility and keyboard controls for games.
- More nuanced recommendation rules.
- Optional anonymous mode.
- More activity types and carefully evaluated wellness content.
- Production database and deployment configuration.

## Safety

Small Steps is a wellness and self-reflection tool, not a medical diagnosis or emergency service. When the check-in contains explicit immediate-danger/self-harm language, the interface pauses recommendations and encourages contacting a trusted person and appropriate local emergency/crisis support.
