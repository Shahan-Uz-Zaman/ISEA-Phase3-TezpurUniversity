# Assignment 7 - Secure TCP Chat Application

This version extends the Assignment 6 multi-client TCP chat application.

## Account creation

Use the **Sign Up** button in the GUI to create a new account. The server checks that the username is unique, hashes the password with SHA-256, stores only the hash in `users.csv`, and returns a success message. The same username/password can then be used through the **Login** button.

## Demo accounts

- `student1` / `student123`
- `student2` / `student456`

Only SHA-256 password hashes are stored in `users.csv`.

## Security features

- Username/password authentication
- GUI Sign Up option for creating new accounts
- Newly registered credentials can immediately be used for Login
- SHA-256 password hashing
- Duplicate-login prevention
- Username/message/command validation
- Temporary lockout after 5 consecutive failed logins
- 5-minute inactivity session timeout
- Logout support
- Security event logging without passwords

## Run

Server:

```bash
python3 server.py
```

Client:

```bash
python3 client_gui.py
```

Mininet:

```bash
sudo mn --topo single,5
nodes
net
pingall
```

The client uses `10.0.0.1:5000` by default.

## Wireshark

Use:

```text
tcp.port == 5000
```

Capture successful login, failed login, authenticated communication, duplicate login/lockout, and logout.

Important: SHA-256 here protects passwords **at rest in users.csv**. The assignment does not add TLS, so the TCP login payload itself is still visible in Wireshark.
