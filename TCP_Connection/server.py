import socket
import datetime

HOST = "10.0.0.1"
PORT = 5000

MAX_CONNECTIONS = 33      # 3 persistent + 30 new_connection

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server started...")

connection_count = 0

while connection_count < MAX_CONNECTIONS:

    conn, addr = server.accept()
    connection_count += 1

    print(f"Connection {connection_count}/{MAX_CONNECTIONS} from {addr}")

    while True:

        data = conn.recv(2048)

        if not data:
            break

        msg = data.decode()

        try:
            msg_id, size, payload = msg.split("|", 2)
        except ValueError:
            print("Invalid message format")
            continue

        ack = f"ACK|{msg_id}|{size}"
        conn.send(ack.encode())

        with open("server_log.txt", "a") as f:
            f.write(
                f"{datetime.datetime.now()},"
                f"{addr[0]},"
                f"{msg_id},"
                f"{size},ACK\n"
            )

    conn.close()

print("\nExperiment Complete")
server.close()
print("Server Closed")