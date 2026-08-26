#!/usr/bin/env python3
"""
Assignment 8 client: extends Assignment 7 GUI without changing the TCP protocol.

Reliability additions:
- configurable connection timeout
- automatic reconnection after unexpected disconnect
- bounded reconnect attempts
- clean socket/resource handling
"""

import json
import socket
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"

DEFAULTS = {
    "server": {"host": "10.0.0.1", "port": 5000},
    "client": {
        "connect_timeout": 10,
        "reconnect_attempts": 5,
        "reconnect_delay": 2,
        "buffer_size": 4096,
        "max_username_length": 20,
        "max_password_length": 128,
        "max_message_length": 1000
    }
}


def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(DEFAULTS, indent=2), encoding="utf-8")
        return DEFAULTS
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        for section, values in DEFAULTS.items():
            data.setdefault(section, {})
            for k, v in values.items():
                data[section].setdefault(k, v)
        return data
    except (OSError, json.JSONDecodeError):
        return DEFAULTS


CONFIG = load_config()
SERVER_IP = CONFIG["server"]["host"]
SERVER_PORT = int(CONFIG["server"]["port"])
BUFFER_SIZE = int(CONFIG["client"]["buffer_size"])
CONNECT_TIMEOUT = float(CONFIG["client"]["connect_timeout"])
RECONNECT_ATTEMPTS = int(CONFIG["client"]["reconnect_attempts"])
RECONNECT_DELAY = float(CONFIG["client"]["reconnect_delay"])
MAX_USERNAME_LENGTH = int(CONFIG["client"]["max_username_length"])
MAX_PASSWORD_LENGTH = int(CONFIG["client"]["max_password_length"])
MAX_MESSAGE_LENGTH = int(CONFIG["client"]["max_message_length"])


