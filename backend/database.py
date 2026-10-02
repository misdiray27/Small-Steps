import sqlite3
from pathlib import Path
DB=Path(__file__).parent/'small_steps.db'
def get_conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
def init_db():
    c=get_conn(); c.executescript('''
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,full_name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,user_type TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS preferences(user_id INTEGER PRIMARY KEY,stress_sources TEXT,other_stress TEXT,meditation_time TEXT,recent_feeling TEXT,meditation_experience TEXT,goals TEXT,support_preference TEXT,language TEXT DEFAULT 'English',FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
CREATE TABLE IF NOT EXISTS checkins(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,mood TEXT,message TEXT,safety_alert INTEGER DEFAULT 0,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS chats(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,role TEXT,message TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS game_scores(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,game TEXT,score INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
CREATE TABLE IF NOT EXISTS meditation_logs(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,session_name TEXT,duration_seconds INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
'''); c.commit(); c.close()
