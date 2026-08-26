#!/usr/bin/env python3
"""Assignment 8: real 5/8/10-client performance benchmark.

Run the server first, then:
  python3 benchmark.py --clients 5 --mode optimized
  python3 benchmark.py --clients 8 --mode optimized
  python3 benchmark.py --clients 10 --mode optimized

For the before/after comparison, run the same commands against the unchanged
Assignment 7 server and use --mode baseline for those rows.
"""
import argparse
import csv
import json
import os
import socket
import threading
import time
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None

BASE = Path(__file__).resolve().parent
CONFIG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
HOST = CONFIG["client"]["host"]
PORT = int(CONFIG["client"]["port"])
BUF = int(CONFIG["client"]["buffer_size"])
TEST_SECONDS = float(CONFIG["performance"]["test_seconds"])
CONNECT_TIMEOUT = float(CONFIG["client"]["connect_timeout"])
PERF = BASE / CONFIG["application"].get("performance_file", "performance_results.csv")


def read_lines(sock, minimum=1, timeout=5):
    sock.settimeout(timeout)
    data = b""
    lines = []
    while len(lines) < minimum:
        chunk = sock.recv(BUF)
        if not chunk:
            raise ConnectionError("server closed connection")
        data += chunk
        while b"\n" in data:
            raw, data = data.split(b"\n", 1)
            lines.append(raw.decode("utf-8", errors="replace").rstrip("\r"))
    return lines, data


def request(action, username, password):
    with socket.create_connection((HOST, PORT), timeout=CONNECT_TIMEOUT) as sock:
        lines, buf = read_lines(sock, 2)
        sock.sendall(f"{action} {username} {password}\n".encode())
        lines, _ = read_lines(sock, 1)
        return lines[0]


def ensure_accounts(count):
    for i in range(1, count + 1):
        user = f"bench{i:02d}"
        password = f"BenchPass{i:02d}!"
        response = request("SIGNUP", user, password)
        if response.startswith("SIGNUP_OK") or "already exists" in response.lower():
            continue
        raise RuntimeError(f"Could not prepare {user}: {response}")


def login(sock, username, password):
    lines, buf = read_lines(sock, 2, CONNECT_TIMEOUT)
    sock.sendall(f"LOGIN {username} {password}\n".encode())
    lines, _ = read_lines(sock, 1, CONNECT_TIMEOUT)
    if not lines[0].startswith("AUTH_OK "):
        raise RuntimeError(lines[0])
    # The remaining welcome/list/history messages are intentionally drained
    # before the measured interval starts.
    sock.settimeout(0.1)
    try:
        while True:
            if not sock.recv(BUF):
                break
    except socket.timeout:
        pass


def run_client(index, barrier, deadline, results):
    username = f"bench{index:02d}"
    password = f"BenchPass{index:02d}!"
    messages = 0
    latencies = []
    errors = 0
    try:
        sock = socket.create_connection((HOST, PORT), timeout=CONNECT_TIMEOUT)
        login(sock, username, password)
        sock.settimeout(1.0)
        barrier.wait(timeout=CONNECT_TIMEOUT)

        while time.perf_counter() < deadline:
            token = f"BENCH_{index}_{messages}_{time.time_ns()}"
            start = time.perf_counter()
            sock.sendall((token + "\n").encode())
            found = False
            buffer = b""
            while time.perf_counter() < deadline:
                try:
                    chunk = sock.recv(BUF)
                except socket.timeout:
                    errors += 1
                    break
                if not chunk:
                    raise ConnectionError("server closed during benchmark")
                buffer += chunk
                while b"\n" in buffer:
                    raw, buffer = buffer.split(b"\n", 1)
                    text = raw.decode("utf-8", errors="replace")
                    if token in text:
                        latencies.append((time.perf_counter() - start) * 1000.0)
                        found = True
                        break
                if found:
                    break
            if not found:
                errors += 1
                continue
            messages += 1

        try:
            sock.sendall(b"/quit\n")
        except OSError:
            pass
        sock.close()
    except Exception as exc:
        errors += 1
        results[index] = {"messages": messages, "latencies": latencies, "errors": errors, "error": str(exc)}
        return
    results[index] = {"messages": messages, "latencies": latencies, "errors": errors, "error": ""}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--clients", type=int, required=True, choices=[5, 8, 10])
    parser.add_argument("--mode", choices=["baseline", "optimized"], default="optimized")
    args = parser.parse_args()

    ensure_accounts(args.clients)
    barrier = threading.Barrier(args.clients)
    results = {}
    threads = []
    deadline = time.perf_counter() + TEST_SECONDS

    # The server process is identified by server.pid when available.
    proc = None
    pid_file = BASE / "server.pid"
    if psutil and pid_file.exists():
        try:
            proc = psutil.Process(int(pid_file.read_text().strip()))
            proc.cpu_percent(interval=None)
        except Exception:
            proc = None

    start = time.perf_counter()
    for i in range(1, args.clients + 1):
        t = threading.Thread(target=run_client, args=(i, barrier, deadline, results), daemon=True)
        threads.append(t)
        t.start()
    for t in threads:
        t.join(timeout=TEST_SECONDS + CONNECT_TIMEOUT + 5)
    duration = max(time.perf_counter() - start, 0.001)

    total = sum(r.get("messages", 0) for r in results.values())
    all_latencies = [x for r in results.values() for x in r.get("latencies", [])]
    avg_delay = sum(all_latencies) / len(all_latencies) if all_latencies else 0.0
    throughput = total / duration
    errors = sum(r.get("errors", 0) for r in results.values())

    cpu = 0.0
    memory = 0.0
    if proc:
        try:
            cpu = proc.cpu_percent(interval=0.1)
            memory = proc.memory_info().rss / (1024 * 1024)
        except Exception:
            pass

    PERF.parent.mkdir(parents=True, exist_ok=True)
    if not PERF.exists():
        PERF.write_text(
            "timestamp,mode,clients,messages,errors,avg_delay_ms,throughput_msgs_per_sec,cpu_percent,memory_mb,duration_sec\n",
            encoding="utf-8",
        )
    with PERF.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            time.strftime("%Y-%m-%d %H:%M:%S"), args.mode, args.clients,
            total, errors, round(avg_delay, 3), round(throughput, 3),
            round(cpu, 2), round(memory, 2), round(duration, 3)
        ])

    print(f"mode={args.mode} clients={args.clients} messages={total} errors={errors}")
    print(f"avg RTT/delay={avg_delay:.3f} ms throughput={throughput:.3f} msg/s CPU={cpu:.2f}% RAM={memory:.2f} MB")


if __name__ == "__main__":
    main()
