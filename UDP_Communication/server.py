# server.py
import socket
import argparse

def main():
    parser = argparse.ArgumentParser(description="Reliable UDP Server using Stop-and-Wait")
    parser.add_argument("--host", default="0.0.0.0", help="IP address to bind the server")
    parser.add_argument("--port", type=int, default=5000, help="UDP port number")
    args = parser.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((args.host, args.port))

    print("==========================================")
    print(" Reliable UDP Server Started")
    print(f" Listening on {args.host}:{args.port}")
    print("==========================================")

    received_sequences = set()
    total_unique_messages = 0
    total_duplicates = 0

    while True:
        data, client_addr = server_socket.recvfrom(4096)
        message = data.decode().strip()

        # Client sends END after all messages are delivered
        if message == "END":
            print("\n========== SERVER FINAL OUTPUT ==========")
            print(f"TOTAL_UNIQUE_MESSAGES_RECEIVED={total_unique_messages}")
            print(f"TOTAL_DUPLICATES_DETECTED={total_duplicates}")
            print("STATUS=SUCCESS")
            print("=========================================")
            break

        # Expected format: SEQ|MESSAGE
        if "|" not in message:
            print(f"[SERVER] Invalid packet received: {message}")
            continue

        seq_str, payload = message.split("|", 1)

        try:
            seq = int(seq_str)
        except ValueError:
            print(f"[SERVER] Invalid sequence number in packet: {message}")
            continue

        if seq in received_sequences:
            total_duplicates += 1
            print(f"[SERVER] Duplicate packet received -> SEQ={seq}, MSG='{payload}'")
        else:
            received_sequences.add(seq)
            total_unique_messages += 1
            print(f"[SERVER] New packet received -> SEQ={seq}, MSG='{payload}'")

        # ACK every received packet, including duplicates
        ack = f"ACK|{seq}"
        server_socket.sendto(ack.encode(), client_addr)
        print(f"[SERVER] Sent {ack}")

    server_socket.close()


if __name__ == "__main__":
    main()