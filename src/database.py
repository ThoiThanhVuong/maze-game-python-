"""
Database Manager
================
Handles all SQLite database operations including user management,
scores, custom mazes, and multiplayer sessions.
"""

import sqlite3
import hashlib
import json
from typing import Optional, List, Tuple, Dict
from src.untils.constants import DB_NAME


class DatabaseManager:
    """Manages all database operations for the game."""

    def __init__(self):
        """Initialize database connection and create tables if needed."""
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create all necessary database tables."""
        # Users table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS users
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                username
                                TEXT
                                UNIQUE
                                NOT
                                NULL,
                                password
                                TEXT
                                NOT
                                NULL,
                                skin
                                INTEGER
                                DEFAULT
                                1,
                                created_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP
                            )
                            ''')

        # Scores table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS scores
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                user_id
                                INTEGER
                                NOT
                                NULL,
                                score
                                INTEGER
                                NOT
                                NULL,
                                level
                                INTEGER
                                NOT
                                NULL,
                                time_played
                                REAL
                                NOT
                                NULL,
                                completed_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP,
                                FOREIGN
                                KEY
                            (
                                user_id
                            ) REFERENCES users
                            (
                                id
                            )
                                )
                            ''')

        # Custom mazes table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS mazes
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT
                                NOT
                                NULL,
                                data
                                TEXT
                                NOT
                                NULL,
                                created_by
                                INTEGER
                                NOT
                                NULL,
                                created_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP,
                                FOREIGN
                                KEY
                            (
                                created_by
                            ) REFERENCES users
                            (
                                id
                            )
                                )
                            ''')

        # Multiplayer sessions table
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS multiplayer_sessions
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                session_code
                                TEXT
                                UNIQUE
                                NOT
                                NULL,
                                host_user_id
                                INTEGER
                                NOT
                                NULL,
                                status
                                TEXT
                                DEFAULT
                                'waiting',
                                created_at
                                TIMESTAMP
                                DEFAULT
                                CURRENT_TIMESTAMP,
                                FOREIGN
                                KEY
                            (
                                host_user_id
                            ) REFERENCES users
                            (
                                id
                            )
                                )
                            ''')

        self.conn.commit()

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> Optional[int]:
        """
        Register a new user.

        Args:
            username: User's username
            password: User's password (will be hashed)

        Returns:
            User ID if successful, None if username exists
        """
        try:
            hashed_pw = self.hash_password(password)
            self.cursor.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_pw)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def login_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user login.

        Args:
            username: User's username
            password: User's password

        Returns:
            User data dict if successful, None if failed
        """
        hashed_pw = self.hash_password(password)
        self.cursor.execute(
            'SELECT id, username, skin FROM users WHERE username = ? AND password = ?',
            (username, hashed_pw)
        )
        result = self.cursor.fetchone()

        if result:
            return {
                'id': result[0],
                'username': result[1],
                'skin': result[2]
            }
        return None

    def update_user_skin(self, user_id: int, skin_id: int):
        """Update user's selected skin."""
        self.cursor.execute(
            'UPDATE users SET skin = ? WHERE id = ?',
            (skin_id, user_id)
        )
        self.conn.commit()

    def save_score(self, user_id: int, score: int, level: int, time_played: float):
        """Save a game score to the database."""
        self.cursor.execute(
            'INSERT INTO scores (user_id, score, level, time_played) VALUES (?, ?, ?, ?)',
            (user_id, score, level, time_played)
        )
        self.conn.commit()

    def get_leaderboard(self, limit: int = 10) -> List[Tuple]:
        """
        Get top scores for leaderboard.

        Args:
            limit: Number of entries to return

        Returns:
            List of tuples: (username, score, level, time_played)
        """
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
        """
        Save a custom maze to the database.

        Args:
            name: Maze name
            maze_data: 2D list representing the maze
            user_id: ID of the user who created it

        Returns:
            Maze ID
        """
        data_json = json.dumps(maze_data)
        self.cursor.execute(
            'INSERT INTO mazes (name, data, created_by) VALUES (?, ?, ?)',
            (name, data_json, user_id)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_custom_mazes(self, user_id: Optional[int] = None) -> List[Tuple]:
        """
        Get custom mazes.

        Args:
            user_id: If provided, only get mazes by this user

        Returns:
            List of tuples: (id, name, data, created_by, username)
        """
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