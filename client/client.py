import asyncio
import websockets
import json
import threading

class MessengerClient:
    def __init__(self):
        self.websocket = None
        self.user_id = None
        self.username = None
        self.on_message = None
        self.on_users = None
        self.on_history = None
        self.on_auth_success = None
        self.loop = None
    
    async def connect(self, host="localhost", port=8765):
        self.websocket = await websockets.connect(f"ws://{host}:{port}")
        asyncio.create_task(self.listen())
        return True
    
    async def register(self, username, password):
        await self.websocket.send(json.dumps({
            'type': 'register',
            'username': username,
            'password': password
        }))
    
    async def login(self, username, password):
        await self.websocket.send(json.dumps({
            'type': 'auth',
            'username': username,
            'password': password
        }))
    
    async def send_message(self, to_id, message):
        await self.websocket.send(json.dumps({
            'type': 'message',
            'from_id': self.user_id,
            'from_name': self.username,
            'to_id': to_id,
            'message': message
        }))
    
    async def get_users(self):
        await self.websocket.send(json.dumps({'type': 'get_users'}))
    
    async def get_history(self, with_id):
        await self.websocket.send(json.dumps({
            'type': 'get_history',
            'with_id': with_id
        }))
    
    async def listen(self):
        try:
            async for message in self.websocket:
                data = json.loads(message)
                if data['type'] == 'auth_success' or data['type'] == 'register_success':
                    self.user_id = data['user']['id']
                    self.username = data['user']['username']
                    if self.on_auth_success:
                        self.on_auth_success(self.user_id, self.username)
                elif data['type'] == 'new_message' and self.on_message:
                    self.on_message(data)
                elif data['type'] == 'users_list' and self.on_users:
                    self.on_users(data['users'])
                elif data['type'] == 'history' and self.on_history:
                    self.on_history(data['messages'])
        except:
            pass
    
    def run_async(self, coro):
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(coro, self.loop)
        else:
            asyncio.run(coro)

class ClientThread(threading.Thread):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.daemon = True
        self.loop = None
    
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.client.loop = self.loop
        self.loop.run_until_complete(self.client.connect())
        self.loop.run_forever()