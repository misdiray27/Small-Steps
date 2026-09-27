import re

MOODS = ["angry","sad","stressed","confused","lonely","bored","tired","anxious","happy","neutral"]

KEYWORDS = {
    "angry": ["angry","mad","furious","rage","irritated","annoyed","frustrated","frustration","hate"],
    "sad": ["sad","upset","cry","crying","down","unhappy","heartbroken","miserable","low"],
    "stressed": ["stress","stressed","pressure","overwhelmed","workload","deadline","tension"],
    "confused": ["confused","confusing","lost","uncertain","don't know","dont know","unclear"],
    "lonely": ["lonely","alone","isolated","no one","nobody","left out"],
    "bored": ["bored","boring","nothing to do","dull","restless"],
    "tired": ["tired","exhausted","sleepy","drained","fatigued","no energy"],
    "anxious": ["anxious","anxiety","worried","worry","nervous","panic","uneasy","scared"],
    "happy": ["happy","great","good","excited","joy","joyful","amazing","proud","calm"],
}

DANGER_TERMS = [
    "kill myself","suicide","suicidal","self harm","self-harm","hurt myself",
    "end my life","want to die","don't want to live","dont want to live"
]

def detect_danger(text: str) -> bool:
    t = text.lower()
    return any(x in t for x in DANGER_TERMS)

def detect_mood(text: str) -> str:
    t = text.lower()
    scores = {m: 0 for m in MOODS}
    for mood, words in KEYWORDS.items():
        for word in words:
            if re.search(r"\b" + re.escape(word) + r"\b", t):
                scores[mood] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] else "neutral"
