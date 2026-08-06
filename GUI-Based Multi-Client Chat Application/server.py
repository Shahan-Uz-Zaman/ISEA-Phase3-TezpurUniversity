#!/usr/bin/env python3
"""
Assignment 5: Advanced Multi-Client Chat Server using TCP
server.py - Concurrent multi-client chat server with private messaging,
            client state management, persistent history, and statistics.

When server is closed (Ctrl+C), performance data is automatically
saved to performance_results.csv

Usage:
    python3 server.py
"""

import socket
import threading
import csv
import os
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000
HISTORY_FILE = "chat_history.csv"
PERF_FILE = "performance_results.csv"
BUFFER_SIZE = 4096

# Global state (protected by lock)
clients = {}          # username -> {sock, addr, login_time, online}
username_of = {}      # sock -> username
stats = {
    "messages_processed": 0,
    "broadcast_messages": 0,
    "private_messages": 0,
}
max_clients_seen = 0
server_start_time = None
lock = threading.Lock()


def init_csv_files():
    """Create CSV files with headers if they do not exist."""
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "sender", "receiver", "message_type", "message"])

    if not os.path.exists(PERF_FILE):
        with open(PERF_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "clients",
                "broadcast_messages",
                "private_messages",
                "avg_delay_ms",
                "throughput_msgs_per_sec"
            ])


