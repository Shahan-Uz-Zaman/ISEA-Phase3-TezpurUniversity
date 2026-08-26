#!/usr/bin/env python3
"""
Assignment 8: Application Optimization, Scalability and Reliability
Extended directly from Assignment 7.

Preserved protocol:
    LOGIN <username> <password>
    SIGNUP <username> <password>
    /list
    /msg <user> <text>
    /stats
    /quit

Assignment 8 improvements:
- JSON configuration instead of hardcoded operational parameters
- bounded ThreadPoolExecutor for scalable client handling
- larger listen backlog
- automatic disconnected-client cleanup
- graceful server shutdown
- socket timeouts and exception handling
- efficient broadcast using socket snapshots (no lock held during network I/O)
- automatic inactivity cleanup
- client capacity protection
- runtime performance/CPU/memory measurements
- thread-safe CSV performance persistence
- secure Assignment 7 authentication/sign-up remains intact
"""

import atexit
import csv
import hashlib
import json
import logging
import os
import re
import signal
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "config.json"


def load_config():
    defaults = {
        "server": {
            "host": "0.0.0.0",
            "port": 5000,
            "backlog": 50,
            "max_workers": 50,
            "socket_timeout": 5,
            "shutdown_timeout": 5
        },
        "security": {
            "users_file": "users.csv",
            "security_log_file": "security_log.txt",
            "session_timeout": 300,
            "lockout_duration": 60,
            "max_failed_attempts": 5
        },
        "application": {
            "history_file": "chat_history.csv",
            "performance_file": "performance_results.csv",
            "buffer_size": 4096,
            "max_username_length": 20,
            "max_password_length": 128,
            "max_message_length": 1000,
            "max_clients": 50
        },
        "reliability": {
            "accept_timeout": 1.0,
            "cleanup_interval": 2.0
        }
    }

    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(json.dumps(defaults, indent=2), encoding="utf-8")
        return defaults

    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
        # Merge one level at a time so missing keys get safe defaults.
        for section, values in defaults.items():
            loaded.setdefault(section, {})
            for key, value in values.items():
                loaded[section].setdefault(key, value)
        return loaded
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[!] Invalid config.json ({exc}); using safe defaults.")
        return defaults


CONFIG = load_config()

HOST = CONFIG["server"]["host"]
PORT = int(CONFIG["server"]["port"])
BACKLOG = int(CONFIG["server"]["backlog"])
MAX_WORKERS = int(CONFIG["server"]["max_workers"])
SOCKET_TIMEOUT = float(CONFIG["server"]["socket_timeout"])
SHUTDOWN_TIMEOUT = float(CONFIG["server"]["shutdown_timeout"])

USERS_FILE = BASE_DIR / CONFIG["security"]["users_file"]
SECURITY_LOG_FILE = BASE_DIR / CONFIG["security"]["security_log_file"]
HISTORY_FILE = BASE_DIR / CONFIG["application"]["history_file"]
PERF_FILE = BASE_DIR / CONFIG["application"]["performance_file"]
PID_FILE = BASE_DIR / "server.pid"

BUFFER_SIZE = int(CONFIG["application"]["buffer_size"])
MAX_USERNAME_LENGTH = int(CONFIG["application"]["max_username_length"])
MAX_PASSWORD_LENGTH = int(CONFIG["application"]["max_password_length"])
MAX_MESSAGE_LENGTH = int(CONFIG["application"]["max_message_length"])
MAX_CLIENTS = int(CONFIG["application"]["max_clients"])

SESSION_TIMEOUT = float(CONFIG["security"]["session_timeout"])
LOCKOUT_DURATION = float(CONFIG["security"]["lockout_duration"])
MAX_FAILED_ATTEMPTS = int(CONFIG["security"]["max_failed_attempts"])

ACCEPT_TIMEOUT = float(CONFIG["reliability"]["accept_timeout"])
CLEANUP_INTERVAL = float(CONFIG["reliability"]["cleanup_interval"])

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")
SUPPORTED_COMMANDS = {"/list", "/stats", "/quit", "/exit", "/msg"}

