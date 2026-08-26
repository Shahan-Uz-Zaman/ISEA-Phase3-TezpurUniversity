#!/usr/bin/env python3
"""
Assignment 7: Secure TCP Chat GUI Client
Extended from Assignment 6.

The client collects username/password through the GUI and sends them over
the existing TCP connection. Passwords are never written to disk or logs.
"""

import socket
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

SERVER_IP = "10.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 4096
MAX_USERNAME_LENGTH = 20
MAX_PASSWORD_LENGTH = 128
MAX_MESSAGE_LENGTH = 1000


class ChatGUI:
    def __init__(self):
        self.client = None
        self.username = ""
        self.connected = False
        self.receive_buffer = ""
        self.login_in_progress = False

        self.root = tk.Tk()
        self.root.title("Secure TCP Chat Client")
        self.root.geometry("420x320")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.disconnect)

        self.login_screen()
        self.root.mainloop()

    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Secure TCP Chat",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        ttk.Label(frame, text=f"Server: {SERVER_IP}:{SERVER_PORT}").pack(pady=3)

        ttk.Label(frame, text="Username").pack(anchor="w", pady=(12, 0))
        self.username_entry = ttk.Entry(frame, width=34)
        self.username_entry.pack(pady=5)

        ttk.Label(frame, text="Password").pack(anchor="w")
        self.password_entry = ttk.Entry(frame, show="*", width=34)
        self.password_entry.pack(pady=5)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=15)

        self.login_button = ttk.Button(
            button_frame,
            text="Login",
            command=self.connect_server
        )
        self.login_button.pack(side="left", padx=5)

        self.signup_button = ttk.Button(
            button_frame,
            text="Sign Up",
            command=self.signup_server
        )
        self.signup_button.pack(side="left", padx=5)

        ttk.Label(
            frame,
            text="New user? Click Sign Up to create an account.",
            foreground="gray"
        ).pack(pady=2)

        self.username_entry.focus_set()
        self.password_entry.bind("<Return>", lambda event: self.connect_server())

    def valid_username(self, username):
        if not (3 <= len(username) <= MAX_USERNAME_LENGTH):
            return False
        return all(ch.isalnum() or ch == "_" for ch in username)

    def valid_password(self, password):
        return 1 <= len(password) <= MAX_PASSWORD_LENGTH

    def signup_server(self):
        """Create a new account on the server, then allow the user to log in."""
        if self.login_in_progress:
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not self.valid_username(username):
            messagebox.showerror(
                "Invalid Username",
                "Username must be 3-20 characters and contain only letters, numbers, or underscore."
            )
            return

        if not self.valid_password(password):
            messagebox.showerror(
                "Invalid Password",
                "Password must contain 1-128 characters."
            )
            return

        self.login_in_progress = True
        self.login_button.config(state="disabled")
        self.signup_button.config(state="disabled")

        signup_socket = None
        old_buffer = self.receive_buffer
        try:
            signup_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            signup_socket.settimeout(10)
            signup_socket.connect((SERVER_IP, SERVER_PORT))

            buffer = ""

            def recv_signup_line():
                nonlocal buffer
                while "\n" not in buffer:
                    data = signup_socket.recv(BUFFER_SIZE)
                    if not data:
                        raise ConnectionError("Server closed the connection.")
                    buffer += data.decode("utf-8", errors="replace")
                line, buffer = buffer.split("\n", 1)
                return line.rstrip("\r")

            first = recv_signup_line()
            if first != "AUTH_REQUIRED":
                raise ConnectionError("Unexpected response from server.")
            recv_signup_line()

            signup_socket.sendall(
                f"SIGNUP {username} {password}\n".encode("utf-8")
            )
            response = recv_signup_line()

            if response.startswith("SIGNUP_OK "):
                messagebox.showinfo(
                    "Sign Up Successful",
                    response[10:].strip() + "\n\nYou can now log in with these credentials."
                )
                self.password_entry.delete(0, tk.END)
                self.username_entry.focus_set()
            elif response.startswith("SIGNUP_FAIL "):
                messagebox.showerror("Sign Up Failed", response[11:].strip())
            else:
                messagebox.showerror("Sign Up Error", "Unexpected server response.")

        except socket.timeout:
            messagebox.showerror("Connection Error", "Server did not respond in time.")
        except Exception as exc:
            messagebox.showerror("Sign Up Error", str(exc))
        finally:
            self.receive_buffer = old_buffer
            if signup_socket:
                try:
                    signup_socket.close()
                except OSError:
                    pass
            self.login_in_progress = False
            if self.root.winfo_exists():
                self.login_button.config(state="normal")
                self.signup_button.config(state="normal")

    def connect_server(self):
        if self.login_in_progress:
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not self.valid_username(username):
            messagebox.showerror(
                "Invalid Username",
                "Username must be 3-20 characters and contain only letters, numbers, or underscore."
            )
            return

        if not self.valid_password(password):
            messagebox.showerror(
                "Invalid Password",
                "Password must contain 1-128 characters."
            )
            return

        self.login_in_progress = True
        self.login_button.config(state="disabled")
        self.signup_button.config(state="disabled")

        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(10)
            self.client.connect((SERVER_IP, SERVER_PORT))

            # Read the authentication banner.
            welcome = self.recv_line_blocking()
            if welcome != "AUTH_REQUIRED":
                raise ConnectionError("Unexpected response from server.")

            instruction = self.recv_line_blocking()
            if not instruction.startswith("AUTH format"):
                raise ConnectionError("Invalid authentication protocol.")

            # Password is sent only to the server over the Assignment 7 TCP channel.
            self.send_line(f"LOGIN {username} {password}")

            response = self.recv_line_blocking()

            if response.startswith("AUTH_OK "):
                self.username = username
                self.connected = True
                self.client.settimeout(None)

                self.show_chat_window()

                receive_thread = threading.Thread(
                    target=self.receive_messages,
                    daemon=True
                )
                receive_thread.start()

            elif response.startswith("AUTH_FAIL "):
                messagebox.showerror(
                    "Login Failed",
                    response[10:].strip()
                )
                self.close_socket()
            else:
                messagebox.showerror(
                    "Authentication Error",
                    "Unexpected server response."
                )
                self.close_socket()

        except socket.timeout:
            messagebox.showerror(
                "Connection Error",
                "Server did not respond in time."
            )
            self.close_socket()
        except Exception as exc:
            messagebox.showerror("Connection Error", str(exc))
            self.close_socket()
        finally:
            self.login_in_progress = False
            if self.root.winfo_exists():
                self.login_button.config(state="normal")
                self.signup_button.config(state="normal")

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

    def send_line(self, message):
        if self.client:
            self.client.sendall((message + "\n").encode("utf-8"))

    def close_socket(self):
        if self.client:
            try:
                self.client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.client.close()
            except OSError:
                pass
        self.client = None
        self.connected = False

    def disconnect(self):
        if self.client:
            try:
                self.send_line("/quit")
            except OSError:
                pass
        self.close_socket()

        if hasattr(self, "status"):
            self.status.config(text="Disconnected", foreground="red")

        if hasattr(self, "send_button"):
            self.send_button.config(state="disabled")
        if hasattr(self, "disconnect_button"):
            self.disconnect_button.config(state="disabled")
        if hasattr(self, "message_entry"):
            self.message_entry.config(state="disabled")

        if self.root.winfo_exists():
            self.root.destroy()

    def append_chat(self, message):
        if not hasattr(self, "chat_box"):
            return

        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, message + "\n")
        self.chat_box.config(state="disabled")
        self.chat_box.yview(tk.END)

    def receive_messages(self):
        while self.connected and self.client:
            try:
                data = self.client.recv(BUFFER_SIZE)
                if not data:
                    break

                self.receive_buffer += data.decode("utf-8", errors="replace")

                while "\n" in self.receive_buffer:
                    message, self.receive_buffer = self.receive_buffer.split("\n", 1)
                    message = message.rstrip("\r")

                    if not message:
                        continue

                    if "joined the chat" in message or "left the chat" in message:
                        self.root.after(0, self.refresh_users)

                    if message.startswith("[SERVER] Online users:"):
                        users = message.replace(
                            "[SERVER] Online users:", "", 1
                        ).strip()
                        names = [
                            u.strip()
                            for u in users.split(",")
                            if u.strip() and u.strip().lower() != "none"
                        ]
                        self.root.after(0, self.update_user_list, names)
                        continue

                    self.root.after(0, self.append_chat, message)

                    if "Session expired due to inactivity" in message:
                        self.connected = False

            except (OSError, ConnectionError):
                break

        self.connected = False
        self.root.after(
            0,
            lambda: self.status.config(
                text="Disconnected",
                foreground="red"
            ) if hasattr(self, "status") else None
        )

    def send_message(self):
        if not self.connected or not self.client:
            return

        message = self.message_entry.get().strip()

        if not message:
            return

        if len(message) > MAX_MESSAGE_LENGTH:
            messagebox.showerror(
                "Message Too Long",
                f"Maximum message length is {MAX_MESSAGE_LENGTH} characters."
            )
            return

        target = self.private_user.get().strip()

        if target:
            if not self.valid_username(target):
                messagebox.showerror(
                    "Invalid User",
                    "Private-message target username is invalid."
                )
                return
            message = f"/msg {target} {message}"

        try:
            self.send_line(message)
            self.message_entry.delete(0, tk.END)
        except OSError as exc:
            messagebox.showerror("Send Error", str(exc))
            self.connected = False

    def refresh_users(self):
        if not self.connected or not self.client:
            return
        try:
            self.send_line("/list")
        except OSError:
            pass

    def update_user_list(self, users):
        if not hasattr(self, "user_list"):
            return

        self.user_list.delete(0, tk.END)
        for user in users:
            self.user_list.insert(tk.END, user)

    def select_private_user(self, event):
        selection = self.user_list.curselection()
        if not selection:
            return

        user = self.user_list.get(selection[0])

        self.private_user.delete(0, tk.END)
        self.private_user.insert(0, user)

    def show_chat_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("900x600")
        self.root.title(f"Secure TCP Chat - {self.username}")

        top = ttk.Frame(self.root)
        top.pack(fill="x")

        self.status = ttk.Label(
            top,
            text=f"Connected to {SERVER_IP}:{SERVER_PORT}",
            foreground="green"
        )
        self.status.pack(side="right", padx=10, pady=10)

        ttk.Label(
            top,
            text=f"Logged in as: {self.username}",
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=10)

        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, width=180)
        left.pack(side="left", fill="y", padx=5, pady=5)

        ttk.Label(left, text="Online Users").pack()

        self.user_list = tk.Listbox(left, height=25)
        self.user_list.pack(fill="both", expand=True)

        right = ttk.Frame(body)
        right.pack(side="right", fill="both", expand=True)

        self.chat_box = scrolledtext.ScrolledText(
            right,
            wrap=tk.WORD,
            state="disabled",
            font=("Consolas", 10)
        )
        self.chat_box.pack(fill="both", expand=True, padx=5, pady=5)

        self.append_chat("Authenticated successfully.")
        self.append_chat("Passwords are not stored by the client.")

        pm_frame = ttk.Frame(right)
        pm_frame.pack(fill="x", padx=5)

        ttk.Label(pm_frame, text="Private To:").pack(side="left")

        self.private_user = ttk.Entry(pm_frame, width=20)
        self.private_user.pack(side="left", padx=5)

        bottom = ttk.Frame(right)
        bottom.pack(fill="x")

        self.message_entry = ttk.Entry(bottom, width=70)
        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
            pady=5
        )

        self.send_button = ttk.Button(
            bottom,
            text="Send",
            command=self.send_message
        )
        self.send_button.pack(side="left", padx=5)

        self.disconnect_button = ttk.Button(
            bottom,
            text="Logout",
            command=self.disconnect
        )
        self.disconnect_button.pack(side="left", padx=5)

        self.message_entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        self.user_list.bind(
            "<Double-Button-1>",
            self.select_private_user
        )

        self.refresh_users()


if __name__ == "__main__":
    ChatGUI()
