import os,json
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from database import get_conn,init_db
from models import *
from mood_engine import detect_mood,detect_danger
from ai_chat import reply
app=FastAPI(title='Small Steps API',version='2.1')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
pwd=CryptContext(schemes=['bcrypt'],deprecated='auto')
SESSIONS=[('1-Minute Reset',60,'stress'),('2-Minute Breathing',120,'stress'),('5-Minute Calm',300,'calm'),('Before-Sleep Wind Down',420,'sleep'),('Exam Stress Reset',240,'focus'),('Anger Cooldown',240,'anger'),('Overthinking Reset',300,'overthinking'),('Loneliness Comfort',300,'lonely'),('Confidence Reset',180,'confidence'),('Morning Grounding',180,'morning'),('Afternoon Reboot',120,'afternoon'),('Body Scan',360,'body'),('Focus Before Study',180,'focus'),('Post-College Decompress',300,'evening'),('Social Anxiety Reset',240,'anxiety'),('Tired-Day Recovery',180,'tired'),('Gratitude Pause',120,'positive'),('Self-Compassion Break',240,'sad'),('Mindful Walking Prep',120,'movement'),('Digital Detox Pause',180,'screen'),('Pre-Presentation Calm',180,'performance'),('Night Overthinking Ease',360,'sleep'),('Weekend Reset',300,'reset'),('Deep Relaxation',600,'deep')]
@app.on_event('startup')
def start(): init_db()
@app.get('/')
def root(): return {'status':'ok','service':'Small Steps API'}
@app.post('/api/register')
def register(r:Register):
 if r.password!=r.confirm_password: raise HTTPException(400,'Passwords do not match.')
 c=get_conn()
 if c.execute('SELECT id FROM users WHERE email=?',(r.email,)).fetchone(): c.close(); raise HTTPException(409,'Email already registered.')
 cur=c.execute('INSERT INTO users(full_name,email,password_hash,user_type) VALUES(?,?,?,?)',(r.full_name,r.email,pwd.hash(r.password),r.user_type)); uid=cur.lastrowid
 c.execute('INSERT INTO preferences VALUES(?,?,?,?,?,?,?,?,?)',(uid,json.dumps(r.stress_sources),r.other_stress,r.meditation_time,r.recent_feeling,r.meditation_experience,json.dumps(r.goals),r.support_preference,'English')); c.commit(); row=c.execute('SELECT id,full_name,email,user_type,created_at FROM users WHERE id=?',(uid,)).fetchone(); c.close(); return {'user':dict(row)}
@app.post('/api/login')
def login(r:Login):
 c=get_conn(); row=c.execute('SELECT * FROM users WHERE email=?',(r.email,)).fetchone();
 if not row or not pwd.verify(r.password,row['password_hash']): c.close(); raise HTTPException(401,'Invalid email or password.')
 u={k:row[k] for k in ['id','full_name','email','user_type','created_at']}; c.close(); return {'user':u}
@app.post('/api/analyze')
def analyze(r:Analyze):
 mood,conf=detect_mood(r.message); danger=detect_danger(r.message); c=get_conn(); c.execute('INSERT INTO checkins(user_id,mood,message,safety_alert) VALUES(?,?,?,?)',(r.user_id,mood,r.message,int(danger))); c.commit(); c.close()
 return {'mood':mood,'confidence':conf,'safety_alert':danger,'activities':[{'id':i,'name':n,'category':'Guided practice','description':d,'duration':f'{sec//60} min','game_key':'meditation','icon':'🌿'} for i,(n,sec,tag) in enumerate(SESSIONS,1) if mood in {'stressed','anxious','angry','sad','tired','lonely','bored','confused','neutral','happy'}][:r.count]}
@app.get('/api/meditations')
def meditations(): return {'sessions':[{'id':i+1,'name':n,'duration_seconds':s,'tag':t} for i,(n,s,t) in enumerate(SESSIONS)]}
@app.post('/api/meditation/complete')
def complete(user_id:int,session_id:int):
 n,s,t=SESSIONS[session_id-1]; c=get_conn(); c.execute('INSERT INTO meditation_logs(user_id,session_name,duration_seconds) VALUES(?,?,?)',(user_id,n,s)); c.commit(); c.close(); return {'ok':True}
@app.post('/api/chat')
async def chat(r:Chat):
 danger=detect_danger(r.message); c=get_conn(); c.execute('INSERT INTO chats(user_id,role,message) VALUES(?,?,?)',(r.user_id,'user',r.message)); c.commit(); ans,real=await reply(r.user_id,r.message,r.language); c.execute('INSERT INTO chats(user_id,role,message) VALUES(?,?,?)',(r.user_id,'assistant',ans)); c.commit(); c.close()
 if danger: ans+='\n\nIf you may be in immediate danger or may hurt yourself, please contact a trusted person and your local emergency/crisis service now.'
 return {'reply':ans,'ai_enabled':real,'safety_alert':danger}
@app.put('/api/profile/{uid}')
def profile(uid:int,r:Profile): c=get_conn(); c.execute('UPDATE users SET full_name=? WHERE id=?',(r.full_name,uid)); c.commit(); row=c.execute('SELECT id,full_name,email,user_type,created_at FROM users WHERE id=?',(uid,)).fetchone(); c.close(); return {'user':dict(row)}
@app.put('/api/preferences/{uid}')
def prefs(uid:int,r:Prefs):
 c=get_conn()
 if r.language is not None: c.execute('UPDATE preferences SET language=? WHERE user_id=?',(r.language,uid))
 if r.meditation_time is not None: c.execute('UPDATE preferences SET meditation_time=? WHERE user_id=?',(r.meditation_time,uid))
 c.commit(); c.close(); return {'ok':True}
@app.post('/api/forgot-password')
def forgot(r:Forgot):
 c=get_conn(); exists=c.execute('SELECT id FROM users WHERE email=?',(r.email,)).fetchone(); c.close()
 return {'ok':True,'message':'If that email is registered, reset instructions can be sent. Email delivery must be configured on the server.'}
@app.post('/api/change-password')
def change(r:PasswordChange):
 c=get_conn(); row=c.execute('SELECT password_hash FROM users WHERE id=?',(r.user_id,)).fetchone()
 if not row or not pwd.verify(r.old_password,row['password_hash']): c.close(); raise HTTPException(401,'Current password is incorrect.')
 c.execute('UPDATE users SET password_hash=? WHERE id=?',(pwd.hash(r.new_password),r.user_id)); c.commit(); c.close(); return {'ok':True}
@app.post('/api/game/score')
def game_score(user_id:int, game:str, score:int):
 c=get_conn(); c.execute('INSERT INTO game_scores(user_id,game,score) VALUES(?,?,?)',(user_id,game,score)); c.commit(); c.close(); return {'ok':True}
@app.get('/api/dashboard/{uid}')
def dash(uid:int):
 c=get_conn(); a=c.execute('SELECT COUNT(*) n FROM checkins WHERE user_id=?',(uid,)).fetchone()['n']; ch=c.execute('SELECT COUNT(*) n FROM chats WHERE user_id=?',(uid,)).fetchone()['n']; m=c.execute('SELECT COALESCE(SUM(duration_seconds),0) n FROM meditation_logs WHERE user_id=?',(uid,)).fetchone()['n']; c.close(); return {'checkins':a,'chat_messages':ch,'meditation_minutes':m//60,'activities':len(SESSIONS)}
if __name__=='__main__':
 import uvicorn; uvicorn.run('main:app',host='0.0.0.0',port=int(os.getenv('PORT','8000')))