clients = {}
username_of = {}
failed_logins = {}
stats = {
    "messages_processed": 0,
    "broadcast_messages": 0,
    "private_messages": 0,
    "connections_accepted": 0,
    "connections_rejected": 0,
}
max_clients_seen = 0
server_start_time = None

state_lock = threading.RLock()
shutdown_event = threading.Event()
server_socket = None
executor = None
perf_lock = threading.Lock()


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def security_log(event, username="-", addr="-", details=""):
    # Never log passwords or password-derived values.
    safe = str(details).replace("\n", " ").replace("\r", " ")
    try:
        with SECURITY_LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"{now_text()} | {event} | user={username} | addr={addr} | {safe}\n")
    except OSError as exc:
        print(f"[!] Security log error: {exc}")


def ensure_users_file():
    if not USERS_FILE.exists():
        with USERS_FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password_hash"])
            writer.writerow(["student1", hash_password("student123")])
            writer.writerow(["student2", hash_password("student456")])


def load_users():
    ensure_users_file()
    users = {}
    try:
        with USERS_FILE.open("r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                username = row.get("username", "").strip()
                password_hash = row.get("password_hash", "").strip()
                if validate_username(username) and re.fullmatch(r"[0-9a-f]{64}", password_hash):
                    users[username] = password_hash
    except (OSError, csv.Error) as exc:
        security_log("USER_DB_ERROR", "-", "-", type(exc).__name__)
    return users


def register_user(username, password, client_addr):
    addr = f"{client_addr[0]}:{client_addr[1]}"
    if not validate_username(username):
        security_log("SIGNUP_REJECTED", username or "-", addr, "invalid username")
        return False, "Username must be 3-20 characters and contain only letters, numbers, or underscore."
    if not validate_password(password):
        security_log("SIGNUP_REJECTED", username, addr, "invalid password length")
        return False, "Password must contain 1-128 characters."

    # Serialize credential-file updates to avoid corruption during concurrent sign-ups.
    with state_lock:
        users = load_users()
        if username in users:
            security_log("SIGNUP_REJECTED", username, addr, "username already exists")
            return False, "Username already exists. Please choose another username."
        try:
            with USERS_FILE.open("a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([username, hash_password(password)])
        except OSError as exc:
            security_log("SIGNUP_ERROR", username, addr, type(exc).__name__)
            return False, "Unable to create account. Please try again."

    with state_lock:
        failed_logins.pop(username, None)
    security_log("SIGNUP_SUCCESS", username, addr, "account created")
    return True, "Account created successfully. You can now log in."


def init_files():
    ensure_users_file()
    if not HISTORY_FILE.exists():
        with HISTORY_FILE.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["timestamp", "sender", "receiver", "message_type", "message"])
    if not PERF_FILE.exists():
        with PERF_FILE.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "timestamp", "mode", "clients", "messages", "broadcast_messages",
                "private_messages", "avg_delay_ms", "throughput_msgs_per_sec",
                "cpu_percent", "memory_mb", "duration_sec"
            ])
    SECURITY_LOG_FILE.touch(exist_ok=True)


