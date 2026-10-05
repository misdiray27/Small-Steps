import os
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from database import get_conn, init_db
from models import (
    Register,
    Login,
    Analyze,
    Chat,
    Profile,
    Prefs,
    Forgot,
    PasswordChange,
)
from mood_engine import detect_mood, detect_danger
from ai_chat import reply


app = FastAPI(
    title="Small Steps API",
    version="3.0"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------------

pwd = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ---------------------------------------------------------
# MEDITATION / WELLNESS SESSIONS
# ---------------------------------------------------------

SESSIONS = [
    ("1-Minute Reset", 60, "stress"),
    ("2-Minute Breathing", 120, "stress"),
    ("5-Minute Calm", 300, "calm"),
    ("Before-Sleep Wind Down", 420, "sleep"),
    ("Exam Stress Reset", 240, "focus"),
    ("Anger Cooldown", 240, "anger"),
    ("Overthinking Reset", 300, "overthinking"),
    ("Loneliness Comfort", 300, "lonely"),
    ("Confidence Reset", 180, "confidence"),
    ("Morning Grounding", 180, "morning"),
    ("Afternoon Reboot", 120, "afternoon"),
    ("Body Scan", 360, "body"),
    ("Focus Before Study", 180, "focus"),
    ("Post-College Decompress", 300, "evening"),
    ("Social Anxiety Reset", 240, "anxiety"),
    ("Tired-Day Recovery", 180, "tired"),
    ("Gratitude Pause", 120, "positive"),
    ("Self-Compassion Break", 240, "sad"),
    ("Mindful Walking Prep", 120, "movement"),
    ("Digital Detox Pause", 180, "screen"),
    ("Pre-Presentation Calm", 180, "performance"),
    ("Night Overthinking Ease", 360, "sleep"),
    ("Weekend Reset", 300, "reset"),
    ("Deep Relaxation", 600, "deep"),
]


# ---------------------------------------------------------
# STARTUP
# ---------------------------------------------------------

@app.on_event("startup")
def start():
    init_db()


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Small Steps API",
        "version": "3.0"
    }


# ---------------------------------------------------------
# REGISTER
# ---------------------------------------------------------

