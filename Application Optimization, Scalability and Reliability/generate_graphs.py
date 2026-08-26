#!/usr/bin/env python3
"""Generate Assignment 8 graphs only from actual benchmark CSV rows."""
import csv
from pathlib import Path
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
CSV_FILE = BASE / "performance_results.csv"
OUT = BASE / "graphs"
OUT.mkdir(exist_ok=True)

if not CSV_FILE.exists():
    raise SystemExit("Run benchmark.py first; performance_results.csv does not exist.")

rows = list(csv.DictReader(CSV_FILE.open(encoding="utf-8")))
if not rows:
    raise SystemExit("No actual experiment rows found.")

metrics = [
    ("avg_delay_ms", "Average Delay (ms)", "delay_comparison.png"),
    ("throughput_msgs_per_sec", "Throughput (messages/sec)", "throughput_comparison.png"),
    ("cpu_percent", "CPU Usage (%)", "cpu_comparison.png"),
    ("memory_mb", "Memory Usage (MB)", "memory_comparison.png"),
]

for field, ylabel, filename in metrics:
    plt.figure()
    modes = sorted({r["mode"] for r in rows if r.get("mode")})
    for mode in modes:
        subset = sorted(
            (r for r in rows if r.get("mode") == mode),
            key=lambda r: int(r["clients"]),
        )
        if subset:
            x = [int(r["clients"]) for r in subset]
            y = [float(r[field]) for r in subset]
            plt.plot(x, y, marker="o", label=mode)
    plt.xlabel("Concurrent Clients")
    plt.ylabel(ylabel)
    plt.title(f"{ylabel} vs Concurrent Clients")
    plt.legend()
    plt.grid(True)
    plt.savefig(OUT / filename, dpi=150, bbox_inches="tight")
    plt.close()

print(f"Generated {len(metrics)} graphs in {OUT}")
