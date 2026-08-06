#!/usr/bin/env python3
"""
Assignment 5: Advanced Multi-Client Chat Server using TCP
client.py - Interactive chat client.

Usage:
    python3 client.py

Just run the file. IP and port are set below.
"""

import socket
import threading
import sys
import time

# ============================================================
# CHANGE THESE VALUES IF NEEDED
# ============================================================
SERVER_IP   = "10.0.0.1"   # Use "10.0.0.1" inside Mininet (h1)
SERVER_PORT = 5000
# ============================================================

BUFFER_SIZE = 4096


def receive_messages(sock):
    """Background thread – continuously receives and prints messages."""
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("\n[!] Connection closed by server.")
                break
            sys.stdout.write(data.decode("utf-8"))
            sys.stdout.flush()
        except (ConnectionResetError, OSError):
            print("\n[!] Disconnected from server.")
            break
        except Exception as e:
            print(f"\n[!] Receive error: {e}")
            break


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"[*] Connecting to {SERVER_IP}:{SERVER_PORT} ...")
        sock.connect((SERVER_IP, SERVER_PORT))
        print("[+] Connected to the chat server.\n")
    except Exception as e:
        print(f"[!] Could not connect to server: {e}")
        return

    # Start receiver thread
    t = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
    t.start()

    # Small delay so welcome message appears first
    time.sleep(0.3)

    try:
        while True:
            try:
                msg = input()
            except EOFError:
                break

            if not msg:
                continue

            try:
                sock.sendall((msg + "\n").encode("utf-8"))
            except Exception as e:
                print(f"[!] Failed to send: {e}")
                break

            if msg.lower() in ("/quit", "/exit"):
                print("[*] Leaving chat...")
                break

    except KeyboardInterrupt:
        print("\n[*] Interrupted. Leaving chat...")
        try:
            sock.sendall(b"/quit\n")
        except Exception:
            pass
    finally:
        try:
            sock.close()
        except Exception:
            pass
        print("[*] Disconnected.")


if __name__ == "__main__":
    main()