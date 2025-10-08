
import sqlite3
import hashlib
import json
from typing import Optional, List, Tuple
from src.untils.constants import DB_NAME


class DatabaseManager:


    def __init__(self):
        """Initialize database connection and create tables if needed."""
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Users table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                username TEXT UNIQUE,
                                password TEXT,
                                skin_type TEXT DEFAULT 'preset',
                                skin_value TEXT DEFAULT '1',
                                last_level INTEGER DEFAULT 0
                            )
        ''')

        # Scores table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS scores
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER NOT NULL,
                                score INTEGER NOT NULL,                             
                                level INTEGER NOT NULL,
                                time_played REAL NOT NULL,
                                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (user_id)  REFERENCES users(id)               
                            )
        ''')

        # Custom mazes table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS mazes
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                data TEXT NOT NULL,
                                created_by INTEGER NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (created_by)  REFERENCES users(id)  
                            )
        ''')

        # Multiplayer sessions table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS multiplayer_sessions
                            (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                session_code TEXT UNIQUE NOT NULL,
                                host_user_id INTEGER NOT NULL,
                                status TEXT DEFAULT 'waiting',
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (host_user_id)  REFERENCES users(id)
                            )
        ''')

        self.conn.commit()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_user_by_username(self, username: str):
        """Trả về user nếu tồn tại, ngược lại trả về None."""
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone()

    def register_user(self, username: str, password: str):
        """Đăng ký người dùng mới."""
        try:
            hashed_pw = self.hash_password(password)
            self.cursor.execute(
                "INSERT INTO users (username, password, skin_type, skin_value, last_level) VALUES (?, ?, ?, ?, ?)",
                (username, hashed_pw, 'preset', '1', 0)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Lỗi khi đăng ký: {e}")
            return False

    def login_user(self, username: str, password: str):
        """Đăng nhập tài khoản."""
        hashed_pw = self.hash_password(password)
        try:
            self.cursor.execute(
                'SELECT id, username, skin_type, skin_value, last_level FROM users WHERE username = ? AND password = ?',
                (username, hashed_pw)
            )
            result = self.cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'skin_type': result[2],
                    'skin_value': result[3],
                    'last_level': result[4]
                }
            return None
        except Exception as e:
            print(f"Lỗi khi đăng nhập: {e}")
            return None

    def update_user_progress(self, user_id: int, last_level: int):
        self.cursor.execute("UPDATE users SET last_level = ? WHERE id = ?", (last_level, user_id))
        self.conn.commit()

    def get_user_progress(self, user_id: int) -> int:
        self.cursor.execute("SELECT last_level FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_user_skin(self, user_id: int, skin_type: str, skin_value: str):
        self.cursor.execute(
            "UPDATE users SET skin_type = ?, skin_value = ? WHERE id = ?",
            (skin_type, skin_value, user_id)
        )
        self.conn.commit()

    def get_user_skin(self, user_id: int):
        """Lấy thông tin skin hiện tại của user."""
        self.cursor.execute("SELECT skin_type, skin_value FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return {"skin_type": result[0], "skin_value": result[1]}
        return {"skin_type": "preset", "skin_value": "1"}

    def save_score(self, user_id: int, score: int, level: int, time_played: float):
        """Save a game score to the database."""
        self.cursor.execute(
            'INSERT INTO scores (user_id, score, level, time_played) VALUES (?, ?, ?, ?)',
            (user_id, score, level, time_played)
        )
        self.conn.commit()

    def get_leaderboard(self, limit: int = 10) -> List[Tuple]:
        self.cursor.execute('''
                            SELECT u.username, s.score, s.level, s.time_played
                            FROM scores s
                                     JOIN users u ON s.user_id = u.id
                            ORDER BY s.score DESC, s.level DESC LIMIT ?
                            ''', (limit,))
        return self.cursor.fetchall()

    def get_user_best_score(self, user_id: int) -> Optional[int]:
        """Get user's highest score."""
        self.cursor.execute(
            'SELECT MAX(score) FROM scores WHERE user_id = ?',
            (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result[0] else 0

    def save_custom_maze(self, name: str, maze_data: List[List[int]], user_id: int) -> int:
        data_json = json.dumps(maze_data)
        self.cursor.execute(
            'INSERT INTO mazes (name, data, created_by) VALUES (?, ?, ?)',
            (name, data_json, user_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_custom_mazes(self, user_id: Optional[int] = None) -> List[Tuple]:
        if user_id:
            self.cursor.execute('''
                                SELECT m.id, m.name, m.data, m.created_by, u.username
                                FROM mazes m
                                         JOIN users u ON m.created_by = u.id
                                WHERE m.created_by = ?
                                ORDER BY m.created_at DESC
                                ''', (user_id,))
        else:
            self.cursor.execute('''
                                SELECT m.id, m.name, m.data, m.created_by, u.username
                                FROM mazes m
                                         JOIN users u ON m.created_by = u.id
                                ORDER BY m.created_at DESC
                                ''')
        return self.cursor.fetchall()

    def load_custom_maze(self, maze_id: int) -> Optional[List[List[int]]]:
        """Load a custom maze by ID."""
        self.cursor.execute('SELECT data FROM mazes WHERE id = ?', (maze_id,))
        result = self.cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None

    def close(self):
        """Close database connection."""
        self.conn.close()