# Small Steps V3 — Implementation Guide

## 1. Keep your old project safe
Make a backup of your current `small-steps-project` folder before replacing anything.

## 2. Extract this ZIP
Extract the ZIP. The main folder is `Small_Steps_V2`.

Inside it:
- `backend/` = FastAPI + SQLite + AI chat APIs
- `frontend/` = website
- `frontend/assets/small-steps-logo.png` = the original Small Steps logo supplied from the reference screenshot
- `frontend/audio/` = meditation/ambient audio

## 3. Copy into VS Code
Do NOT delete your old project first.

Recommended:
1. Rename your current project to `small-steps-project-backup`.
2. Create a new folder named `small-steps-project`.
3. Copy everything from `Small_Steps_V2` into it.
4. Open that new folder in VS Code.

## 4. Backend setup
Open PowerShell in the project folder:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

If PowerShell blocks activation, run the backend using the existing Python environment or use:

```powershell
python -m uvicorn main:app --reload --port 8000
```

## 5. Test the backend
Open:

`http://127.0.0.1:8000/docs`

If Swagger/OpenAPI appears, the backend is running.

## 6. Frontend local test
Open `frontend/index.html` using VS Code Live Server.

The frontend currently points to:

`https://small-steps-backend-8cjh.onrender.com`

For local backend testing, change:

```js
const API='https://small-steps-backend-8cjh.onrender.com';
```

to:

```js
const API='http://127.0.0.1:8000';
```

Before pushing the frontend to Render, change it back to the Render backend URL.

## 7. AI chat requirement
The backend supports the AI chat through the OpenAI API. For real AI responses on Render, add `OPENAI_API_KEY` in the backend Render service Environment Variables.

Do NOT put the OpenAI key inside `index.html` or commit it to GitHub.

## 8. GitHub
From the project root (the folder containing `backend` and `frontend`):

```powershell
git status
git add .
git commit -m "Small Steps V3 adult wellness update"
git push
```

If Git says `not a git repository`, run `git status` first. You are probably one folder above/below the repository.

## 9. Backend Render service
Your existing backend service should point to the backend folder.

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Python runtime should be 3.12 rather than 3.14 for this project.

## 10. Frontend Render service
The frontend is a Static Site.

Build command:

```text
echo "No build required"
```

Publish directory:

```text
frontend
```

If your Render frontend already deploys from the repository root and the HTML is in the correct publish directory, keep the existing working configuration rather than creating a second frontend service.

## 11. Final order
Do it in this order:

1. Backup old project.
2. Copy V3 files.
3. Test backend locally.
4. Test frontend locally.
5. Confirm logo, AI chat, activities, meditation and games.
6. Commit and push to GitHub.
7. Let Render deploy backend.
8. Check backend `/docs`.
9. Let Render deploy frontend.
10. Open the live frontend and test registration/login/chat/activities/music/games/dashboard.

## 12. Important
The supplied logo is intentionally preserved as an image. Do not replace it with a generated icon or another brand mark.
