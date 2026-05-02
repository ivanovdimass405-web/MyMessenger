import asyncio
import websockets
import json
from database import Database
from models import MessageType

class MessengerServer:
    def __init__(self):
        self.db = Database()
        self.connections = {}  # {user_id: websocket}
        self.user_websockets = {}  # {websocket: user_id}
    
    async def handle_connection(self, websocket):
        """Обработка подключения"""
        user_id = None
        
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # Регистрация
                if data['type'] == MessageType.REGISTER:
                    user = self.db.register_user(data['username'], data['password'])
                    if user:
                        user_id = user['id']
                        self.connections[user_id] = websocket
                        self.user_websockets[websocket] = user_id
                        await websocket.send(json.dumps({
                            'type': MessageType.REGISTER_SUCCESS,
                            'user': user
                        }))
                        await self.broadcast_users()
                    else:
                        await websocket.send(json.dumps({
                            'type': MessageType.REGISTER_ERROR,
                            'message': 'Логин уже занят'
                        }))
                
                # Авторизация
                elif data['type'] == MessageType.AUTH:
                    user = self.db.auth_user(data['username'], data['password'])
                    if user:
                        user_id = user['id']
                        self.connections[user_id] = websocket
                        self.user_websockets[websocket] = user_id
                        self.db.update_status(user_id, 'online')
                        await websocket.send(json.dumps({
                            'type': MessageType.AUTH_SUCCESS,
                            'user': user
                        }))
                        await self.broadcast_users()
                    else:
                        await websocket.send(json.dumps({
                            'type': MessageType.AUTH_ERROR,
                            'message': 'Неверный логин или пароль'
                        }))
                
                # Отправка сообщения
                elif data['type'] == MessageType.MESSAGE:
                    timestamp = self.db.save_message(
                        data['from_id'],
                        data['to_id'],
                        data['message']
                    )
                    
                    # Отправляем собеседнику, если он онлайн
                    if data['to_id'] in self.connections:
                        await self.connections[data['to_id']].send(json.dumps({
                            'type': MessageType.NEW_MESSAGE,
                            'from_id': data['from_id'],
                            'from_name': data['from_name'],
                            'message': data['message'],
                            'timestamp': timestamp
                        }))
                    
                    # Подтверждение отправителю
                    await websocket.send(json.dumps({
                        'type': MessageType.MESSAGE_SENT,
                        'message': data['message'],
                        'timestamp': timestamp
                    }))
                
                # Получить список пользователей
                elif data['type'] == MessageType.GET_USERS:
                    users = self.db.get_all_users(user_id)
                    await websocket.send(json.dumps({
                        'type': MessageType.USERS_LIST,
                        'users': users
                    }))
                
                # Получить историю чата
                elif data['type'] == MessageType.GET_HISTORY:
                    history = self.db.get_chat_history(user_id, data['with_id'])
                    await websocket.send(json.dumps({
                        'type': MessageType.HISTORY,
                        'messages': history
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if user_id:
                if user_id in self.connections:
                    del self.connections[user_id]
                self.db.update_status(user_id, 'offline')
                await self.broadcast_users()
            
            if websocket in self.user_websockets:
                del self.user_websockets[websocket]
    
    async def broadcast_users(self):
        """Отправить список пользователей всем онлайн"""
        for ws in self.connections.values():
            try:
                await ws.send(json.dumps({
                    'type': 'users_update',
                    'online_count': len(self.connections)
                }))
            except:
                pass
    
    async def start(self):
        """Запуск сервера"""
        async with websockets.serve(self.handle_connection, "localhost", 8765):
            print("🚀 WebSocket сервер запущен на ws://localhost:8765")
            print("👥 Ожидание подключений...")
            await asyncio.Future()

if __name__ == "__main__":
    server = MessengerServer()
    asyncio.run(server.start())