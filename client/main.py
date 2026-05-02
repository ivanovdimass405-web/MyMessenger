import tkinter as tk
from tkinter import scrolledtext
import threading
from styles import DARK_THEME
from client import MessengerClient, ClientThread

class ModernMessenger:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MyMessenger")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)
        
        self.colors = DARK_THEME
        self.current_chat_id = None
        self.client = None
        self.users = {}
        
        self.setup_styles()
        self.create_layout()
        self.start_client()
    
    def setup_styles(self):
        self.root.configure(bg=self.colors['bg'])
        import tkinter.font as tkfont
        self.title_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")
        self.text_font = tkfont.Font(family="Segoe UI", size=10)
        self.time_font = tkfont.Font(family="Segoe UI", size=8)
    
    def start_client(self):
        self.client = MessengerClient()
        self.client.on_message = self.on_new_message
        self.client.on_users = self.update_users_list
        self.client.on_history = self.load_history
        self.client.on_auth_success = self.on_auth
        
        thread = ClientThread(self.client)
        thread.start()
        
        self.show_login_window()
    
    def show_login_window(self):
        login_win = tk.Toplevel(self.root)
        login_win.title("Вход")
        login_win.geometry("400x300")
        login_win.configure(bg=self.colors['bg'])
        login_win.transient(self.root)
        login_win.grab_set()
        
        tk.Label(login_win, text="MyMessenger", font=("Arial", 20), 
                bg=self.colors['bg'], fg=self.colors['text']).pack(pady=20)
        
        tk.Label(login_win, text="Логин:", bg=self.colors['bg'], 
                fg=self.colors['text']).pack()
        username_entry = tk.Entry(login_win, width=30)
        username_entry.pack(pady=5)
        
        tk.Label(login_win, text="Пароль:", bg=self.colors['bg'], 
                fg=self.colors['text']).pack()
        password_entry = tk.Entry(login_win, width=30, show="*")
        password_entry.pack(pady=5)
        
        def do_login():
            self.client.run_async(self.client.login(username_entry.get(), password_entry.get()))
            login_win.destroy()
        
        def do_register():
            self.client.run_async(self.client.register(username_entry.get(), password_entry.get()))
            login_win.destroy()
        
        tk.Button(login_win, text="Войти", command=do_login,
                 bg=self.colors['accent'], fg='white').pack(pady=10)
        tk.Button(login_win, text="Регистрация", command=do_register,
                 bg='gray', fg='white').pack()
    
    def on_auth(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.status_label.config(text=f"🟢 {username}")
        self.client.run_async(self.client.get_users())
    
    def update_users_list(self, users):
        self.users = {u['id']: u for u in users}
        for widget in self.contacts_scrollable.winfo_children():
            widget.destroy()
        
        for user in users:
            self.create_contact_widget(user['username'], "", user['status'] == 'online', user['id'])
    
    def create_contact_widget(self, name, last_message, online=False, user_id=None):
        frame = tk.Frame(self.contacts_scrollable, bg=self.colors['sidebar'], height=70)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame, text="👤", font=("Segoe UI", 20),
                bg=self.colors['sidebar'], fg=self.colors['text']).pack(side=tk.LEFT, padx=5)
        
        name_label = tk.Label(frame, text=name, font=self.title_font,
                              fg=self.colors['text'], bg=self.colors['sidebar'])
        name_label.pack(side=tk.LEFT, padx=5)
        
        status_color = self.colors['online'] if online else self.colors['offline']
        tk.Label(frame, text="●", fg=status_color, bg=self.colors['sidebar']).pack(side=tk.RIGHT, padx=5)
        
        frame.bind("<Button-1>", lambda e: self.open_chat(user_id, name))
    
    def open_chat(self, user_id, username):
        self.current_chat_id = user_id
        self.chat_name.config(text=username)
        for widget in self.messages_container.winfo_children():
            widget.destroy()
        self.client.run_async(self.client.get_history(user_id))
    
    def load_history(self, messages):
        for msg in messages:
            is_my = msg['from_id'] == self.user_id
            self.create_message_bubble(msg['message'], is_my, str(msg['timestamp'])[:5], "")
        self.messages_canvas.yview_moveto(1.0)
    
    def on_new_message(self, data):
        if data['type'] == 'new_message' and self.current_chat_id == data['from_id']:
            self.root.after(0, lambda: self.create_message_bubble(data['message'], False, data['timestamp'], ""))
    
    def create_message_bubble(self, text, is_my, time, status):
        frame = tk.Frame(self.messages_container, bg=self.colors['chat_bg'])
        frame.pack(fill=tk.X, padx=10, pady=5)
        bubble_color = self.colors['my_msg'] if is_my else self.colors['their_msg']
        tk.Label(frame, text=text, font=self.text_font, fg=self.colors['text'], 
                bg=bubble_color, wraplength=400).pack(padx=10, pady=8, anchor='e' if is_my else 'w')
    
    def send_message(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        if message and self.current_chat_id:
            self.client.run_async(self.client.send_message(self.current_chat_id, message))
            self.create_message_bubble(message, True, "", "✓")
            self.message_entry.delete("1.0", tk.END)
            self.messages_canvas.yview_moveto(1.0)
    
    def create_layout(self):
        self.header = tk.Frame(self.root, bg=self.colors['header'], height=60)
        self.header.pack(fill=tk.X)
        tk.Label(self.header, text="📱 MyMessenger", font=self.title_font,
                fg=self.colors['text'], bg=self.colors['header']).pack(side=tk.LEFT, padx=15)
        self.status_label = tk.Label(self.header, text="🟡 Подключение...", font=self.text_font,
                                     fg=self.colors['online'], bg=self.colors['header'])
        self.status_label.pack(side=tk.RIGHT, padx=15)
        
        main = tk.Frame(self.root, bg=self.colors['bg'])
        main.pack(fill=tk.BOTH, expand=True)
        
        self.sidebar = tk.Frame(main, bg=self.colors['sidebar'], width=300)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        self.contacts_frame = tk.Frame(self.sidebar, bg=self.colors['sidebar'])
        self.contacts_frame.pack(fill=tk.BOTH, expand=True)
        
        self.contacts_canvas = tk.Canvas(self.contacts_frame, bg=self.colors['sidebar'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.contacts_frame, orient="vertical", command=self.contacts_canvas.yview)
        self.contacts_scrollable = tk.Frame(self.contacts_canvas, bg=self.colors['sidebar'])
        self.contacts_scrollable.bind("<Configure>", lambda e: self.contacts_canvas.configure(scrollregion=self.contacts_canvas.bbox("all")))
        self.contacts_canvas.create_window((0, 0), window=self.contacts_scrollable, anchor="nw")
        self.contacts_canvas.configure(yscrollcommand=scrollbar.set)
        self.contacts_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.chat_area = tk.Frame(main, bg=self.colors['chat_bg'])
        self.chat_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.chat_header = tk.Frame(self.chat_area, bg=self.colors['header'], height=60)
        self.chat_header.pack(fill=tk.X)
        self.chat_name = tk.Label(self.chat_header, text="Выберите чат", font=self.title_font,
                                  fg=self.colors['text'], bg=self.colors['header'])
        self.chat_name.pack(side=tk.LEFT, padx=15)
        
        self.messages_frame = tk.Frame(self.chat_area, bg=self.colors['chat_bg'])
        self.messages_frame.pack(fill=tk.BOTH, expand=True)
        
        self.messages_canvas = tk.Canvas(self.messages_frame, bg=self.colors['chat_bg'], highlightthickness=0)
        msg_scrollbar = tk.Scrollbar(self.messages_frame, orient="vertical", command=self.messages_canvas.yview)
        self.messages_container = tk.Frame(self.messages_canvas, bg=self.colors['chat_bg'])
        self.messages_container.bind("<Configure>", lambda e: self.messages_canvas.configure(scrollregion=self.messages_canvas.bbox("all")))
        self.messages_canvas.create_window((0, 0), window=self.messages_container, anchor="nw")
        self.messages_canvas.configure(yscrollcommand=msg_scrollbar.set)
        self.messages_canvas.pack(side="left", fill="both", expand=True)
        msg_scrollbar.pack(side="right", fill="y")
        
        self.input_frame = tk.Frame(self.chat_area, bg=self.colors['header'], height=60)
        self.input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.message_entry = tk.Text(self.input_frame, height=2, bg=self.colors['bg'], 
                                     fg=self.colors['text'], font=self.text_font, wrap=tk.WORD)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)
        self.message_entry.bind("<Return>", lambda e: self.send_message())
        
        tk.Button(self.input_frame, text="➤", command=self.send_message,
                 bg=self.colors['accent'], fg='white', font=("Segoe UI", 14)).pack(side=tk.RIGHT, padx=8)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernMessenger()
    app.run()