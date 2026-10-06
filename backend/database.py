import os
import mysql.connector
from mysql.connector import Error


# MySQL configuration
# Values come from environment variables.
# Local machine and Render can use different databases safely.

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "small_steps"),
}


class MySQLConnection:
    """
    Compatibility wrapper:
    Existing main.py uses SQLite-style conn.execute()
    while the database is MySQL.
    """

    def __init__(self, connection):
        self.connection = connection

    def execute(self, query, params=None):
        # Convert SQLite ? placeholders to MySQL %s
        query = query.replace("?", "%s")

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor

    def cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_conn():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)

        if conn.is_connected():
            return MySQLConnection(conn)

    except Error as e:
        print("MySQL connection error:", e)
        raise


def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            user_type VARCHAR(30),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            user_id INT PRIMARY KEY,
            stress_sources TEXT,
            other_stress TEXT,
            meditation_time VARCHAR(50),
            recent_feeling VARCHAR(100),
            meditation_experience VARCHAR(100),
            goals TEXT,
            support_preference VARCHAR(100),
            language VARCHAR(30) DEFAULT 'English',
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            mood VARCHAR(50),
            message TEXT,
            safety_alert BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            role VARCHAR(20),
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_scores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            game VARCHAR(100),
            score INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS meditation_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            session_name VARCHAR(100),
            duration_seconds INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
        """)

        conn.commit()
        print("MySQL database initialized successfully.")

    finally:
        cursor.close()
        conn.close()