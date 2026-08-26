#!/usr/bin/env python3
"""
Assignment 7: Secure Network Application Development Using TCP
Extended from Assignment 6.

Security features:
- Username/password authentication
- SHA-256 password hashing
- Duplicate-login prevention
- Username/message/command validation
- Temporary lockout after five consecutive failed logins
- Inactivity-based session timeout
- Security logging without passwords
- Existing broadcast/private chat, history and performance statistics
"""

import csv
import hashlib
import os
import re
import socket
import threading
import time
from datetime import datetime

HOST = "0.0.0.0"
PORT = 5000
HISTORY_FILE = "chat_history.csv"
PERF_FILE = "performance_results.csv"
USERS_FILE = "users.csv"
SECURITY_LOG_FILE = "security_log.txt"

BUFFER_SIZE = 4096
MAX_USERNAME_LENGTH = 20
MAX_PASSWORD_LENGTH = 128
MAX_MESSAGE_LENGTH = 1000
SESSION_TIMEOUT = 300          # 5 minutes of user inactivity
LOCKOUT_DURATION = 60          # 60 seconds
MAX_FAILED_ATTEMPTS = 5

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
SUPPORTED_COMMANDS = {"/list", "/stats", "/quit", "/exit", "/msg"}

# Global state protected by lock
clients = {}          # username -> {sock, addr, login_time, online, last_activity}
username_of = {}      # sock -> username
failed_logins = {}    # username -> {"count": int, "locked_until": float}
stats = {
    "messages_processed": 0,
    "broadcast_messages": 0,
    "private_messages": 0,
}
max_clients_seen = 0
server_start_time = None
lock = threading.Lock()


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def ensure_users_file():
    """Create a credential file containing SHA-256 hashes, never plaintext."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password_hash"])
            # Demo accounts for assignment testing. Passwords are not stored here.
            writer.writerow(["student1", hash_password("student123")])
            writer.writerow(["student2", hash_password("student456")])
        print("[*] Created users.csv with demo SHA-256 credentials.")
        print("[*] Demo usernames: student1 / student2")
        print("[*] Demo passwords are intentionally not written to users.csv.")


def load_users():
    """Load username -> password hash from users.csv."""
    users = {}
    ensure_users_file()

    try:
        with open(USERS_FILE, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                username = row.get("username", "").strip()
                password_hash = row.get("password_hash", "").strip()
                if USERNAME_RE.fullmatch(username) and re.fullmatch(r"[0-9a-f]{64}", password_hash):
                    users[username] = password_hash
    except (OSError, csv.Error) as exc:
        print(f"[!] Unable to read {USERS_FILE}: {exc}")

    return users


def register_user(username, password, client_addr):
    """Create a new account using a SHA-256 password hash."""
    addr = f"{client_addr[0]}:{client_addr[1]}"

    if not validate_username(username):
        security_log("SIGNUP_REJECTED", username or "-", addr, "invalid username format")
        return False, "Username must be 3-20 characters and contain only letters, numbers, or underscore."

    if not validate_password(password):
        security_log("SIGNUP_REJECTED", username, addr, "invalid password length")
        return False, "Password must contain 1-128 characters."

    with lock:
        users = load_users()
        if username in users:
            security_log("SIGNUP_REJECTED", username, addr, "username already exists")
            return False, "Username already exists. Please choose another username."

        try:
            with open(USERS_FILE, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([username, hash_password(password)])
        except OSError as exc:
            security_log("SIGNUP_ERROR", username, addr, type(exc).__name__)
            return False, "Unable to create account. Please try again."

    failed_logins.pop(username, None)
    security_log("SIGNUP_SUCCESS", username, addr, "account created")
    return True, "Account created successfully. You can now log in."


def init_csv_files():
    """Create persistent files with headers if they do not exist."""
    ensure_users_file()

    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                ["timestamp", "sender", "receiver", "message_type", "message"]
            )

    if not os.path.exists(PERF_FILE):
        with open(PERF_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                ["clients", "broadcast_messages", "private_messages",
                 "avg_delay_ms", "throughput_msgs_per_sec"]
            )

    if not os.path.exists(SECURITY_LOG_FILE):
        with open(SECURITY_LOG_FILE, "a", encoding="utf-8"):
            pass


def security_log(event, username="-", addr="-", details=""):
    """Write security events only. Passwords are never logged."""
    safe_details = str(details).replace("\n", " ").replace("\r", " ")
    line = f"{now_text()} | {event} | user={username} | addr={addr} | {safe_details}\n"
    try:
        with open(SECURITY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except OSError as exc:
        print(f"[!] Security log error: {exc}")


def log_message(sender, receiver, msg_type, message):
    """Append a chat message to persistent history."""
    timestamp = now_text()
    with lock:
        with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(
                [timestamp, sender, receiver, msg_type, message]
            )


def get_last_n_messages_by_user(username, n=5):
    messages = []
    if not os.path.exists(HISTORY_FILE):
        return messages

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["sender"] == username:
                    messages.append(row)
        return messages[-n:]
    except (OSError, csv.Error, KeyError):
        return []


def validate_username(username):
    return bool(USERNAME_RE.fullmatch(username))


def validate_password(password):
    return 1 <= len(password) <= MAX_PASSWORD_LENGTH


def validate_message(message):
    return bool(message) and len(message) <= MAX_MESSAGE_LENGTH


def validate_command(message):
    if not message.startswith("/"):
        return True

    command = message.split(" ", 1)[0].lower()
    return command in SUPPORTED_COMMANDS


def send_line(sock, message):
    sock.sendall((message + "\n").encode("utf-8"))


def recv_line(sock, buffer):
    """Read one newline-delimited protocol message from a TCP stream."""
    while "\n" not in buffer:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            return None, buffer
        buffer += data.decode("utf-8", errors="replace")

        # Protect the server from an unbounded input stream.
        if len(buffer) > MAX_MESSAGE_LENGTH + 256:
            raise ValueError("Input exceeds maximum allowed size")

    line, buffer = buffer.split("\n", 1)
    return line.rstrip("\r"), buffer


def is_locked(username):
    with lock:
        state = failed_logins.get(username)
        if not state:
            return False, 0

        remaining = state.get("locked_until", 0) - time.time()
        if remaining > 0:
            return True, int(remaining) + 1

        if state.get("locked_until", 0):
            state["locked_until"] = 0
            state["count"] = 0

        return False, 0


def authenticate(username, password, client_addr):
    """
    Authenticate against SHA-256 hashes.
    Returns (success, reason).
    """
    addr = f"{client_addr[0]}:{client_addr[1]}"
    users = load_users()

    if not validate_username(username):
        security_log("INVALID_LOGIN_INPUT", username or "-", addr, "invalid username format")
        return False, "Invalid username format."

    if not validate_password(password):
        security_log("INVALID_LOGIN_INPUT", username, addr, "invalid password length")
        return False, "Invalid password."

    locked, remaining = is_locked(username)
    if locked:
        security_log("LOGIN_BLOCKED", username, addr, f"temporary lockout; retry in {remaining}s")
        return False, f"Account temporarily locked. Try again in {remaining} seconds."

    stored_hash = users.get(username)
    supplied_hash = hash_password(password)

    # Do not reveal whether the username exists.
    valid = stored_hash is not None and supplied_hash == stored_hash

    if not valid:
        with lock:
            state = failed_logins.setdefault(
                username, {"count": 0, "locked_until": 0}
            )
            state["count"] += 1
            count = state["count"]

            if count >= MAX_FAILED_ATTEMPTS:
                state["locked_until"] = time.time() + LOCKOUT_DURATION

        security_log(
            "LOGIN_FAILED",
            username,
            addr,
            f"consecutive_failed_attempts={count}"
        )

        if count >= MAX_FAILED_ATTEMPTS:
            security_log(
                "ACCOUNT_LOCKED",
                username,
                addr,
                f"duration={LOCKOUT_DURATION}s"
            )
            return False, (
                f"Too many failed attempts. Login blocked for "
                f"{LOCKOUT_DURATION} seconds."
            )

        return False, "Invalid username or password."

    with lock:
        failed_logins.pop(username, None)
        if username in clients and clients[username]["online"]:
            security_log("DUPLICATE_LOGIN", username, addr, "already logged in")
            return False, "This username is already logged in."

    security_log("LOGIN_SUCCESS", username, addr, "authentication successful")
    return True, "Authentication successful."


def broadcast(message, exclude_sock=None):
    with lock:
        dead = []
        for uname, info in list(clients.items()):
            if not info["online"]:
                continue
            sock = info["sock"]
            if sock is exclude_sock:
                continue
            try:
                send_line(sock, message)
            except OSError:
                dead.append(uname)

        for uname in dead:
            _mark_offline(uname)


def send_to_user(username, message):
    with lock:
        info = clients.get(username)
        if info is None or not info["online"]:
            return False
        try:
            send_line(info["sock"], message)
            return True
        except OSError:
            _mark_offline(username)
            return False


def _mark_offline(username):
    """Caller must already hold the global lock."""
    if username in clients:
        clients[username]["online"] = False
        sock = clients[username].get("sock")
        if sock in username_of:
            del username_of[sock]


def get_online_users():
    with lock:
        return [u for u, info in clients.items() if info["online"]]


def get_server_stats():
    with lock:
        online = sum(1 for info in clients.values() if info["online"])
        return (
            f"[SERVER STATS] Connected users: {online} | "
            f"Messages processed: {stats['messages_processed']} | "
            f"Broadcasts: {stats['broadcast_messages']} | "
            f"Private: {stats['private_messages']}"
        )


def save_performance_results():
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
    elapsed = max(elapsed, 1.0)
    throughput = round(total_msgs / elapsed, 2)
    avg_delay_ms = round((elapsed * 1000) / total_msgs, 2)

    with open(PERF_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            clients_count, broadcast_msgs, private_msgs,
            avg_delay_ms, throughput
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
    broadcast("[SERVER] Online users: " + (", ".join(users) if users else "none"))


def register_authenticated_client(client_sock, client_addr, username):
    global max_clients_seen

    login_time = now_text()
    with lock:
        # Check again while holding the lock to avoid a race between two logins.
        if username in clients and clients[username]["online"]:
            return False

        clients[username] = {
            "sock": client_sock,
            "addr": client_addr,
            "login_time": login_time,
            "last_activity": time.time(),
            "online": True,
        }
        username_of[client_sock] = username

        online_now = sum(1 for info in clients.values() if info["online"])
        max_clients_seen = max(max_clients_seen, online_now)

    return True


def handle_client(client_sock, client_addr):
    username = None
    buffer = ""

    try:
        client_sock.settimeout(5.0)
        addr = f"{client_addr[0]}:{client_addr[1]}"

        # ---------------- Authentication ----------------
        send_line(client_sock, "AUTH_REQUIRED")
        send_line(client_sock, "AUTH format: LOGIN <username> <password> | SIGNUP <username> <password>")

        while True:
            try:
                line, buffer = recv_line(client_sock, buffer)
            except socket.timeout:
                continue

            if line is None:
                return

            if not line:
                send_line(client_sock, "AUTH_FAIL Empty login request.")
                continue

            parts = line.split(" ", 2)
            if len(parts) != 3 or parts[0].upper() not in ("LOGIN", "SIGNUP"):
                send_line(client_sock, "AUTH_FAIL Unsupported authentication command.")
                security_log("AUTH_PROTOCOL_ERROR", "-", addr, "unsupported authentication command")
                continue

            action = parts[0].upper()
            username = parts[1].strip()
            password = parts[2]

            if action == "SIGNUP":
                success, reason = register_user(username, password, client_addr)
                if success:
                    send_line(client_sock, f"SIGNUP_OK {reason}")
                else:
                    send_line(client_sock, f"SIGNUP_FAIL {reason}")
                continue

            success, reason = authenticate(username, password, client_addr)
            if not success:
                send_line(client_sock, f"AUTH_FAIL {reason}")
                continue

            if not register_authenticated_client(client_sock, client_addr, username):
                send_line(client_sock, "AUTH_FAIL This username is already logged in.")
                security_log("DUPLICATE_LOGIN", username, addr, "race-condition check")
                return

            send_line(client_sock, f"AUTH_OK Welcome {username}!")
            break

        # ---------------- Existing Assignment 6 functionality ----------------
        join_msg = f"[SERVER] {username} has joined the chat."
        broadcast(join_msg, exclude_sock=client_sock)
        notify_user_list()
        print(f"[+] {username} connected from {addr} at {now_text()}")

        send_line(client_sock, f"[SERVER] Welcome {username}! You are now online.")
        send_line(client_sock, "[SERVER] Commands: /list  /msg <user> <text>  /stats  /quit")

        history = get_last_n_messages_by_user(username, 5)
        if history:
            send_line(client_sock, "[SERVER] --- Your last 5 messages ---")
            for row in history:
                send_line(
                    client_sock,
                    f"  [{row['timestamp']}] {row['sender']} -> "
                    f"{row['receiver']} ({row['message_type']}): {row['message']}"
                )
            send_line(client_sock, "[SERVER] --- End of history ---")
        else:
            send_line(client_sock, "[SERVER] No previous messages found for you.")

        while True:
            try:
                line, buffer = recv_line(client_sock, buffer)
            except socket.timeout:
                with lock:
                    info = clients.get(username)
                    last_activity = info["last_activity"] if info else time.time()

                if time.time() - last_activity >= SESSION_TIMEOUT:
                    send_line(client_sock, "[SERVER] Session expired due to inactivity.")
                    security_log(
                        "SESSION_TIMEOUT", username, addr,
                        f"timeout={SESSION_TIMEOUT}s"
                    )
                    break
                continue

            if line is None:
                break

            message = line.strip()
            if not message:
                security_log("INVALID_INPUT", username, addr, "empty message")
                continue

            if len(message) > MAX_MESSAGE_LENGTH:
                send_line(
                    client_sock,
                    f"[SERVER] Message rejected: maximum length is {MAX_MESSAGE_LENGTH} characters."
                )
                security_log(
                    "INPUT_REJECTED", username, addr,
                    f"message too large ({len(message)} chars)"
                )
                continue

            if not validate_command(message):
                send_line(client_sock, "[SERVER] Unsupported command.")
                security_log(
                    "COMMAND_REJECTED", username, addr,
                    message.split(" ", 1)[0][:30]
                )
                continue

            with lock:
                if username in clients and clients[username]["online"]:
                    clients[username]["last_activity"] = time.time()
                stats["messages_processed"] += 1

            lowered = message.lower()

            if lowered in ("/quit", "/exit"):
                send_line(client_sock, "[SERVER] Goodbye!")
                security_log("LOGOUT", username, addr, "client requested logout")
                break

            if lowered == "/list":
                online = get_online_users()
                reply = "[SERVER] Online users: " + (
                    ", ".join(online) if online else "none"
                )
                send_line(client_sock, reply)
                continue

            if lowered == "/stats":
                send_line(client_sock, get_server_stats())
                continue

            if message.startswith("/msg "):
                parts = message.split(" ", 2)
                if len(parts) < 3 or not parts[1] or not parts[2].strip():
                    send_line(client_sock, "[SERVER] Usage: /msg <username> <message>")
                    security_log("COMMAND_REJECTED", username, addr, "invalid /msg syntax")
                    continue

                target = parts[1].strip()
                private_text = parts[2].strip()

                if not validate_username(target):
                    send_line(client_sock, "[SERVER] Invalid target username.")
                    security_log("INPUT_REJECTED", username, addr, "invalid private-message target")
                    continue

                if not validate_message(private_text):
                    send_line(client_sock, "[SERVER] Private message is empty or too long.")
                    security_log("INPUT_REJECTED", username, addr, "invalid private message")
                    continue

                if target == username:
                    send_line(
                        client_sock,
                        "[SERVER] You cannot send a private message to yourself."
                    )
                    continue

                formatted = f"[PRIVATE from {username}]: {private_text}"
                success = send_to_user(target, formatted)

                if success:
                    with lock:
                        stats["private_messages"] += 1
                    send_line(client_sock, f"[SERVER] Private message sent to {target}.")
                    log_message(username, target, "private", private_text)
                    print(f"[PM] {username} -> {target}: {private_text}")
                else:
                    send_line(
                        client_sock,
                        f"[SERVER] Error: User '{target}' does not exist or is offline."
                    )
                continue

            # Normal broadcast
            formatted = f"[{username}]: {message}"
            broadcast(formatted)
            with lock:
                stats["broadcast_messages"] += 1
            log_message(username, "ALL", "broadcast", message)
            print(f"[BC] {username}: {message}")

    except ConnectionResetError:
        security_log("CONNECTION_RESET", username or "-", f"{client_addr[0]}:{client_addr[1]}")
    except ValueError as exc:
        security_log("INPUT_REJECTED", username or "-", f"{client_addr[0]}:{client_addr[1]}", str(exc))
        try:
            send_line(client_sock, "[SERVER] Connection closed: invalid/oversized input.")
        except OSError:
            pass
    except Exception as exc:
        print(f"[!] Error handling client {client_addr}: {exc}")
        security_log("SERVER_ERROR", username or "-", f"{client_addr[0]}:{client_addr[1]}", type(exc).__name__)
    finally:
        if username:
            with lock:
                if username in clients and clients[username].get("sock") == client_sock:
                    clients[username]["online"] = False
                    clients[username]["sock"] = None
                username_of.pop(client_sock, None)

            broadcast(f"[SERVER] {username} has left the chat.")
            notify_user_list()
            print(f"[-] {username} disconnected.")
            print(get_server_stats())

        try:
            client_sock.close()
        except OSError:
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

    print(f"[*] Secure TCP Chat Server listening on {HOST}:{PORT}")
    print("[*] Waiting for clients... (Press Ctrl+C to stop)")
    print("[*] Session timeout:", SESSION_TIMEOUT, "seconds")
    print("[*] Login lockout:", MAX_FAILED_ATTEMPTS, "failed attempts /", LOCKOUT_DURATION, "seconds")

    try:
        while True:
            client_sock, client_addr = server.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\n[*] Server shutting down...")
    finally:
        save_performance_results()
        server.close()
        print("[*] Server closed.")


if __name__ == "__main__":
    main()