def log_message(sender, receiver, msg_type, message):
    """Append a message to the persistent chat history CSV."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with lock:
        with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, sender, receiver, msg_type, message])


def get_last_n_messages_by_user(username, n=5):
    """Return the last n messages sent by the given username from history."""
    messages = []
    if not os.path.exists(HISTORY_FILE):
        return messages
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["sender"] == username:
                    messages.append(row)
        return messages[-n:]
    except Exception:
        return []


def broadcast(message, exclude_sock=None):
    """Send a message to all currently online clients (optionally exclude one)."""
    with lock:
        dead = []
        for uname, info in clients.items():
            if not info["online"]:
                continue
            sock = info["sock"]
            if sock is exclude_sock:
                continue
            try:
                sock.sendall((message + "\n").encode("utf-8"))
            except Exception:
                dead.append(uname)
        for uname in dead:
            _mark_offline(uname)


def send_to_user(username, message):
    """Send a private message to a specific online user. Returns True on success."""
    with lock:
        info = clients.get(username)
        if info is None or not info["online"]:
            return False
        try:
            info["sock"].sendall((message + "\n").encode("utf-8"))
            return True
        except Exception:
            _mark_offline(username)
            return False


def _mark_offline(username):
    """Internal helper – caller must already hold the lock."""
    if username in clients:
        clients[username]["online"] = False
        sock = clients[username].get("sock")
        if sock in username_of:
            del username_of[sock]


def get_online_users():
    """Return list of currently online usernames."""
    with lock:
        return [u for u, info in clients.items() if info["online"]]


def get_server_stats():
    """Return a human-readable statistics string."""
    with lock:
        online = sum(1 for info in clients.values() if info["online"])
        return (
            f"[SERVER STATS] Connected users: {online} | "
            f"Messages processed: {stats['messages_processed']} | "
            f"Broadcasts: {stats['broadcast_messages']} | "
            f"Private: {stats['private_messages']}"
        )


def save_performance_results():
    """Automatically save performance data when server is closed."""
    global max_clients_seen, server_start_time

    with lock:
        total_msgs = stats["messages_processed"]
        broadcast_msgs = stats["broadcast_messages"]
        private_msgs = stats["private_messages"]
        clients_count = max_clients_seen

    if total_msgs == 0:
        print("[*] No messages processed – performance_results.csv not updated.")
        return

    elapsed = time.time() - server_start_time if server_start_time else 1.0
    if elapsed <= 0:
        elapsed = 1.0

    throughput = round(total_msgs / elapsed, 2)
    avg_delay_ms = round((elapsed * 1000) / total_msgs, 2)

    with open(PERF_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            clients_count,
            broadcast_msgs,
            private_msgs,
            avg_delay_ms,
            throughput
        ])

    print("\n" + "=" * 55)
    print("[*] Performance results automatically saved!")
    print(f"    File                : {PERF_FILE}")
    print(f"    Clients (max seen)  : {clients_count}")
    print(f"    Broadcast messages  : {broadcast_msgs}")
    print(f"    Private messages    : {private_msgs}")
    print(f"    Avg delay (ms)      : {avg_delay_ms}")
    print(f"    Throughput (msg/s)  : {throughput}")
    print("=" * 55)

def notify_user_list():

    users = get_online_users()

    msg = "[SERVER] Online users: " + ", ".join(users)

    broadcast(msg)
def handle_client(client_sock, client_addr):
    """Thread function that manages a single client connection."""
    global max_clients_seen
    username = None
    try:
        # ---- Login / username registration ----
        client_sock.sendall(b"Welcome to the Advanced Chat Server!\n")
        client_sock.sendall(b"Enter your username: ")

        data = client_sock.recv(BUFFER_SIZE).decode("utf-8").strip()
        if not data:
            client_sock.close()
            return
        username = data

        with lock:
            # If same username is already online, force old connection offline
            if username in clients and clients[username]["online"]:
                old_sock = clients[username]["sock"]
                try:
                    old_sock.sendall(b"[SERVER] You have been disconnected (new login).\n")
                    old_sock.close()
                except Exception:
                    pass
                if old_sock in username_of:
                    del username_of[old_sock]

            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            clients[username] = {
                "sock": client_sock,
                "addr": client_addr,
                "login_time": login_time,
                "online": True,
            }
            username_of[client_sock] = username

            # Track maximum concurrent clients
            online_now = sum(1 for info in clients.values() if info["online"])
            if online_now > max_clients_seen:
                max_clients_seen = online_now

        # Notify others
        join_msg = f"[SERVER] {username} has joined the chat."
        broadcast(join_msg, exclude_sock=client_sock)
        notify_user_list()
        print(f"[+] {username} connected from {client_addr[0]}:{client_addr[1]} at {login_time}")

        # Welcome + last 5 messages
        client_sock.sendall(
            f"[SERVER] Welcome {username}! You are now online.\n".encode("utf-8")
        )
        client_sock.sendall(
            b"[SERVER] Commands: /list  /msg <user> <text>  /stats  /quit\n"
        )

        history = get_last_n_messages_by_user(username, 5)
        if history:
            client_sock.sendall(b"[SERVER] --- Your last 5 messages ---\n")
            for row in history:
                line = (
                    f"  [{row['timestamp']}] "
                    f"{row['sender']} -> {row['receiver']} "
                    f"({row['message_type']}): {row['message']}\n"
                )
                client_sock.sendall(line.encode("utf-8"))
            client_sock.sendall(b"[SERVER] --- End of history ---\n")
        else:
            client_sock.sendall(b"[SERVER] No previous messages found for you.\n")

        # ---- Main receive loop ----
        while True:
            data = client_sock.recv(BUFFER_SIZE)
            if not data:
                break
            message = data.decode("utf-8").strip()
            if not message:
                continue

            with lock:
                stats["messages_processed"] += 1

            # ---- Commands ----
            if message.lower() in ("/quit", "/exit"):
                client_sock.sendall(b"[SERVER] Goodbye!\n")
                break

            if message.lower() == "/list":
                online = get_online_users()
                reply = "[SERVER] Online users: " + (", ".join(online) if online else "none")
                client_sock.sendall((reply + "\n").encode("utf-8"))
                continue

            if message.lower() == "/stats":
                client_sock.sendall((get_server_stats() + "\n").encode("utf-8"))
                continue

            if message.startswith("/msg "):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    client_sock.sendall(b"[SERVER] Usage: /msg <username> <message>\n")
                    continue
                target = parts[1]
                private_text = parts[2]

                if target == username:
                    client_sock.sendall(b"[SERVER] You cannot send a private message to yourself.\n")
                    continue

                formatted = f"[PRIVATE from {username}]: {private_text}"
                success = send_to_user(target, formatted)
                if success:
                    with lock:
                        stats["private_messages"] += 1
                    client_sock.sendall(
                        f"[SERVER] Private message sent to {target}.\n".encode("utf-8")
                    )
                    log_message(username, target, "private", private_text)
                    print(f"[PM] {username} -> {target}: {private_text}")
                else:
                    client_sock.sendall(
                        f"[SERVER] Error: User '{target}' does not exist or is offline.\n".encode("utf-8")
                    )
                continue

            # ---- Normal broadcast message ----
            formatted = f"[{username}]: {message}"
            broadcast(formatted)
            with lock:
                stats["broadcast_messages"] += 1
            log_message(username, "ALL", "broadcast", message)
            print(f"[BC] {username}: {message}")

    except ConnectionResetError:
        pass
    except Exception as e:
        print(f"[!] Error handling client {client_addr}: {e}")
    finally:
        if username:
            with lock:
                if username in clients:
                    clients[username]["online"] = False
                    if clients[username].get("sock") == client_sock:
                        clients[username]["sock"] = None
                if client_sock in username_of:
                    del username_of[client_sock]

            leave_msg = f"[SERVER] {username} has left the chat."
            broadcast(leave_msg)
            notify_user_list()
            print(f"[-] {username} disconnected.")
            print(get_server_stats())

        try:
            client_sock.close()
        except Exception:
            pass


def main():
    global server_start_time, max_clients_seen

    init_csv_files()
    server_start_time = time.time()
    max_clients_seen = 0

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)

    print(f"[*] Chat Server listening on {HOST}:{PORT}")
    print("[*] Waiting for clients... (Press Ctrl+C to stop)")
    print("[*] Performance data will be auto-saved on exit")

    try:
        while True:
            client_sock, client_addr = server.accept()
            t = threading.Thread(
                target=handle_client, args=(client_sock, client_addr), daemon=True
            )
            t.start()
    except KeyboardInterrupt:
        print("\n[*] Server shutting down...")
    finally:
        # Automatically save performance results when server is closed
        save_performance_results()
        server.close()
        print("[*] Server closed.")


if __name__ == "__main__":
    main()