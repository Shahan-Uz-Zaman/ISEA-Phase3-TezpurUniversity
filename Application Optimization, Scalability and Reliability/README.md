# Assignment 8 - Application Optimization, Scalability and Reliability

This project is a direct extension of Assignment 7. It keeps the same GUI, TCP protocol, Sign Up/Login, SHA-256 credential storage, duplicate-login prevention, validation, lockout, session timeout, logging, broadcast and private messaging.

## Assignment 8 improvements

### Task 1 - Connection Management
- Detects peer disconnects and cleans up stale sessions.
- Central cleanup releases socket/user mappings.
- Inactivity cleanup worker removes expired sessions.
- Server capacity protection and meaningful errors.

### Task 2 - Reliability
- Client automatic reconnection after unexpected disconnect.
- Configurable connect/socket timeouts.
- Graceful SIGINT/SIGTERM server shutdown.
- Explicit handling of reset, broken pipe, timeout and socket errors.

### Task 3 - Scalability
- `ThreadPoolExecutor` provides a bounded worker pool.
- Default `max_workers` and `max_clients` are 10 for the required test.
- Network I/O is not performed while the global state lock is held.
- Listen backlog is configurable.

### Task 4 - Configuration
Operational values are stored in `config.json` instead of being scattered through the Python code.

### Task 5 - Performance
`benchmark.py` performs actual concurrent-client measurements for 5, 8 and 10 clients. It records average TCP message round-trip delay, throughput, CPU and memory. `generate_graphs.py` creates graphs from the actual CSV rows.

Do not invent results. For before/after comparison, run the benchmark against the unchanged Assignment 7 server with `--mode baseline`, then run Assignment 8 with `--mode optimized`.

## Files

- `server.py`
- `client_gui.py`
- `config.json`
- `users.csv`
- `security_log.txt`
- `chat_history.csv`
- `performance_results.csv`
- `benchmark.py`
- `generate_graphs.py`
- `requirements.txt`
- `graphs/`
- `screenshots/`
- `report_template.md`
- `handwritten_reflection_questions.txt`

## Install

```bash
python3 -m pip install -r requirements.txt
```

Tkinter may need to be installed separately on Ubuntu:

```bash
sudo apt install python3-tk
```

## Run normally

Server:

```bash
python3 server.py
```

Client:

```bash
python3 client_gui.py
```

The default Mininet client address is `10.0.0.1:5000`.

## Mininet experiment

Assignment 8 requires:

```bash
sudo mn --topo single,11
nodes
net
pingall
```

Use 5, 8 and 10 concurrent clients.

## Performance experiment

Start the optimized server, then run:

```bash
python3 benchmark.py --clients 5 --mode optimized
python3 benchmark.py --clients 8 --mode optimized
python3 benchmark.py --clients 10 --mode optimized
python3 generate_graphs.py
```

For baseline results, run the same commands against the original Assignment 7 server and use:

```bash
python3 benchmark.py --clients 5 --mode baseline
python3 benchmark.py --clients 8 --mode baseline
python3 benchmark.py --clients 10 --mode baseline
```

The benchmark creates unique test accounts automatically before the measured interval.
