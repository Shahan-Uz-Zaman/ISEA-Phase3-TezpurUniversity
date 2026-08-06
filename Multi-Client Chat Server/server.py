import socket
import threading
import csv
import os
import time
from datetime import datetime
import matplotlib
matplotlib.use("Agg")   # Use non-GUI backend

import matplotlib.pyplot as plt

HOST="10.0.0.1"
PORT=5000

clients=[]
usernames={}
running=True
message_count=0
total_delivery_time=0.0

server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.bind((HOST,PORT))
server.listen()

print(f"Chat Server Started on {HOST}:{PORT}")
print("Type 'exit' to stop the server.\n")

def log_event(event,user,ip):
    t=datetime.now().strftime("%H:%M:%S")
    line=f"{t},{event},{user},{ip}\n"
    print(line.strip())
    with open("connection_log.txt","a") as f:
        f.write(line)

def log_chat(user,msg):
    t=datetime.now().strftime("%H:%M:%S")
    with open("chat_log.txt","a") as f:
        f.write(f"{t},{user},{msg}\n")

def broadcast(msg,sender=None):
    global message_count,total_delivery_time
    start=time.perf_counter()
    dead=[]
    for c in clients:
        if c!=sender:
            try:
                c.send(msg.encode())
                message_count+=1
            except:
                dead.append(c)
    for c in dead:
        if c in clients:
            clients.remove(c)
    total_delivery_time+=(time.perf_counter()-start)*1000

def save_results():
    avg=total_delivery_time/message_count if message_count else 0
    thr=message_count/(total_delivery_time/1000) if total_delivery_time else 0
    exists=os.path.exists("performance_results.csv")
    with open("performance_results.csv","a",newline="") as f:
        w=csv.writer(f)
        if not exists:
            w.writerow(["clients","total_messages","avg_delivery_time_ms","throughput_msgs_per_sec"])
        w.writerow([len(usernames),message_count,round(avg,3),round(thr,3)])

def generate_graphs():

    try:
        print("Generating graphs...")

        os.makedirs("graphs", exist_ok=True)

        if not os.path.exists("performance_results.csv"):
            print("performance_results.csv not found!")
            return

        clients_data = []
        delay = []
        throughput = []

        with open("performance_results.csv", "r") as f:

            reader = csv.DictReader(f)

            for row in reader:

                print(row)

                clients_data.append(int(row["clients"]))
                delay.append(float(row["avg_delivery_time_ms"]))
                throughput.append(float(row["throughput_msgs_per_sec"]))

        print("Clients:", clients_data)
        print("Delay:", delay)
        print("Throughput:", throughput)

        if len(clients_data) == 0:
            print("No data found in CSV!")
            return

        os.makedirs("graphs", exist_ok=True)

        plt.figure(figsize=(6,4))
        plt.plot(clients_data, delay, marker="o")
        plt.title("Clients vs Average Delay")
        plt.xlabel("Clients")
        plt.ylabel("Delay (ms)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("graphs/clients_vs_delay.png")
        plt.close()

        plt.figure(figsize=(6,4))
        plt.plot(clients_data, throughput, marker="o")
        plt.title("Clients vs Throughput")
        plt.xlabel("Clients")
        plt.ylabel("Throughput (msg/sec)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("graphs/clients_vs_throughput.png")
        plt.close()

        print("Graphs generated successfully.")

    except Exception as e:
        print("Graph Error:", e)

def handle_client(client,address):
    try:
        username=client.recv(1024).decode().strip()
        usernames[client]=username
        log_event("CONNECTED",username,address[0])
        broadcast(f"*** {username} joined the chat ***")
        while True:
            data=client.recv(1024)
            if not data:
                break
            msg=data.decode().strip()
            log_chat(username,msg)
            print(f"[{username}] {msg}")
            broadcast(f"[{username}] {msg}",client)
    except Exception as e:
        print("Client error:",e)
    finally:
        if client in clients:
            clients.remove(client)
        user=usernames.pop(client,"Unknown")
        log_event("DISCONNECTED",user,address[0])
        broadcast(f"*** {user} left the chat ***")
        try: client.close()
        except: pass

def server_console():
    global running
    while running:
        try:
            cmd=input().strip().lower()
        except EOFError:
            cmd="exit"
        if cmd=="exit":
            print("Saving results...")
            save_results()
            generate_graphs()
            running=False
            for c in clients[:]:
                try:
                    c.send(b"SERVER CLOSED")
                    c.close()
                except:
                    pass
            clients.clear()
            server.close()
            print("Server stopped.")
            os._exit(0)

threading.Thread(target=server_console,daemon=True).start()

while running:
    try:
        client,address=server.accept()
    except OSError:
        break
    clients.append(client)
    threading.Thread(target=handle_client,args=(client,address),daemon=True).start()

print("Server exited.")
