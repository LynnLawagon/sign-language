import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',
    'database': 'logindeaf'
}
BG_COLOR = "#d3d3d3"
LABEL_WIDTH = 10
ENTRY_WIDTH = 25
LOGIN_BUTTON_WIDTH = 5
REGISTER_BUTTON_WIDTH = 7
SHOW_BUTTON_WIDTH = 5
BUTTONS_HORIZONTAL_PADDING = 5
MAIN_WIDTH = 400
MAIN_HEIGHT = 400
REG_WIDTH = 350
REG_HEIGHT = 280

class WindowManager:
    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        window.geometry(f"{width}x{height}+{x}+{y}")

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Could not connect to database: {err}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.is_connected():
            self.conn.close()

    def check_user_exists(self, username):
        if not self.connect(): 
            return True
        query = "SELECT COUNT(*) FROM users WHERE username = %s"
        self.cursor.execute(query, (username,))
        count = self.cursor.fetchone()[0]
        self.close()
        return count > 0

    def register_user(self, username, password):
        if not self.connect(): 
            return False
        
        now = datetime.now()

        sql = "INSERT INTO users (username, password, created_at) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(sql, (username, password, now))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to register user: {err}")
            self.conn.rollback()
            return False
        finally:
            self.close()

    def authenticate_user(self, username, password):
        if not self.connect(): 
            return False

        query = "SELECT id, password FROM users WHERE username = %s"
        self.cursor.execute(query, (username,))
        result = self.cursor.fetchone()
        
        authenticated = False
        if result and result[1] == password:
            authenticated = True
            
            user_id = result[0]
            update_sql = "UPDATE users SET last_login = %s WHERE id = %s"
            self.cursor.execute(update_sql, (datetime.now(), user_id))
            self.conn.commit()
            
        self.close()
        return authenticated

class Registration:
    def __init__(self, master):
        self.master = master
        self.db_manager = DatabaseManager()
        self.window_manager = WindowManager()
        self.window = tk.Toplevel(master)
        self.window.title("Register")
        self.window.configure(bg=BG_COLOR)
        self.window.resizable(False, False)
        self.window_manager.center_window(self.window, REG_WIDTH, REG_HEIGHT)
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.window, bg=BG_COLOR)
        main_frame.pack(expand=True)
        tk.Label(main_frame, text="NEW USER REGISTRATION", font=("Arial", 14), bg=BG_COLOR).pack(pady=(20, 20))
        
        username_frame = tk.Frame(main_frame, bg=BG_COLOR)
        username_frame.pack(pady=5)
        tk.Label(username_frame, text="Username:", width=LABEL_WIDTH, anchor='e', bg=BG_COLOR).pack(side="left", padx=5)
        self.entry_user = tk.Entry(username_frame, width=ENTRY_WIDTH)
        self.entry_user.pack(side="left", padx=5)
        
        password_frame = tk.Frame(main_frame, bg=BG_COLOR)
        password_frame.pack(pady=5)
        tk.Label(password_frame, text="Password:", width=LABEL_WIDTH, anchor='e', bg=BG_COLOR).pack(side="left", padx=5)
        self.entry_pass = tk.Entry(password_frame, show="*", width=ENTRY_WIDTH)
        self.entry_pass.pack(side="left", padx=5)
        
        tk.Button(main_frame, text="Register", width=REGISTER_BUTTON_WIDTH, command=self.register_user).pack(pady=(20, 10))

    def register_user(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        if not self.entry_user.winfo_exists() or not self.entry_pass.winfo_exists():
            return

        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill all fields", parent=self.window)
            return
        
        if self.db_manager.check_user_exists(username):
            messagebox.showerror("Error", "Username already exists", parent=self.window)
            return

        if self.db_manager.register_user(username, password):
            messagebox.showinfo("Success", "Registration Successful!")
            self.window.destroy()

class LoginApp:
    def __init__(self, master):
        self.master = master
        self.db_manager = DatabaseManager()
        self.window_manager = WindowManager()
        self.master.title("Login")
        self.master.configure(bg=BG_COLOR)
        self.master.resizable(False, False)
        self.window_manager.center_window(self.master, MAIN_WIDTH, MAIN_HEIGHT)
        self.setup_ui()

    def setup_ui(self):
        main_frame = tk.Frame(self.master, bg=BG_COLOR)
        main_frame.pack(expand=True)
        tk.Label(main_frame, text="🎵 WELCOME USER 🎵", font=("Arial", 25), bg=BG_COLOR).pack(pady=(0, 20))
        tk.Label(main_frame, text="LOGIN", font=("Arial", 16), bg=BG_COLOR).pack(pady=(0, 20))

        username_frame = tk.Frame(main_frame, bg=BG_COLOR)
        username_frame.pack(pady=5)
        tk.Label(username_frame, text="Username:", width=LABEL_WIDTH, anchor='w', bg=BG_COLOR).pack(side="left", padx=5)
        self.entry_user = tk.Entry(username_frame, width=ENTRY_WIDTH)
        self.entry_user.pack(side="left", padx=5)

        password_frame = tk.Frame(main_frame, bg=BG_COLOR)
        password_frame.pack(pady=5)
        tk.Label(password_frame, text="Password:", width=LABEL_WIDTH, anchor='w', bg=BG_COLOR).pack(side="left", padx=5)
        self.entry_pass = tk.Entry(password_frame, show="*", width=ENTRY_WIDTH)
        self.entry_pass.pack(side="left", padx=5)

        buttons_frame = tk.Frame(main_frame, bg=BG_COLOR)
        buttons_frame.pack(pady=(20, 10))
        FIXED_LEFT_SHIFT_PADDING = 50
        
        tk.Button(buttons_frame, text="Login", width=LOGIN_BUTTON_WIDTH, command=self.login_user).pack(
            side="left", padx=(FIXED_LEFT_SHIFT_PADDING, BUTTONS_HORIZONTAL_PADDING)
        )
        tk.Button(buttons_frame, text="Register", width=REGISTER_BUTTON_WIDTH, command=self.open_registration).pack(
            side="left", padx=BUTTONS_HORIZONTAL_PADDING
        )
        self.btn_show_pass = tk.Button(buttons_frame, text="Show", width=SHOW_BUTTON_WIDTH, command=self.toggle_password)
        self.btn_show_pass.pack(side="left", padx=BUTTONS_HORIZONTAL_PADDING)

    def toggle_password(self):
        if self.entry_pass.cget('show') == "":
            self.entry_pass.config(show="*")
            self.btn_show_pass.config(text="Show")
        else:
            self.entry_pass.config(show="")
            self.btn_show_pass.config(text="Hide")

    def login_user(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()
        
        if self.db_manager.authenticate_user(username, password):
            messagebox.showinfo("Success", "Login Successful!")
            self.master.destroy()
            try:
                import test
                app = test.HandGestureApp()
                app.run()
            except ImportError:
                messagebox.showwarning("Warning", "Login successful, but detection not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred in test.py: {e}")
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def open_registration(self):
        Registration(self.master)

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()