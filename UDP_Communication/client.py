# client.py
import socket
import argparse
import time
import csv
import os

def get_timeout_from_roll(roll_no: str) -> float:
    last_digit = int(roll_no[-1])
    if last_digit in [0, 1]:
        return 0.5
    elif last_digit in [2, 3]:
        return 0.7
    elif last_digit in [4, 5]:
        return 1.0
    elif last_digit in [6, 7]:
        return 1.2
    else:
        return 1.5

def initialize_csv(csv_file):
    if not os.path.exists(csv_file):
        with open(csv_file, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "roll_no",
                "name",
                "loss_percent",
                "timeout",
                "total_messages",
                "total_packets_sent",
                "total_retransmissions",
                "transfer_time_seconds",
                "status"
            ])

def append_csv_row(csv_file, roll_no, name, loss_percent, timeout,
                   total_messages, total_packets_sent,
                   total_retransmissions, transfer_time_seconds, status):
    with open(csv_file, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            roll_no,
            name,
            loss_percent,
            timeout,
            total_messages,
            total_packets_sent,
            total_retransmissions,
            transfer_time_seconds,
            status
        ])

def main():
    parser = argparse.ArgumentParser(description="Reliable UDP Client using Stop-and-Wait")
    parser.add_argument("--server-ip", default="10.0.0.1", help="Server IP address")
    parser.add_argument("--server-port", type=int, default=5000, help="Server UDP port")
    parser.add_argument("--loss", type=int, required=True, help="Packet loss percentage used in Mininet")
    parser.add_argument("--roll", required=True, help="Student roll number")
    parser.add_argument("--name", required=True, help="Student name")
    parser.add_argument("--csv", default="result_table.csv", help="CSV file name")
    args = parser.parse_args()

    timeout = get_timeout_from_roll(args.roll)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(timeout)

    total_messages = 10
    total_packets_sent = 0
    total_retransmissions = 0

    initialize_csv(args.csv)

    print("==========================================")
    print(" Reliable UDP Client Started")
    print(f" Server IP: {args.server_ip}")
    print(f" Server Port: {args.server_port}")
    print(f" Roll Number: {args.roll}")
    print(f" Name: {args.name}")
    print(f" Timeout selected automatically: {timeout} seconds")
    print(f" Loss percentage: {args.loss}%")
    print("==========================================")

    start_time = time.time()

    for seq in range(1, total_messages + 1):
        msg = f"Message {seq} from h2"
        packet = f"{seq}|{msg}"

        ack_received = False

        while not ack_received:
            try:
                client_socket.sendto(packet.encode(), (args.server_ip, args.server_port))
                total_packets_sent += 1
                print(f"[CLIENT] Sent packet -> {packet}")

                data, _ = client_socket.recvfrom(4096)
                ack = data.decode().strip()
                print(f"[CLIENT] Received -> {ack}")

                expected_ack = f"ACK|{seq}"
                if ack == expected_ack:
                    ack_received = True
                    print(f"[CLIENT] Correct ACK received for SEQ={seq}\n")
                else:
                    print(f"[CLIENT] Incorrect ACK received. Expected {expected_ack}, got {ack}")
                    total_retransmissions += 1

            except socket.timeout:
                print(f"[CLIENT] Timeout for SEQ={seq}. Retransmitting...\n")
                total_retransmissions += 1

    end_time = time.time()
    transfer_time = round(end_time - start_time, 4)

    client_socket.sendto("END".encode(), (args.server_ip, args.server_port))

    print("\n========== CLIENT FINAL OUTPUT ==========")
    print(f"TOTAL_MESSAGES={total_messages}")
    print(f"LOSS_PERCENT={args.loss}")
    print(f"TIMEOUT={timeout}")
    print(f"TOTAL_PACKETS_SENT={total_packets_sent}")
    print(f"TOTAL_RETRANSMISSIONS={total_retransmissions}")
    print(f"TRANSFER_TIME_SECONDS={transfer_time}")
    print("STATUS=SUCCESS")
    print("=========================================")

    append_csv_row(
        csv_file=args.csv,
        roll_no=args.roll,
        name=args.name,
        loss_percent=args.loss,
        timeout=timeout,
        total_messages=total_messages,
        total_packets_sent=total_packets_sent,
        total_retransmissions=total_retransmissions,
        transfer_time_seconds=transfer_time,
        status="SUCCESS"
    )

    client_socket.close()

if __name__ == "__main__":
    main()