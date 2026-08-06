import socket
import threading
import sys

SERVER_IP = "10.0.0.1"      # h1 IP in Mininet
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((SERVER_IP, PORT))
except Exception as e:
    print("Unable to connect to server:", e)
    sys.exit()

username = input("Enter Username: ").strip()

while username == "":
    username = input("Username cannot be empty. Enter Username: ").strip()

client.send(username.encode())

running = True


def receive_messages():
    global running

    while running:
        try:
            message = client.recv(1024).decode()

            if not message:
                print("\nServer disconnected.")
                break

            if message == "SERVER CLOSED":
                print("\nServer has been closed.")
                break

            print(f"\n{message}")

        except:
            print("\nConnection lost.")
            break

    running = False

    try:
        client.close()
    except:
        pass

    sys.exit()


threading.Thread(
    target=receive_messages,
    daemon=True
).start()

print("\n===================================")
print(" Connected to Chat Server")
print("===================================")
print("Type your message and press Enter.")
print("Type 'exit' to disconnect.\n")

while running:

    try:
        message = input()

        if not running:
            break

        if message.strip() == "":
            continue

        if message.lower() == "exit":
            running = False
            client.close()
            break

        client.send(message.encode())

        # Display your own message
        print(f"[You] {message}")

    except KeyboardInterrupt:
        running = False
        break

    except:
        break

try:
    client.close()
except:
    pass

print("Disconnected successfully.")
