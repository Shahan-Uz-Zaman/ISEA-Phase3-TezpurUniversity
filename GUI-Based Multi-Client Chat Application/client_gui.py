import socket
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
SERVER_IP = "10.0.0.1"
SERVER_PORT = 5000
BUFFER_SIZE = 4096
class ChatGUI:

    def __init__(self):

        self.client = None
        self.username = ""

        self.root = tk.Tk()
        self.root.title("TCP Chat Client")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        self.login_screen()

        self.root.mainloop()

    def login_screen(self):

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(
            frame,
            text="Chat Client",
            font=("Arial",16,"bold")
        )
        title.pack(pady=10)

        ttk.Label(frame,text="Username").pack()

        self.username_entry = ttk.Entry(frame,width=30)
        self.username_entry.pack(pady=5)

        ttk.Label(frame,text="Password (Optional)").pack()

        self.password_entry = ttk.Entry(
            frame,
            show="*",
            width=30
        )
        self.password_entry.pack(pady=5)

        ttk.Button(
            frame,
            text="Connect",
            command=self.connect_server
        ).pack(pady=20)
    def connect_server(self):

        username = self.username_entry.get().strip()

        if username == "":
            messagebox.showerror(
                "Error",
                "Username cannot be empty"
            )
            return

        self.username = username

        try:

            self.client = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM
            )

            self.client.connect(
                (SERVER_IP,SERVER_PORT)
            )

        except Exception as e:

            messagebox.showerror(
                "Connection Error",
                str(e)
            )

            return

        welcome = self.client.recv(BUFFER_SIZE).decode()

        print(welcome)

        self.client.sendall(
            (username + "\n").encode()
        )
        self.show_chat_window()
    def disconnect(self):

        try:
            self.client.sendall(b"/quit\n")
        except:
            pass

        try:
            self.client.shutdown(socket.SHUT_RDWR)
        except:
            pass

        try:
            self.client.close()
        except:
            pass

        self.status.config(
            text="Disconnected",
            foreground="red"
        )

        self.send_button.config(state="disabled")
        self.disconnect_button.config(state="disabled")
        self.message_entry.config(state="disabled")
    def append_chat(self, message):

        self.chat_box.config(state="normal")

        if message.startswith("[SERVER]"):

            self.chat_box.insert(
                tk.END,
                message + "\n"
            )

        elif message.startswith("[PRIVATE"):

            self.chat_box.insert(
                tk.END,
                message + "\n"
            )

        else:

            self.chat_box.insert(
                tk.END,
                message + "\n"
            )

        self.chat_box.config(state="disabled")
        self.chat_box.yview(tk.END)

    def receive_messages(self):

        while True:

            try:

                data = self.client.recv(BUFFER_SIZE)

                if not data:
                    break

                message = data.decode().strip()
                if "joined the chat" in message:
                    self.root.after(
                        0,
                        lambda: self.refresh_users()
                    )

                if "left the chat" in message:
                    self.root.after(
                        0,
                        lambda: self.refresh_users()
                    )
                if message.startswith("[SERVER] Online users:"):

                    users = message.replace(
                        "[SERVER] Online users:",
                        ""
                    ).strip()

                    names = [
                        u.strip()
                        for u in users.split(",")
                        if u.strip()
                    ]

                    self.root.after(
                        0,
                        self.update_user_list,
                        names
                    )

                    continue
                self.root.after(
                    0,
                    self.append_chat,
                    message
                )

            except:

                break

        self.root.after(
            0,
            lambda: self.status.config(
                text="Disconnected",
                foreground="red"
            )
        )

    def send_message(self):

        message = self.message_entry.get().strip()

        if message == "":
            return

        target = self.private_user.get().strip()

        if target != "":
            message = f"/msg {target} {message}"

        try:

            self.client.sendall(
                (message + "\n").encode()
            )

            self.message_entry.delete(0, tk.END)

        except Exception as e:

            messagebox.showerror(
                "Send Error",
                str(e)
            )
    def refresh_users(self):

            try:

                self.client.sendall(
                    b"/list\n"
                )

            except:
                pass
    def update_user_list(self, users):

        self.user_list.delete(0, tk.END)

        for user in users:

            self.user_list.insert(
                tk.END,
                user
            )
    def select_private_user(self, event):

        selection = self.user_list.curselection()

        if not selection:
            return

        user = self.user_list.get(selection[0])

        self.private_user.delete(
            0,
            tk.END
        )

        self.private_user.insert(
            0,
            user
        )
    def show_chat_window(self):

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("900x600")

        self.root.title(
            f"TCP Chat - {self.username}"
        )
        top = ttk.Frame(self.root)
        top.pack(fill="x")

        self.status = ttk.Label(
            top,
            text=f"Connected to {SERVER_IP}:{SERVER_PORT}",
            foreground="green"
        )

        self.status.pack(
            side="right",
            padx=10,
            pady=10
        )

        ttk.Label(
            top,
            text=f"Logged in as : {self.username}",
            font=("Arial",11,"bold")
        ).pack(
            side="left",
            padx=10
        )
        body = ttk.Frame(self.root)
        body.pack(fill="both",expand=True)
        left = ttk.Frame(body,width=180)

        left.pack(
            side="left",
            fill="y",
            padx=5,
            pady=5
        )

        ttk.Label(
            left,
            text="Online Users"
        ).pack()

        self.user_list = tk.Listbox(
            left,
            height=25
        )

        self.user_list.pack(
            fill="both",
            expand=True
        )
        right = ttk.Frame(body)

        right.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.chat_box = scrolledtext.ScrolledText(
            right,
            wrap=tk.WORD,
            state="disabled",
            font=("Consolas",10)
        )

        self.chat_box.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )
        self.append_chat("Connected to chat server...")
        bottom = ttk.Frame(right)
        bottom.pack(fill="x")

        pm_frame = ttk.Frame(right)
        pm_frame.pack(fill="x", padx=5)

        ttk.Label(
            pm_frame,
            text="Private To:"
        ).pack(side="left")

        self.private_user = ttk.Entry(
            pm_frame,
            width=20
        )

        self.private_user.pack(
            side="left",
            padx=5
        )

        self.message_entry = ttk.Entry(
            bottom,
            width=70
        )

        self.message_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=5,
            pady=5
        )
        self.send_button = ttk.Button(
            bottom,
            text="Send"
        )

        self.send_button.pack(
            side="left",
            padx=5
        )
        self.disconnect_button = ttk.Button(
            bottom,
            text="Disconnect"
        )

        self.disconnect_button.pack(
            side="left",
            padx=5
        )
        # Start background receiver thread
        receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True
        )
        receive_thread.start()

        # Send button event
        self.send_button.config(command=self.send_message)

        # Press Enter to send
        self.message_entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        # Disconnect button
        self.disconnect_button.config(
            command=self.disconnect
        )
        self.user_list.bind(
            "<Double-Button-1>",
            self.select_private_user
        )
        self.refresh_users()
    
if __name__ == "__main__":
    ChatGUI()