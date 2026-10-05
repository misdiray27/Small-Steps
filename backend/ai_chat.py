import os
from openai import AsyncOpenAI

from database import get_conn


API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = os.getenv("OPENAI_MODEL", "gpt-6-luna")

client = AsyncOpenAI(
    api_key=API_KEY,
    timeout=25.0,
)


SYSTEM_PROMPT = """
You are Mio, the supportive wellness companion inside the Small Steps app.

Your personality:
- Warm
- Calm
- Human-like
- Friendly
- Non-judgmental
- Conversational
- Never robotic
- Never overly formal

Your job:
Help the user with everyday emotional wellbeing, stress, loneliness,
overthinking, motivation, study pressure, confidence and general wellness.

Important:
- You are NOT a doctor.
- You are NOT a therapist.
- Do not diagnose medical or psychiatric conditions.
- Do not pretend to provide professional medical treatment.
- If a user asks for medical diagnosis, recommend consulting a qualified professional.

Conversation style:
- Understand what the user actually said.
- Respond naturally instead of giving generic motivational quotes.
- Ask a small follow-up question when appropriate.
- Do not give huge lists unless the user asks.
- Keep normal replies around 2-6 short paragraphs.
- Use simple language.
- Match the user's emotional tone.
- If the user is casual, be casual.
- If the user is serious, be calm and serious.
- Never repeatedly say "I am here for you" in every message.

For Hindi:
Reply naturally in Hindi.

For Hinglish:
Reply naturally in Roman Hindi mixed with English.
Example:
"Samajh sakti hoon, kabhi-kabhi jab bahut saari cheezein ek saath
ho jaati hain na, mind completely overloaded feel karta hai."

For English:
Reply naturally in English.

Safety:
If the user expresses immediate danger, suicide, self-harm,
or intention to seriously hurt themselves:
- Do not ignore it.
- Encourage them to contact emergency services or a trusted person immediately.
- Encourage them not to stay alone.
- Keep the response supportive and direct.
"""


def get_history(user_id: int, limit: int = 12):
    conn = get_conn()

    rows = conn.execute(
        """
        SELECT role, message
        FROM chats
        WHERE user_id=?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()

    conn.close()

    rows = list(reversed(rows))

    history = []

    for row in rows:
        role = "user" if row["role"] == "user" else "assistant"

        history.append({
            "role": role,
            "content": row["message"]
        })

    return history


async def reply(user_id: int, message: str, language: str = "English"):

    if not API_KEY:
        return (
            "Mio's AI service is not configured yet. "
            "Please add the OPENAI_API_KEY environment variable on the backend."
        ), False

    language = language or "English"

    language_instruction = f"""
The user's selected language is {language}.

You MUST respond in:
- English if language = English
- Hindi if language = Hindi
- natural Roman Hindi + English if language = Hinglish
"""

    history = get_history(user_id)

    input_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + "\n\n" + language_instruction
        }
    ]

    # Keep recent conversation context.
    for item in history:
        input_messages.append(item)

    # Add current message only if it isn't already in history.
    if not history or history[-1]["role"] != "user" or history[-1]["content"] != message:
        input_messages.append({
            "role": "user",
            "content": message
        })

    try:
        response = await client.responses.create(
            model=MODEL,
            input=input_messages,
            max_output_tokens=350
        )

        answer = response.output_text.strip()

        if not answer:
            return (
                "I understand you. Tell me a little more about "
                "what's going on."
            ), True

        return answer, True

    except Exception as e:
        print("OPENAI ERROR:", repr(e))

        return (
            "I'm having trouble connecting to Mio's AI service right now. "
            "Please try again in a moment."
        ), False