def log_message(sender, receiver, msg_type, message):
    # File writes are short and serialized; network I/O never happens while holding state_lock.
    try:
        with state_lock:
            with HISTORY_FILE.open("a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([now_text(), sender, receiver, msg_type, message])
    except OSError as exc:
        security_log("HISTORY_WRITE_ERROR", sender, "-", type(exc).__name__)


def get_last_n_messages_by_user(username, n=5):
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as f:
            rows = [r for r in csv.DictReader(f) if r.get("sender") == username]
        return rows[-n:]
    except (OSError, csv.Error):
        return []


def validate_username(username):
    return (
        isinstance(username, str)
        and len(username) <= MAX_USERNAME_LENGTH
        and bool(USERNAME_RE.fullmatch(username))
    )


def validate_password(password):
    return isinstance(password, str) and 1 <= len(password) <= MAX_PASSWORD_LENGTH


def validate_message(message):
    return isinstance(message, str) and bool(message) and len(message) <= MAX_MESSAGE_LENGTH


def validate_command(message):
    if not message.startswith("/"):
        return True
    return message.split(" ", 1)[0].lower() in SUPPORTED_COMMANDS


def send_line(sock, message):
    sock.sendall((message + "\n").encode("utf-8"))


def recv_line(sock, buffer):
    while "\n" not in buffer:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            return None, buffer
        buffer += data.decode("utf-8", errors="replace")
        if len(buffer) > MAX_MESSAGE_LENGTH + 256:
            raise ValueError("Input exceeds maximum allowed size")
    line, buffer = buffer.split("\n", 1)
    return line.rstrip("\r"), buffer


def is_locked(username):
    with state_lock:
        state = failed_logins.get(username)
        if not state:
            return False, 0
        remaining = state.get("locked_until", 0) - time.time()
        if remaining > 0:
            return True, int(remaining) + 1
        if state.get("locked_until", 0):
            failed_logins.pop(username, None)
        return False, 0


def authenticate(username, password, client_addr):
    addr = f"{client_addr[0]}:{client_addr[1]}"
    if not validate_username(username):
        security_log("INVALID_LOGIN_INPUT", username or "-", addr, "invalid username")
        return False, "Invalid username format."
    if not validate_password(password):
        security_log("INVALID_LOGIN_INPUT", username, addr, "invalid password length")
        return False, "Invalid password."

    locked, remaining = is_locked(username)
    if locked:
        security_log("LOGIN_BLOCKED", username, addr, f"retry_in={remaining}s")
        return False, f"Account temporarily locked. Try again in {remaining} seconds."

    stored_hash = load_users().get(username)
    valid = stored_hash is not None and hash_password(password) == stored_hash

    with state_lock:
        if not valid:
            state = failed_logins.setdefault(username, {"count": 0, "locked_until": 0})
            state["count"] += 1
            count = state["count"]
            if count >= MAX_FAILED_ATTEMPTS:
                state["locked_until"] = time.time() + LOCKOUT_DURATION
        else:
            failed_logins.pop(username, None)

    if not valid:
        security_log("LOGIN_FAILED", username, addr, "credentials rejected")
        if count >= MAX_FAILED_ATTEMPTS:
            security_log("ACCOUNT_LOCKED", username, addr, f"duration={LOCKOUT_DURATION}s")
            return False, f"Too many failed attempts. Login blocked for {int(LOCKOUT_DURATION)} seconds."
        return False, "Invalid username or password."

    with state_lock:
        if username in clients and clients[username]["online"]:
            security_log("DUPLICATE_LOGIN", username, addr, "already logged in")
            return False, "This username is already logged in."

    security_log("LOGIN_SUCCESS", username, addr, "authentication successful")
    return True, "Authentication successful."


def get_online_users():
    with state_lock:
        return [u for u, info in clients.items() if info["online"]]


def _snapshot_clients(exclude_sock=None):
    # Critical scalability optimization: release lock before network I/O.
    with state_lock:
        return [
            (u, info["sock"])
            for u, info in clients.items()
            if info["online"] and info["sock"] is not exclude_sock
        ]


def broadcast(message, exclude_sock=None):
    dead = []
    for username, sock in _snapshot_clients(exclude_sock):
        try:
            send_line(sock, message)
        except (OSError, ConnectionError):
            dead.append((username, sock))
    for username, sock in dead:
        cleanup_client(username, sock, reason="send_failure")


def send_to_user(username, message):
    with state_lock:
        info = clients.get(username)
        if not info or not info["online"]:
            return False
        sock = info["sock"]

    try:
        send_line(sock, message)
        return True
    except (OSError, ConnectionError):
        cleanup_client(username, sock, reason="private_send_failure")
        return False


def cleanup_client(username, sock=None, reason="disconnect"):
    if not username:
        return
    removed = False
    with state_lock:
        info = clients.get(username)
        if not info:
            return
        if sock is not None and info.get("sock") is not sock:
            return
        if info["online"]:
            info["online"] = False
            removed = True
        actual_sock = info.get("sock")
        info["sock"] = None
        if actual_sock is not None:
            username_of.pop(actual_sock, None)

    if removed:
        security_log("CLIENT_CLEANUP", username, "-", reason)


def register_authenticated_client(client_sock, client_addr, username):
    global max_clients_seen
    with state_lock:
        if sum(1 for info in clients.values() if info["online"]) >= MAX_CLIENTS:
            return False, "Server capacity reached. Please try again later."
        if username in clients and clients[username]["online"]:
            return False, "This username is already logged in."

        clients[username] = {
            "sock": client_sock,
            "addr": client_addr,
            "login_time": now_text(),
            "last_activity": time.time(),
            "online": True,
        }
        username_of[client_sock] = username
        online_now = sum(1 for info in clients.values() if info["online"])
        max_clients_seen = max(max_clients_seen, online_now)
    return True, "registered"


def get_server_stats():
    with state_lock:
        online = sum(1 for info in clients.values() if info["online"])
        return (
            f"[SERVER STATS] Connected users: {online} | "
            f"Messages processed: {stats['messages_processed']} | "
            f"Broadcasts: {stats['broadcast_messages']} | "
            f"Private: {stats['private_messages']}"
        )


def update_activity(username):
    with state_lock:
        if username in clients and clients[username]["online"]:
            clients[username]["last_activity"] = time.time()
            stats["messages_processed"] += 1


def handle_client(client_sock, client_addr):
    username = None
    buffer = ""
    addr = f"{client_addr[0]}:{client_addr[1]}"

    try:
        client_sock.settimeout(SOCKET_TIMEOUT)
        send_line(client_sock, "AUTH_REQUIRED")
        send_line(client_sock, "AUTH format: LOGIN <username> <password> | SIGNUP <username> <password>")

        while not shutdown_event.is_set():
            try:
                line, buffer = recv_line(client_sock, buffer)
            except socket.timeout:
                continue
            if line is None:
                return
            if not line:
                send_line(client_sock, "AUTH_FAIL Empty authentication request.")
                continue

            parts = line.split(" ", 2)
            if len(parts) != 3 or parts[0].upper() not in ("LOGIN", "SIGNUP"):
                send_line(client_sock, "AUTH_FAIL Unsupported authentication command.")
                security_log("AUTH_PROTOCOL_ERROR", "-", addr, "unsupported authentication command")
                continue

            action, username, password = parts[0].upper(), parts[1].strip(), parts[2]

            if action == "SIGNUP":
                ok, reason = register_user(username, password, client_addr)
                send_line(client_sock, f"{'SIGNUP_OK' if ok else 'SIGNUP_FAIL'} {reason}")
                continue

            ok, reason = authenticate(username, password, client_addr)
            if not ok:
                send_line(client_sock, f"AUTH_FAIL {reason}")
                continue

            ok, reason = register_authenticated_client(client_sock, client_addr, username)
            if not ok:
                send_line(client_sock, f"AUTH_FAIL {reason}")
                security_log("LOGIN_REJECTED", username, addr, reason)
                return

            send_line(client_sock, f"AUTH_OK Welcome {username}!")
            break

        if not username or shutdown_event.is_set():
            return

        broadcast(f"[SERVER] {username} has joined the chat.", exclude_sock=client_sock)
        broadcast("[SERVER] Online users: " + ", ".join(get_online_users()))
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

        while not shutdown_event.is_set():
            try:
                line, buffer = recv_line(client_sock, buffer)
            except socket.timeout:
                with state_lock:
                    info = clients.get(username)
                    last_activity = info["last_activity"] if info else time.time()
                if time.time() - last_activity >= SESSION_TIMEOUT:
                    send_line(client_sock, "[SERVER] Session expired due to inactivity.")
                    security_log("SESSION_TIMEOUT", username, addr, f"timeout={SESSION_TIMEOUT}s")
                    break
                continue

            if line is None:
                security_log("CLIENT_DISCONNECTED", username, addr, "peer closed connection")
                break

            message = line.strip()
            if not message:
                security_log("INVALID_INPUT", username, addr, "empty message")
                continue

            if len(message) > MAX_MESSAGE_LENGTH:
                send_line(client_sock, f"[SERVER] Message rejected: maximum length is {MAX_MESSAGE_LENGTH} characters.")
                security_log("INPUT_REJECTED", username, addr, "message too large")
                continue

            if not validate_command(message):
                send_line(client_sock, "[SERVER] Unsupported command.")
                security_log("COMMAND_REJECTED", username, addr, "unsupported command")
                continue

            update_activity(username)
            lowered = message.lower()

            if lowered in ("/quit", "/exit"):
                send_line(client_sock, "[SERVER] Goodbye!")
                security_log("LOGOUT", username, addr, "client requested logout")
                break

            if lowered == "/list":
                online = get_online_users()
                send_line(client_sock, "[SERVER] Online users: " + (", ".join(online) if online else "none"))
                continue

            if lowered == "/stats":
                send_line(client_sock, get_server_stats())
                continue

            if message.startswith("/msg "):
                parts = message.split(" ", 2)
                if len(parts) < 3:
                    send_line(client_sock, "[SERVER] Usage: /msg <username> <message>")
                    continue
                target, private_text = parts[1].strip(), parts[2].strip()
                if not validate_username(target) or not validate_message(private_text):
                    send_line(client_sock, "[SERVER] Invalid private message or target.")
                    continue
                if target == username:
                    send_line(client_sock, "[SERVER] You cannot send a private message to yourself.")
                    continue

                if send_to_user(target, f"[PRIVATE from {username}]: {private_text}"):
                    with state_lock:
                        stats["private_messages"] += 1
                    send_line(client_sock, f"[SERVER] Private message sent to {target}.")
                    log_message(username, target, "private", private_text)
                else:
                    send_line(client_sock, f"[SERVER] Error: User '{target}' does not exist or is offline.")
                continue

            broadcast(f"[{username}]: {message}")
            with state_lock:
                stats["broadcast_messages"] += 1
            log_message(username, "ALL", "broadcast", message)

    except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
        security_log("CLIENT_DISCONNECTED", username or "-", addr, "connection reset")
    except (OSError, ValueError) as exc:
        security_log("CLIENT_ERROR", username or "-", addr, type(exc).__name__)
        try:
            send_line(client_sock, "[SERVER] Connection closed due to a network/input error.")
        except OSError:
            pass
    except Exception as exc:
        print(f"[!] Unexpected client error {addr}: {exc}")
        security_log("SERVER_ERROR", username or "-", addr, type(exc).__name__)
    finally:
        if username:
            cleanup_client(username, client_sock, reason="handler_exit")
            if not shutdown_event.is_set():
                broadcast(f"[SERVER] {username} has left the chat.")
                broadcast("[SERVER] Online users: " + (", ".join(get_online_users()) if get_online_users() else "none"))
        try:
            client_sock.close()
        except OSError:
            pass


def cleanup_inactive_clients():
    while not shutdown_event.wait(CLEANUP_INTERVAL):
        now = time.time()
        expired = []
        with state_lock:
            for username, info in clients.items():
                if info["online"] and now - info["last_activity"] >= SESSION_TIMEOUT:
                    expired.append((username, info["sock"]))
        for username, sock in expired:
            try:
                send_line(sock, "[SERVER] Session expired due to inactivity.")
            except OSError:
                pass
            cleanup_client(username, sock, reason="inactivity_timeout")
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                sock.close()
            except OSError:
                pass
            security_log("SESSION_TIMEOUT", username, "-", f"cleanup_worker timeout={SESSION_TIMEOUT}s")


def process_cpu_memory():
    if psutil is None:
        return 0.0, 0.0
    proc = psutil.Process(os.getpid())
    try:
        cpu = proc.cpu_percent(interval=0.1)
        memory_mb = proc.memory_info().rss / (1024 * 1024)
        return round(cpu, 2), round(memory_mb, 2)
    except (psutil.Error, OSError):
        return 0.0, 0.0


def print_runtime_summary():
    """Print runtime statistics. Actual Assignment 8 benchmark rows are written
    by benchmark.py so performance_results.csv contains only controlled
    5/8/10-client experiment measurements.
    """
    elapsed = max(time.time() - server_start_time, 0.001) if server_start_time else 0.001
    with state_lock:
        total = stats["messages_processed"]
        broadcasts = stats["broadcast_messages"]
        private = stats["private_messages"]
        clients_count = max_clients_seen
    throughput = total / elapsed
    cpu, memory = process_cpu_memory()
    print(
        f"[*] Runtime summary: max_clients={clients_count}, messages={total}, "
        f"broadcasts={broadcasts}, private={private}, throughput={throughput:.2f} msg/s, "
        f"CPU={cpu:.2f}%, RAM={memory:.2f} MB"
    )


def graceful_shutdown(signum=None, frame=None):
    if shutdown_event.is_set():
        return
    print("\n[*] Graceful shutdown requested...")
    shutdown_event.set()

    # Stop accepting new connections.
    global server_socket
    if server_socket:
        try:
            server_socket.close()
        except OSError:
            pass

    # Tell clients and release all sockets.
    with state_lock:
        active = [(u, info["sock"]) for u, info in clients.items() if info["online"] and info.get("sock")]

    for username, sock in active:
        try:
            send_line(sock, "[SERVER] Server is shutting down. Goodbye.")
        except OSError:
            pass
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            sock.close()
        except OSError:
            pass
        cleanup_client(username, sock, reason="server_shutdown")

    if executor:
        executor.shutdown(wait=False, cancel_futures=True)


def main():
    global server_socket, executor, server_start_time, max_clients_seen

    init_files()
    server_start_time = time.time()
    max_clients_seen = 0
    shutdown_event.clear()
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

    signal.signal(signal.SIGINT, graceful_shutdown)
    signal.signal(signal.SIGTERM, graceful_shutdown)

    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="tcp-client")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(BACKLOG)
    server_socket.settimeout(ACCEPT_TIMEOUT)

    cleanup_thread = threading.Thread(target=cleanup_inactive_clients, name="cleanup-worker", daemon=True)
    cleanup_thread.start()

    print(f"[*] Assignment 8 Secure TCP Server listening on {HOST}:{PORT}")
    print(f"[*] backlog={BACKLOG}, max_workers={MAX_WORKERS}, max_clients={MAX_CLIENTS}")
    print(f"[*] Mininet target: 10 concurrent clients")
    print("[*] Press Ctrl+C for graceful shutdown.")

    try:
        while not shutdown_event.is_set():
            try:
                sock, addr = server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                if shutdown_event.is_set():
                    break
                continue

            with state_lock:
                if sum(1 for info in clients.values() if info["online"]) >= MAX_CLIENTS:
                    stats["connections_rejected"] += 1
                    try:
                        send_line(sock, "[SERVER] Server capacity reached. Please try again later.")
                        sock.close()
                    except OSError:
                        pass
                    continue
                stats["connections_accepted"] += 1

            try:
                executor.submit(handle_client, sock, addr)
            except RuntimeError:
                stats["connections_rejected"] += 1
                try:
                    sock.close()
                except OSError:
                    pass

    finally:
        graceful_shutdown()
        print_runtime_summary()
        try:
            PID_FILE.unlink(missing_ok=True)
        except OSError:
            pass
        print("[*] Server closed cleanly.")


if __name__ == "__main__":
    main()
