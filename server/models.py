from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    password: Optional[str] = None
    avatar: str = '👤'
    status: str = 'offline'
    created_at: Optional[datetime] = None

@dataclass
class Message:
    id: int
    from_id: int
    to_id: int
    message: str
    is_read: bool = False
    timestamp: Optional[datetime] = None

@dataclass
class Chat:
    id: int
    user1_id: int
    user2_id: int
    last_message: str
    last_message_time: datetime

# Типы сообщений для WebSocket
class MessageType:
    AUTH = 'auth'
    AUTH_SUCCESS = 'auth_success'
    AUTH_ERROR = 'auth_error'
    REGISTER = 'register'
    REGISTER_SUCCESS = 'register_success'
    REGISTER_ERROR = 'register_error'
    MESSAGE = 'message'
    NEW_MESSAGE = 'new_message'
    MESSAGE_SENT = 'message_sent'
    GET_USERS = 'get_users'
    USERS_LIST = 'users_list'
    GET_HISTORY = 'get_history'
    HISTORY = 'history'
    USER_ONLINE = 'user_online'
    USER_OFFLINE = 'user_offline'