import socket
import time
import csv
import os
import matplotlib.pyplot as plt

SERVER_IP = "10.0.0.1"
PORT = 5000

ROLL_NO = "CS-BTC24-23"
NAME = "Shahan Uz Zaman"

MESSAGE_SIZES = [128, 512, 1024]
TOTAL_MESSAGES = 10

response_log = []
result_table = []


def send_message(sock, msg_id, size):
    data = "A" * size
    message = f"{msg_id}|{size}|{data}"

    start = time.perf_counter()

    sock.send(message.encode())

    ack = sock.recv(1024).decode()

    end = time.perf_counter()

    response_time = end - start

    return response_time


def persistent_mode():

    print("\nRunning Persistent Mode")

    for size in MESSAGE_SIZES:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, PORT))

        total_bytes = 0
        total_time = 0

        for i in range(1, TOTAL_MESSAGES + 1):

            rt = send_message(sock, i, size)

            response_log.append([
                ROLL_NO,
                NAME,
                "persistent",
                size,
                i,
                rt
            ])

            total_bytes += size
            total_time += rt

        sock.close()

        avg = total_time / TOTAL_MESSAGES
        throughput = total_bytes / total_time

        result_table.append([
            ROLL_NO,
            NAME,
            "persistent",
            5,
            50,
            size,
            TOTAL_MESSAGES,
            avg,
            throughput,
            "Success"
        ])


def new_connection_mode():

    print("\nRunning New Connection Mode")

    for size in MESSAGE_SIZES:

        total_bytes = 0
        total_time = 0

        for i in range(1, TOTAL_MESSAGES + 1):

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            sock.connect((SERVER_IP, PORT))

            rt = send_message(sock, i, size)

            sock.close()

            response_log.append([
                ROLL_NO,
                NAME,
                "new_connection",
                size,
                i,
                rt
            ])

            total_bytes += size
            total_time += rt

        avg = total_time / TOTAL_MESSAGES
        throughput = total_bytes / total_time

        result_table.append([
            ROLL_NO,
            NAME,
            "new_connection",
            5,
            50,
            size,
            TOTAL_MESSAGES,
            avg,
            throughput,
            "Success"
        ])


def save_csv():

    with open("message_response_log.csv", "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "roll_no",
            "name",
            "mode",
            "message_size_bytes",
            "message_number",
            "response_time_seconds"
        ])

        writer.writerows(response_log)

    with open("result_table.csv", "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow([
            "roll_no",
            "name",
            "mode",
            "bandwidth_mbps",
            "delay_ms",
            "message_size_bytes",
            "total_messages",
            "average_response_time_seconds",
            "throughput_bytes_per_second",
            "status"
        ])

        writer.writerows(result_table)

def create_graphs():

    os.makedirs("graphs", exist_ok=True)

    # Graph 1
    modes = []
    avg_response = []

    for row in result_table:
        modes.append(f"{row[2]}-{row[5]}")
        avg_response.append(row[7])

    plt.figure(figsize=(8,5))
    plt.bar(modes, avg_response)
    plt.xlabel("Mode")
    plt.ylabel("Average Response Time (s)")
    plt.title("Mode vs Average Response Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("graphs/mode_vs_response_time.png")
    plt.close()


    # Graph 2
    labels = []
    throughput = []

    for row in result_table:
        labels.append(f"{row[2]}-{row[5]}")
        throughput.append(row[8])

    plt.figure(figsize=(8,5))
    plt.bar(labels, throughput)
    plt.xlabel("Mode and Message Size")
    plt.ylabel("Throughput (Bytes/sec)")
    plt.title("Message Size vs Throughput")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("graphs/message_size_vs_throughput.png")
    plt.close()


    # Graph 3
    persistent = []
    new_connection = []

    for row in response_log:

        if row[3] == 512:

            if row[2] == "persistent":
                persistent.append(row[5])

            else:
                new_connection.append(row[5])

    plt.figure(figsize=(8,5))

    plt.plot(range(1,11), persistent,
             marker='o',
             label="Persistent")

    plt.plot(range(1,11), new_connection,
             marker='s',
             label="New Connection")

    plt.xlabel("Message Number")
    plt.ylabel("Response Time (s)")
    plt.title("512-byte Response Time")

    plt.legend()
    plt.grid(True)

    plt.savefig("graphs/message_response_time.png")
    plt.close()

    print("Graphs created successfully.")


if __name__ == "__main__":

    persistent_mode()

    new_connection_mode()

    save_csv()

    create_graphs()

    print("Experiment Completed")