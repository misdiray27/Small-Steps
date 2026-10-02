import os
from database import get_conn
SYSTEM='''You are Mio, a warm supportive companion in Small Steps. Listen before advising, ask one useful follow-up question, and offer small practical next steps. Never diagnose or claim to replace a doctor or therapist. For self-harm or immediate danger, encourage immediate local emergency/crisis support and a trusted person. Adapt to English, Hindi or Hinglish.'''
def fallback(t):
 t=t.lower()
 if any(x in t for x in ['sad','cry','upset']): return "I'm listening. What part of today is hurting the most?"
 if any(x in t for x in ['stress','stressed','exam','pressure']): return "That sounds heavy. What is the one thing creating the most pressure right now?"
 if any(x in t for x in ['bored','boring']): return "Let's change the energy. Do you want a quick activity, a two-minute reset, or just a conversation?"
 if any(x in t for x in ['tired','exhausted','drained']): return "Your energy sounds low. Would you rather rest, talk it out, or do one tiny task together?"
 return "I'm here. Tell me what happened in your own words. Do you want me to listen, help you solve it, or distract you?"
async def reply(uid,msg,lang):
 key=os.getenv('OPENAI_API_KEY')
 if not key: return fallback(msg),False
 try:
  from openai import OpenAI
  c=OpenAI(api_key=key); db=get_conn(); rows=db.execute('SELECT role,message FROM chats WHERE user_id=? ORDER BY id DESC LIMIT 12',(uid,)).fetchall(); db.close()
  inp=[{'role':'system','content':SYSTEM+' Reply in '+lang+'.'}]+[{'role':'assistant' if r['role']=='assistant' else 'user','content':r['message']} for r in reversed(rows)]+[{'role':'user','content':msg}]
  r=c.responses.create(model=os.getenv('OPENAI_MODEL','gpt-4.1-mini'),input=inp); return r.output_text,True
 except Exception: return fallback(msg),False
