from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pathlib import Path
import secrets

from database import get_conn, init_db
from models import RegisterRequest, LoginRequest, AnalyzeRequest, MoodRequest, GameRequest
from mood_engine import detect_mood, detect_danger
from activities import seed_activities, get_recommendations

app = FastAPI(title="Small Steps API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://small-steps-fay1.onrender.com",
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def startup():
    init_db()
    conn = get_conn()
    seed_activities(conn)
    conn.close()

@app.get("/")
def root():
    return {"name":"Small Steps","status":"running"}

@app.get("/api/health")
def health():
    return {"ok": True}

@app.post("/api/register")
def register(req: RegisterRequest):
    if req.password != req.confirm_password:
        raise HTTPException(400, "Passwords do not match.")
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO users(full_name,email,password_hash,user_type) VALUES(?,?,?,?)",
            (req.full_name.strip(), req.email.lower(), pwd_context.hash(req.password), req.user_type)
        )
        conn.commit()
        user_id = cur.lastrowid
        return {"user": {"id":user_id, "full_name":req.full_name.strip(), "email":req.email.lower(), "user_type":req.user_type}}
    except Exception as e:
        if "UNIQUE" in str(e):
            raise HTTPException(409, "An account with this email already exists.")
        raise HTTPException(500, "Could not create your account.")
    finally:
        conn.close()

@app.post("/api/login")
def login(req: LoginRequest):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE email=?", (req.email.lower(),)).fetchone()
    conn.close()
    if not row or not pwd_context.verify(req.password, row["password_hash"]):
        raise HTTPException(401, "Incorrect email or password.")
    return {"user":{"id":row["id"],"full_name":row["full_name"],"email":row["email"],"user_type":row["user_type"]}}

@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    conn = get_conn()
    row = conn.execute("SELECT id,full_name,email,user_type,created_at FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "User not found.")
    return {"user":dict(row)}

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    if not req.message.strip():
        raise HTTPException(400, "Tell us a little about how you're feeling first.")
    mood = detect_mood(req.message)
    danger = detect_danger(req.message)
    conn = get_conn()
    activities = [] if danger else get_recommendations(conn, mood, req.count)
    conn.close()
    return {
        "mood": mood,
        "confidence": "prototype",
        "safety_alert": danger,
        "activities": activities
    }

@app.post("/api/mood")
def save_mood(req: MoodRequest):
    conn = get_conn()
    cur = conn.execute("INSERT INTO mood_checkins(user_id,mood,message) VALUES(?,?,?)",
                       (req.user_id, req.mood, req.message))
    conn.commit()
    conn.close()
    return {"id":cur.lastrowid, "saved":True}

@app.get("/api/mood/{user_id}")
def mood_history(user_id: int):
    conn = get_conn()
    moods = conn.execute(
        "SELECT id,mood,message,created_at FROM mood_checkins WHERE user_id=? ORDER BY id DESC LIMIT 20",
        (user_id,)
    ).fetchall()
    games = conn.execute(
        """SELECT g.id,g.game_name,g.score,g.duration,g.created_at,a.category
           FROM game_sessions g LEFT JOIN activities a ON a.id=g.activity_id
           WHERE g.user_id=? ORDER BY g.id DESC LIMIT 20""", (user_id,)
    ).fetchall()
    conn.close()
    return {"moods":[dict(x) for x in moods], "games":[dict(x) for x in games]}

@app.post("/api/game")
def save_game(req: GameRequest):
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO game_sessions(user_id,activity_id,game_name,score,duration) VALUES(?,?,?,?,?)",
        (req.user_id, req.activity_id, req.game_name, req.score, req.duration)
    )
    conn.commit()
    conn.close()
    return {"id":cur.lastrowid, "saved":True}

@app.get("/api/activities/{mood}")
def activities_for_mood(mood: str):
    conn = get_conn()
    result = get_recommendations(conn, mood, 8)
    conn.close()
    return {"mood":mood, "activities":result}
