import sqlite3
from datetime import datetime
import hashlib

class Database:
    def __init__(self, db_path='messenger.db'):
        self.db_path = db_path
        self.init_tables()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_tables(self):
        """Создание всех таблиц"""
        with self.get_connection() as conn:
            # Пользователи
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    avatar TEXT DEFAULT '👤',
                    status TEXT DEFAULT 'offline',
                    created_at TIMESTAMP
                )
            ''')
            
            # Сообщения
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_id INTEGER,
                    to_id INTEGER,
                    message TEXT,
                    is_read INTEGER DEFAULT 0,
                    timestamp TIMESTAMP,
                    FOREIGN KEY(from_id) REFERENCES users(id),
                    FOREIGN KEY(to_id) REFERENCES users(id)
                )
            ''')
            
            # Чаты
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER,
                    user2_id INTEGER,
                    last_message TEXT,
                    last_message_time TIMESTAMP,
                    UNIQUE(user1_id, user2_id)
                )
            ''')
            conn.commit()
            print("✅ База данных инициализирована")
    
    def register_user(self, username, password):
        """Регистрация пользователя"""
        try:
            hashed = hashlib.sha256(password.encode()).hexdigest()
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO users (username, password, created_at, status) VALUES (?, ?, ?, ?)",
                    (username, hashed, datetime.now(), 'online')
                )
                conn.commit()
                user_id = cursor.lastrowid
                return {'id': user_id, 'username': username}
        except sqlite3.IntegrityError:
            return None
    
    def auth_user(self, username, password):
        """Авторизация пользователя"""
        hashed = hashlib.sha256(password.encode()).hexdigest()
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, username FROM users WHERE username=? AND password=?",
                (username, hashed)
            )
            user = cursor.fetchone()
            return {'id': user[0], 'username': user[1]} if user else None
    
    def get_all_users(self, current_id):
        """Получить всех пользователей кроме себя"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, username, status, avatar FROM users WHERE id != ?",
                (current_id,)
            )
            return [{'id': u[0], 'username': u[1], 'status': u[2], 'avatar': u[3]} for u in cursor.fetchall()]
    
    def get_user_by_id(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT id, username, status FROM users WHERE id=?", (user_id,))
            user = cursor.fetchone()
            return {'id': user[0], 'username': user[1], 'status': user[2]} if user else None
    
    def update_status(self, user_id, status):
        with self.get_connection() as conn:
            conn.execute("UPDATE users SET status=? WHERE id=?", (status, user_id))
            conn.commit()
    
    def save_message(self, from_id, to_id, message):
        """Сохранить сообщение"""
        timestamp = datetime.now()
        with self.get_connection() as conn:
            conn.execute(
                "INSERT INTO messages (from_id, to_id, message, timestamp) VALUES (?, ?, ?, ?)",
                (from_id, to_id, message, timestamp)
            )
            # Обновляем последнее сообщение в чате
            conn.execute('''
                INSERT OR REPLACE INTO chats (user1_id, user2_id, last_message, last_message_time)
                VALUES (?, ?, ?, ?)
            ''', (min(from_id, to_id), max(from_id, to_id), message, timestamp))
            conn.commit()
        return timestamp.strftime("%H:%M")
    
    def get_chat_history(self, user1_id, user2_id):
        """История переписки"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT from_id, message, timestamp, is_read 
                FROM messages 
                WHERE (from_id=? AND to_id=?) OR (from_id=? AND to_id=?)
                ORDER BY timestamp ASC
            ''', (user1_id, user2_id, user2_id, user1_id))
            
            return [{'from_id': row[0], 'message': row[1], 'timestamp': row[2], 'is_read': row[3]} for row in cursor.fetchall()]
    
    def get_chats_list(self, user_id):
        """Список чатов пользователя"""
        with self.get_connection() as conn:
            cursor = conn.execute('''
                SELECT c.user1_id, c.user2_id, c.last_message, c.last_message_time,
                       u.username, u.status, u.avatar
                FROM chats c
                JOIN users u ON (u.id = c.user1_id OR u.id = c.user2_id)
                WHERE (c.user1_id=? OR c.user2_id=?) AND u.id != ?
                ORDER BY c.last_message_time DESC
            ''', (user_id, user_id, user_id))
            
            chats = []
            for row in cursor.fetchall():
                chats.append({
                    'user_id': row[0] if row[0] != user_id else row[1],
                    'username': row[4],
                    'status': row[5],
                    'avatar': row[6],
                    'last_message': row[2],
                    'last_message_time': row[3]
                })
            return chats