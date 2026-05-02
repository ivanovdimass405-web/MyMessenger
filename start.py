import subprocess
import time
import os
import sys

def start_server():
    """Запуск сервера в отдельном процессе"""
    server_path = os.path.join(os.path.dirname(__file__), "server", "server.py")
    return subprocess.Popen([sys.executable, server_path])

def start_client():
    """Запуск клиента"""
    client_path = os.path.join(os.path.dirname(__file__), "client", "main.py")
    return subprocess.Popen([sys.executable, client_path])

if __name__ == "__main__":
    print("🚀 Запуск MyMessenger...")
    print("=" * 40)
    
    # Запускаем сервер
    print("📡 Запуск сервера...")
    server = start_server()
    time.sleep(2)  # Ждём пока сервер поднимется
    
    # Запускаем клиент
    print("💻 Запуск клиента...")
    client = start_client()
    
    print("✅ MyMessenger запущен!")
    print("=" * 40)
    print("Для завершения закрой окна или нажми Ctrl+C")
    
    try:
        server.wait()
    except KeyboardInterrupt:
        print("\n🛑 Завершение работы...")
        server.terminate()
        client.terminate()