@app.post("/api/register")
def register(r: Register):

    if r.password != r.confirm_password:
        raise HTTPException(
            status_code=400,
            detail="Passwords do not match."
        )

    if len(r.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters."
        )

    conn = get_conn()

    existing = conn.execute(
        "SELECT id FROM users WHERE email=?",
        (r.email,),
    ).fetchone()

    if existing:
        conn.close()

        raise HTTPException(
            status_code=409,
            detail="Email already registered."
        )

    cursor = conn.execute(
        """
        INSERT INTO users(
            full_name,
            email,
            password_hash,
            user_type
        )
        VALUES(?,?,?,?)
        """,
        (
            r.full_name,
            r.email,
            pwd.hash(r.password),
            r.user_type,
        ),
    )

    user_id = cursor.lastrowid

    conn.execute(
        """
        INSERT INTO preferences(
            user_id,
            stress_sources,
            other_stress,
            meditation_time,
            recent_feeling,
            meditation_experience,
            goals,
            support_preference,
            language
        )
        VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (
            user_id,
            json.dumps(r.stress_sources),
            r.other_stress,
            r.meditation_time,
            r.recent_feeling,
            r.meditation_experience,
            json.dumps(r.goals),
            r.support_preference,
            r.language or "English",
        ),
    )

    conn.commit()

    row = conn.execute(
        """
        SELECT
            id,
            full_name,
            email,
            user_type,
            created_at
        FROM users
        WHERE id=?
        """,
        (user_id,),
    ).fetchone()

    conn.close()

    return {
        "user": dict(row)
    }


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.post("/api/login")
def login(r: Login):

    conn = get_conn()

    row = conn.execute(
        "SELECT * FROM users WHERE email=?",
        (r.email,),
    ).fetchone()

    if not row:
        conn.close()

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    try:
        valid_password = pwd.verify(
            r.password,
            row["password_hash"]
        )
    except Exception:
        valid_password = False

    if not valid_password:
        conn.close()

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    user = {
        "id": row["id"],
        "full_name": row["full_name"],
        "email": row["email"],
        "user_type": row["user_type"],
        "created_at": row["created_at"],
    }

    conn.close()

    return {
        "user": user
    }


# ---------------------------------------------------------
# MOOD ANALYSIS
# ---------------------------------------------------------

@app.post("/api/analyze")
def analyze(r: Analyze):

    mood, confidence = detect_mood(r.message)

    danger = detect_danger(r.message)

    conn = get_conn()

    conn.execute(
        """
        INSERT INTO checkins(
            user_id,
            mood,
            message,
            safety_alert
        )
        VALUES(?,?,?,?)
        """,
        (
            r.user_id,
            mood,
            r.message,
            int(danger),
        ),
    )

    conn.commit()
    conn.close()

    activities = []

    for i, (name, seconds, tag) in enumerate(SESSIONS, 1):

        activities.append({
            "id": i,
            "name": name,
            "category": "Guided practice",
            "description": f"A {seconds // 60}-minute wellness activity.",
            "duration": f"{seconds // 60} min",
            "game_key": "meditation",
            "icon": "🌿",
        })

        if len(activities) >= max(1, r.count):
            break

    return {
        "mood": mood,
        "confidence": confidence,
        "safety_alert": danger,
        "activities": activities,
    }


# ---------------------------------------------------------
# MEDITATIONS
# ---------------------------------------------------------

@app.get("/api/meditations")
def meditations():

    return {
        "sessions": [
            {
                "id": i + 1,
                "name": name,
                "duration_seconds": seconds,
                "tag": tag,
            }
            for i, (name, seconds, tag) in enumerate(SESSIONS)
        ]
    }


# ---------------------------------------------------------
# MEDITATION COMPLETE
# ---------------------------------------------------------

@app.post("/api/meditation/complete")
def complete(
    user_id: int,
    session_id: int
):

    if session_id < 1 or session_id > len(SESSIONS):
        raise HTTPException(
            status_code=400,
            detail="Invalid session."
        )

    name, seconds, tag = SESSIONS[session_id - 1]

    conn = get_conn()

    conn.execute(
        """
        INSERT INTO meditation_logs(
            user_id,
            session_name,
            duration_seconds
        )
        VALUES(?,?,?)
        """,
        (
            user_id,
            name,
            seconds,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "ok": True
    }# ---------------------------------------------------------
# MIO AI CHAT
# ---------------------------------------------------------

@app.post("/api/chat")
async def chat(r: Chat):

    danger = detect_danger(r.message)

    # -----------------------------------------------------
    # 1. Save USER message and CLOSE connection immediately
    # -----------------------------------------------------

    conn = get_conn()

    try:
        conn.execute(
            """
            INSERT INTO chats(
                user_id,
                role,
                message
            )
            VALUES(?,?,?)
            """,
            (
                r.user_id,
                "user",
                r.message,
            ),
        )

        conn.commit()

    finally:
        conn.close()


    # -----------------------------------------------------
    # 2. Get AI response
    # -----------------------------------------------------

    answer, real_ai = await reply(
        r.user_id,
        r.message,
        r.language,
    )


    # -----------------------------------------------------
    # 3. Safety addition
    # -----------------------------------------------------

    if danger:

        answer += (
            "\n\nIf you may be in immediate danger or think you "
            "may hurt yourself, please contact a trusted person "
            "and your local emergency/crisis service now. "
            "Please do not stay alone."
        )


    # -----------------------------------------------------
    # 4. Save ASSISTANT response with a NEW connection
    # -----------------------------------------------------

    conn = get_conn()

    try:
        conn.execute(
            """
            INSERT INTO chats(
                user_id,
                role,
                message
            )
            VALUES(?,?,?)
            """,
            (
                r.user_id,
                "assistant",
                answer,
            ),
        )

        conn.commit()

    finally:
        conn.close()


    # -----------------------------------------------------
    # 5. Return response
    # -----------------------------------------------------

    return {
        "reply": answer,
        "ai_enabled": real_ai,
        "safety_alert": danger,
    }


# ---------------------------------------------------------
# PROFILE
# ---------------------------------------------------------

@app.put("/api/profile/{uid}")
def profile(
    uid: int,
    r: Profile
):

    conn = get_conn()

    conn.execute(
        """
        UPDATE users
        SET full_name=?
        WHERE id=?
        """,
        (
            r.full_name,
            uid,
        ),
    )

    conn.commit()

    row = conn.execute(
        """
        SELECT
            id,
            full_name,
            email,
            user_type,
            created_at
        FROM users
        WHERE id=?
        """,
        (uid,),
    ).fetchone()

    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return {
        "user": dict(row)
    }


# ---------------------------------------------------------
# PREFERENCES
# ---------------------------------------------------------

@app.put("/api/preferences/{uid}")
def prefs(
    uid: int,
    r: Prefs
):

    conn = get_conn()

    if r.language is not None:

        conn.execute(
            """
            UPDATE preferences
            SET language=?
            WHERE user_id=?
            """,
            (
                r.language,
                uid,
            ),
        )

    if r.meditation_time is not None:

        conn.execute(
            """
            UPDATE preferences
            SET meditation_time=?
            WHERE user_id=?
            """,
            (
                r.meditation_time,
                uid,
            ),
        )

    conn.commit()
    conn.close()

    return {
        "ok": True
    }


# ---------------------------------------------------------
# FORGOT PASSWORD
# ---------------------------------------------------------

@app.post("/api/forgot-password")
def forgot(r: Forgot):

    conn = get_conn()

    conn.execute(
        "SELECT id FROM users WHERE email=?",
        (r.email,),
    ).fetchone()

    conn.close()

    return {
        "ok": True,
        "message": (
            "If that email is registered, reset instructions "
            "can be sent. Email delivery must be configured "
            "on the server."
        ),
    }


# ---------------------------------------------------------
# CHANGE PASSWORD
# ---------------------------------------------------------

@app.post("/api/change-password")
def change(r: PasswordChange):

    conn = get_conn()

    row = conn.execute(
        """
        SELECT password_hash
        FROM users
        WHERE id=?
        """,
        (r.user_id,),
    ).fetchone()

    if not row:
        conn.close()

        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    if not pwd.verify(
        r.old_password,
        row["password_hash"]
    ):
        conn.close()

        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect."
        )

    conn.execute(
        """
        UPDATE users
        SET password_hash=?
        WHERE id=?
        """,
        (
            pwd.hash(r.new_password),
            r.user_id,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "ok": True
    }


# ---------------------------------------------------------
# GAME SCORE
# ---------------------------------------------------------

@app.post("/api/game/score")
def game_score(
    user_id: int,
    game: str,
    score: int
):

    conn = get_conn()

    conn.execute(
        """
        INSERT INTO game_scores(
            user_id,
            game,
            score
        )
        VALUES(?,?,?)
        """,
        (
            user_id,
            game,
            score,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "ok": True
    }


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.get("/api/dashboard/{uid}")
def dash(uid: int):

    conn = get_conn()

    checkins = conn.execute(
        """
        SELECT COUNT(*) n
        FROM checkins
        WHERE user_id=?
        """,
        (uid,),
    ).fetchone()["n"]

    chats = conn.execute(
        """
        SELECT COUNT(*) n
        FROM chats
        WHERE user_id=?
        """,
        (uid,),
    ).fetchone()["n"]

    meditation = conn.execute(
        """
        SELECT COALESCE(
            SUM(duration_seconds),
            0
        ) n
        FROM meditation_logs
        WHERE user_id=?
        """,
        (uid,),
    ).fetchone()["n"]

    conn.close()

    return {
        "checkins": checkins,
        "chat_messages": chats,
        "meditation_minutes": meditation // 60,
        "activities": len(SESSIONS),
    }


# ---------------------------------------------------------
# RUN LOCALLY
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
    )