class ChatGUI:
    def __init__(self):
        self.client = None
        self.username = ""
        self.password = ""
        self.connected = False
        self.receive_buffer = ""
        self.login_in_progress = False
        self.intentional_disconnect = False
        self.reconnect_lock = threading.Lock()
        self.reconnecting = False

        self.root = tk.Tk()
        self.root.title("Secure TCP Chat - Assignment 8")
        self.root.geometry("430x350")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)
        self.login_screen()
        self.root.mainloop()

    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Secure TCP Chat", font=("Arial", 18, "bold")).pack(pady=10)
        ttk.Label(frame, text=f"Server: {SERVER_IP}:{SERVER_PORT}").pack(pady=3)
        ttk.Label(frame, text="Username").pack(anchor="w", pady=(12, 0))
        self.username_entry = ttk.Entry(frame, width=34)
        self.username_entry.pack(pady=5)
        ttk.Label(frame, text="Password").pack(anchor="w")
        self.password_entry = ttk.Entry(frame, show="*", width=34)
        self.password_entry.pack(pady=5)

        buttons = ttk.Frame(frame)
        buttons.pack(pady=15)
        self.login_button = ttk.Button(buttons, text="Login", command=self.connect_server)
        self.login_button.pack(side="left", padx=5)
        self.signup_button = ttk.Button(buttons, text="Sign Up", command=self.signup_server)
        self.signup_button.pack(side="left", padx=5)

        ttk.Label(frame, text="Assignment 8: reliable & scalable TCP client").pack(pady=5)
        self.username_entry.focus_set()
        self.password_entry.bind("<Return>", lambda event: self.connect_server())

    def valid_username(self, username):
        return (
            3 <= len(username) <= MAX_USERNAME_LENGTH
            and all(ch.isalnum() or ch == "_" for ch in username)
        )

    def valid_password(self, password):
        return 1 <= len(password) <= MAX_PASSWORD_LENGTH

    def recv_line_blocking(self):
        while "\n" not in self.receive_buffer:
            data = self.client.recv(BUFFER_SIZE)
            if not data:
                raise ConnectionError("Server closed the connection.")
            self.receive_buffer += data.decode("utf-8", errors="replace")
            if len(self.receive_buffer) > 8192:
                raise ConnectionError("Invalid server response.")
        line, self.receive_buffer = self.receive_buffer.split("\n", 1)
        return line.rstrip("\r")

    def connect_socket(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(CONNECT_TIMEOUT)
        self.client.connect((SERVER_IP, SERVER_PORT))
        first = self.recv_line_blocking()
        if first != "AUTH_REQUIRED":
            raise ConnectionError("Unexpected server response.")
        self.recv_line_blocking()

    def signup_server(self):
        """Create a new account using a separate temporary TCP connection.

        TCP is a byte stream, so signup reads complete newline-delimited
        protocol messages instead of assuming one recv() == one message.
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not self.valid_username(username):
            messagebox.showerror(
                "Invalid Username",
                f"Username must be 3-{MAX_USERNAME_LENGTH} characters "
                "and contain only letters, numbers, or underscore."
            )
            return

        if not self.valid_password(password):
            messagebox.showerror(
                "Invalid Password",
                f"Password must contain 1-{MAX_PASSWORD_LENGTH} characters."
            )
            return

        signup_sock = None
        signup_buffer = ""

        def recv_line():
            nonlocal signup_buffer
            while "\n" not in signup_buffer:
                chunk = signup_sock.recv(BUFFER_SIZE)
                if not chunk:
                    raise ConnectionError("Server closed the connection.")
                signup_buffer += chunk.decode("utf-8", errors="replace")
                if len(signup_buffer) > 8192:
                    raise ConnectionError("Invalid server response from server.")

            line, signup_buffer = signup_buffer.split("\n", 1)
            return line.rstrip("\r")

        self.signup_button.config(state="disabled")
        self.login_button.config(state="disabled")

        try:
            signup_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            signup_sock.settimeout(CONNECT_TIMEOUT)
            signup_sock.connect((SERVER_IP, SERVER_PORT))

            # Server sends two newline-delimited authentication banner lines.
            first = recv_line()
            if first != "AUTH_REQUIRED":
                raise ConnectionError(
                    f"Unexpected server response: {first}"
                )

            # Consume the protocol/help line before sending SIGNUP.
            recv_line()

            signup_sock.sendall(
                f"SIGNUP {username} {password}\n".encode("utf-8")
            )

            response = recv_line()

            if response.startswith("SIGNUP_OK"):
                parts = response.split(" ", 1)
                detail = parts[1] if len(parts) == 2 else "Account created successfully."
                messagebox.showinfo("Sign Up Successful", detail)

                # Keep username ready for login, but never retain the password.
                self.username_entry.delete(0, tk.END)
                self.username_entry.insert(0, username)
                self.password_entry.delete(0, tk.END)
                self.password_entry.focus_set()

            elif response.startswith("SIGNUP_FAIL"):
                parts = response.split(" ", 1)
                detail = parts[1] if len(parts) == 2 else "Registration failed."
                messagebox.showerror("Sign Up Failed", detail)
            else:
                messagebox.showerror(
                    "Sign Up Error",
                    f"Unexpected server response: {response}"
                )

        except socket.timeout:
            messagebox.showerror(
                "Sign Up Error",
                "The server did not respond in time."
            )
        except ConnectionRefusedError:
            messagebox.showerror(
                "Sign Up Error",
                f"Cannot connect to {SERVER_IP}:{SERVER_PORT}. "
                "Make sure the server is running."
            )
        except (ConnectionError, OSError) as exc:
            messagebox.showerror("Sign Up Error", str(exc))
        finally:
            if signup_sock is not None:
                try:
                    signup_sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                try:
                    signup_sock.close()
                except OSError:
                    pass

            if self.root.winfo_exists():
                self.signup_button.config(state="normal")
                self.login_button.config(state="normal")

    def connect_server(self):
        if self.login_in_progress:
            return
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        if not self.valid_username(username):
            messagebox.showerror("Invalid Username", "Username must be 3-20 characters and contain only letters, numbers, or underscore.")
            return
        if not self.valid_password(password):
            messagebox.showerror("Invalid Password", "Password must contain 1-128 characters.")
            return

        self.login_in_progress = True
        self.intentional_disconnect = False
        self.login_button.config(state="disabled")
        self.signup_button.config(state="disabled")
        try:
            self.receive_buffer = ""
            self.connect_socket()
            self.client.sendall(f"LOGIN {username} {password}\n".encode("utf-8"))
            response = self.recv_line_blocking()
            if response.startswith("AUTH_OK "):
                self.username, self.password = username, password
                self.connected = True
                self.client.settimeout(None)
                self.show_chat_window()
                threading.Thread(target=self.receive_messages, daemon=True, name="client-receiver").start()
            elif response.startswith("AUTH_FAIL "):
                messagebox.showerror("Login Failed", response[10:].strip())
                self.close_socket()
            else:
                raise ConnectionError("Unexpected authentication response.")
        except socket.timeout:
            messagebox.showerror("Connection Error", "Server did not respond in time.")
            self.close_socket()
        except Exception as exc:
            messagebox.showerror("Connection Error", str(exc))
            self.close_socket()
        finally:
            self.login_in_progress = False
            # show_chat_window() destroys the login widgets after a successful
            # login, so never configure them after they have been destroyed.
            try:
                if (not self.connected and
                        self.login_button.winfo_exists() and
                        self.signup_button.winfo_exists()):
                    self.login_button.config(state="normal")
                    self.signup_button.config(state="normal")
            except tk.TclError:
                pass

    def close_socket(self):
        sock = self.client
        self.client = None
        self.connected = False
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass

    def disconnect(self):
        self.intentional_disconnect = True
        if self.client:
            try:
                self.client.sendall(b"/quit\n")
            except OSError:
                pass
        self.close_socket()
        if hasattr(self, "status"):
            self.status.config(text="Disconnected", foreground="red")
        if self.root.winfo_exists():
            self.root.destroy()

    def attempt_reconnect(self):
        with self.reconnect_lock:
            if self.reconnecting or self.intentional_disconnect or not self.username:
                return
            self.reconnecting = True

        def worker():
            try:
                for attempt in range(1, RECONNECT_ATTEMPTS + 1):
                    if self.intentional_disconnect:
                        return
                    self.root.after(0, lambda a=attempt: self.status.config(
                        text=f"Reconnecting... attempt {a}/{RECONNECT_ATTEMPTS}",
                        foreground="orange"
                    ))
                    try:
                        self.receive_buffer = ""
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(CONNECT_TIMEOUT)
                        sock.connect((SERVER_IP, SERVER_PORT))

                        banner = ""
                        while banner.count("\n") < 2:
                            chunk = sock.recv(BUFFER_SIZE).decode("utf-8", errors="replace")
                            if not chunk:
                                raise ConnectionError("Server closed connection.")
                            banner += chunk

                        sock.sendall(f"LOGIN {self.username} {self.password}\n".encode("utf-8"))
                        response = ""
                        while "\n" not in response:
                            chunk = sock.recv(BUFFER_SIZE).decode("utf-8", errors="replace")
                            if not chunk:
                                raise ConnectionError("Server closed connection.")
                            response += chunk

                        first = response.split("\n", 1)[0].rstrip("\r")
                        if first.startswith("AUTH_OK "):
                            self.client = sock
                            self.client.settimeout(None)
                            self.connected = True
                            self.root.after(0, lambda: self.status.config(text=f"Reconnected to {SERVER_IP}:{SERVER_PORT}", foreground="green"))
                            threading.Thread(target=self.receive_messages, daemon=True, name="client-receiver").start()
                            return
                        sock.close()
                    except Exception:
                        try:
                            sock.close()
                        except Exception:
                            pass
                    time.sleep(RECONNECT_DELAY)
                self.root.after(0, lambda: messagebox.showwarning("Reconnection Failed", "Unable to reconnect automatically. Please log in again."))
            finally:
                with self.reconnect_lock:
                    self.reconnecting = False

        threading.Thread(target=worker, daemon=True, name="reconnect-worker").start()

    def receive_messages(self):
        sock = self.client
        try:
            while self.connected and sock is self.client:
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    raise ConnectionError("Server disconnected.")
                self.receive_buffer += data.decode("utf-8", errors="replace")
                while "\n" in self.receive_buffer:
                    message, self.receive_buffer = self.receive_buffer.split("\n", 1)
                    message = message.rstrip("\r")
                    if not message:
                        continue
                    if "Session expired due to inactivity" in message:
                        self.connected = False
                        self.root.after(0, self.append_chat, message)
                        self.intentional_disconnect = True
                        self.close_socket()
                        return
                    if "joined the chat" in message or "left the chat" in message:
                        self.root.after(0, self.refresh_users)
                    if message.startswith("[SERVER] Online users:"):
                        users = message.replace("[SERVER] Online users:", "", 1).strip()
                        names = [u.strip() for u in users.split(",") if u.strip() and u.strip().lower() != "none"]
                        self.root.after(0, self.update_user_list, names)
                        continue
                    self.root.after(0, self.append_chat, message)
        except (OSError, ConnectionError):
            if self.connected and not self.intentional_disconnect:
                self.connected = False
                self.root.after(0, self.append_chat, "[SERVER] Connection lost. Starting automatic reconnection...")
                self.attempt_reconnect()
        finally:
            if self.intentional_disconnect:
                self.connected = False

    def send_line(self, message):
        sock = self.client
        if not sock:
            raise ConnectionError("Not connected.")
        sock.sendall((message + "\n").encode("utf-8"))

    def send_message(self):
        if not self.connected:
            return
        message = self.message_entry.get().strip()
        if not message:
            return
        if len(message) > MAX_MESSAGE_LENGTH:
            messagebox.showerror("Message Too Long", f"Maximum message length is {MAX_MESSAGE_LENGTH} characters.")
            return
        target = self.private_user.get().strip()
        if target:
            if not self.valid_username(target):
                messagebox.showerror("Invalid User", "Private-message target username is invalid.")
                return
            message = f"/msg {target} {message}"
        try:
            self.send_line(message)
            self.message_entry.delete(0, tk.END)
        except (OSError, ConnectionError) as exc:
            messagebox.showerror("Send Error", str(exc))
            if not self.intentional_disconnect:
                self.connected = False
                self.attempt_reconnect()

    def refresh_users(self):
        if not self.connected:
            return
        try:
            self.send_line("/list")
        except (OSError, ConnectionError):
            self.connected = False
            self.attempt_reconnect()

    def update_user_list(self, users):
        try:
            user_list = getattr(self, "user_list", None)
            if user_list is None or not user_list.winfo_exists():
                return

            user_list.delete(0, tk.END)
            for user in users:
                user_list.insert(tk.END, user)
        except tk.TclError:
            pass

    def select_private_user(self, event):
        try:
            user_list = getattr(self, "user_list", None)
            private_user = getattr(self, "private_user", None)

            if user_list is None or private_user is None:
                return
            if not user_list.winfo_exists() or not private_user.winfo_exists():
                return

            selection = user_list.curselection()
            if selection:
                user = user_list.get(selection[0])
                private_user.delete(0, tk.END)
                private_user.insert(0, user)
        except tk.TclError:
            pass

    def append_chat(self, message):
        """Safely append a message to the chat window."""
        try:
            if not self.root.winfo_exists():
                return

            chat_box = getattr(self, "chat_box", None)
            if chat_box is None:
                return

            if not chat_box.winfo_exists():
                return

            chat_box.config(state="normal")

            # Keep server/system messages readable.
            chat_box.insert(tk.END, message + "\n")

            chat_box.config(state="disabled")
            chat_box.see(tk.END)

        except tk.TclError:
            # The chat window may have been destroyed during logout/shutdown.
            pass

    def show_chat_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("900x600")
        self.root.title(f"Secure TCP Chat - {self.username}")

        top = ttk.Frame(self.root)
        top.pack(fill="x")
        self.status = ttk.Label(top, text=f"Connected to {SERVER_IP}:{SERVER_PORT}", foreground="green")
        self.status.pack(side="right", padx=10, pady=10)
        ttk.Label(top, text=f"Logged in as: {self.username}", font=("Arial", 11, "bold")).pack(side="left", padx=10)

        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True)
        left = ttk.Frame(body, width=180)
        left.pack(side="left", fill="y", padx=5, pady=5)
        ttk.Label(left, text="Online Users").pack()
        self.user_list = tk.Listbox(left, height=25)
        self.user_list.pack(fill="both", expand=True)

        right = ttk.Frame(body)
        right.pack(side="right", fill="both", expand=True)
        self.chat_box = scrolledtext.ScrolledText(right, wrap=tk.WORD, state="disabled", font=("Consolas", 10))
        self.chat_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.append_chat("Authenticated successfully.")
        self.append_chat("Assignment 8 reliability: automatic reconnect enabled.")

        pm_frame = ttk.Frame(right)
        pm_frame.pack(fill="x", padx=5)
        ttk.Label(pm_frame, text="Private To:").pack(side="left")
        self.private_user = ttk.Entry(pm_frame, width=20)
        self.private_user.pack(side="left", padx=5)

        bottom = ttk.Frame(right)
        bottom.pack(fill="x")
        self.message_entry = ttk.Entry(bottom, width=70)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        self.send_button = ttk.Button(bottom, text="Send", command=self.send_message)
        self.send_button.pack(side="left", padx=5)
        self.disconnect_button = ttk.Button(bottom, text="Logout", command=self.disconnect)
        self.disconnect_button.pack(side="left", padx=5)

        self.message_entry.bind("<Return>", lambda event: self.send_message())
        self.user_list.bind("<Double-Button-1>", self.select_private_user)
        self.refresh_users()


if __name__ == "__main__":
    ChatGUI()