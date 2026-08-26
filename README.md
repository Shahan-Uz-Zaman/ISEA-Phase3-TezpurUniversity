# ISEA Phase-III – Tezpur University  
### Network Programming Laboratory Assignments

**Student Name:** Shahan Uz Zaman  
**Roll Number:** CS-BTC24-23  
**Institution:** Birangana Sati Sadhani Rajyik Vishwavidyalaya (BSSRV)
**Project:** Information Security Education & Awareness (ISEA) Project – Phase III under Tezpur University 
**Department:** Computer Science & Engineering  

---

## Overview

This repository contains the complete set of practical assignments completed under the **ISEA Phase-III** project at Tezpur University. The assignments progressively cover fundamental to advanced concepts in **network programming**, including:

- TCP socket programming and performance analysis  
- Reliable data transfer over UDP using Stop-and-Wait ARQ  
- Raw socket programming for packet capture and header analysis  
- Multi-threaded concurrent chat servers  
- Advanced chat features (private messaging, history, statistics)  
- GUI-based client application using Tkinter  

All programs were developed, tested, and documented as part of the ISEA internship/assignment requirements.

---

## 📂 Repository Structure

The repository is organized into six laboratory assignments, each focusing on a specific networking concept. Every assignment contains the complete source code, implementation details, execution instructions, screenshots, and supporting documentation.

```text
ISEA-Phase3-TezpurUniversity/
│
├── Assignment-01-Reliable-UDP-Communication/
├── Assignment-02-TCP-Client-Server/
├── Assignment-03-Raw-Socket-Programming/
├── Assignment-04-Multi-Client-Chat-Server/
├── Assignment-05-GUI-Based-Multi-Client-Chat/
├── Assignment-06-Advanced-Multi-Client-Chat-Server/
│
├── README.md
└── LICENSE
```

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python 3 |
| Operating System | Ubuntu Linux |
| Networking | TCP, UDP, Raw Socket Programming |
| GUI Framework | Tkinter |
| Network Emulator | Mininet |
| Packet Analysis | Wireshark |
| Data Storage | CSV |
| Version Control | Git & GitHub |

---

## 📚 Academic Information

| Item | Details |
|------|---------|
| Programme | Information Security Education and Awareness (ISEA) Phase-III |
| Mentoring Institution | Tezpur University |
| Student Institution | Birangana Sati Sadhani Rajyik Vishwavidyalaya (BSSRV) |
| Department | Computer Science & Engineering |
| Domain | Computer Networks & Network Programming |
| Programming Language | Python |

---
# Assignment 1: Reliable UDP Communication using Stop-and-Wait ARQ

## 📌 Overview

This assignment demonstrates the implementation of **Reliable Data Transfer (RDT)** over the **User Datagram Protocol (UDP)** using the **Stop-and-Wait Automatic Repeat reQuest (ARQ)** protocol. Since UDP is a connectionless transport protocol that does not guarantee packet delivery, ordering, or error recovery, an application-layer reliability mechanism is implemented to ensure successful data transmission between a client and a server.

The project simulates reliable communication by incorporating sequence numbers, acknowledgements (ACKs), timeout management, and retransmission of lost packets. Additionally, experiments are conducted under different packet loss conditions using **Mininet**, and the communication statistics are recorded for performance evaluation.

---

## 🎯 Objectives

The primary objectives of this assignment are:

- Understand the limitations of UDP communication.
- Implement reliable communication using the Stop-and-Wait ARQ protocol.
- Develop UDP client and server applications using Python sockets.
- Handle packet loss through timeout and retransmission mechanisms.
- Detect duplicate packets at the receiver.
- Analyze protocol performance under different packet loss conditions.
- Record experimental results for further analysis.

---

## 📚 Learning Outcomes

After completing this assignment, the following concepts are understood:

- UDP Socket Programming
- Connectionless Communication
- Reliable Data Transfer (RDT)
- Stop-and-Wait ARQ Protocol
- Sequence Number Management
- ACK-based Communication
- Timeout Handling
- Packet Retransmission
- Duplicate Packet Detection
- Network Performance Evaluation
- Experimental Analysis using Mininet

---

# 📖 Introduction

The **User Datagram Protocol (UDP)** provides a lightweight communication mechanism with minimal overhead. Unlike TCP, UDP does not establish a connection before transmitting data and provides no guarantee regarding packet delivery, ordering, or integrity.

To overcome these limitations, this assignment implements the **Stop-and-Wait Automatic Repeat reQuest (ARQ)** protocol. In this protocol, the sender transmits one packet at a time and waits for an acknowledgement from the receiver before sending the next packet. If an acknowledgement is not received within a specified timeout interval, the sender retransmits the packet until successful delivery is confirmed.

This approach provides reliable communication while maintaining the simplicity of UDP.

---

# 🏗 System Architecture

```
                 Reliable UDP Communication

                 +----------------------+
                 |      UDP Client      |
                 |     client.py        |
                 +----------+-----------+
                            |
             Packet + Sequence Number
                            |
                            ▼
                   -------------------
                  |      Network      |
                  |   (UDP Channel)   |
                   -------------------
                            |
                            ▼
                 +----------+-----------+
                 |      UDP Server      |
                 |      server.py       |
                 +----------+-----------+
                            |
                      ACK Response
                            |
                            ▲
```

---

# 🌐 Network Topology

```
                 +-------------+
                 |   Switch    |
                 |     s1      |
                 +------+------+
                        |
            -------------------------
            |                       |
        +-------+              +-------+
        |  h1   |              |  h2   |
        |Server |              |Client |
        +-------+              +-------+

Server IP : 10.0.0.1
Client IP : 10.0.0.2
Protocol  : UDP
Port      : 5000
```

---

# ⚙️ Working Principle

The communication process follows the Stop-and-Wait ARQ protocol.

### Step 1

The client creates a UDP socket and initializes the communication.

### Step 2

A packet is generated with a sequence number.

Example

```
SEQ=1 | Hello Server
```

### Step 3

The packet is transmitted to the server.

### Step 4

The client starts a timeout timer and waits for an acknowledgement.

### Step 5

The server receives the packet.

### Step 6

The server checks whether the sequence number has already been received.

- New packet → Process message
- Duplicate packet → Ignore message but send ACK

### Step 7

The server sends an acknowledgement.

```
ACK=1
```

### Step 8

If the acknowledgement reaches the client before timeout:

- Next packet is transmitted.

Otherwise:

- Timeout occurs.
- Packet is retransmitted.

### Step 9

After all packets are delivered successfully, the client sends an **END** message to terminate the communication.

---

# 🔄 Stop-and-Wait ARQ Workflow

```
          Client                           Server

             |                                |
             |------ Packet (SEQ=1) --------->|
             |                                |
             |<----------- ACK 1 -------------|
             |                                |
             |------ Packet (SEQ=2) --------->|
             |                                |
             |<----------- ACK 2 -------------|
             |                                |
             |------ Packet (SEQ=3) --------->|
             |                                |
             |     ACK Lost                  |
             |                                |
      Timeout Occurs                          |
             |                                |
             |---- Retransmit Packet -------->|
             |                                |
             |<----------- ACK 3 -------------|
```

---

# 📂 Project Structure

```
Assignment-01-Reliable-UDP-Communication/
│
├── client.py
├── server.py
├── result_table.csv
├── screenshots/
│   ├── client_output.png
│   ├── server_output.png
│   ├── mininet_network.png
│   └── packet_loss_test.png
│
└── README.md
```

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming Language |
| UDP Socket | Communication |
| Socket Library | Network Programming |
| CSV | Result Storage |
| Mininet | Packet Loss Simulation |
| Ubuntu Linux | Development Environment |

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/Shahan-Uz-Zaman/ISEA-Phase3-TezpurUniversity.git
```

Navigate to the assignment directory

```bash
cd Assignment-01-Reliable-UDP-Communication
```

---

# ▶️ Execution Steps

### Start Mininet

```bash
sudo mn
```

Check network connectivity

```bash
mininet> pingall
```

Start the server

```bash
mininet> h1 python3 server.py
```

Run the client

```bash
mininet> h2 python3 client.py \
--server-ip 10.0.0.1 \
--loss 20 \
--roll 220101234 \
--name "Shahan Uz Zaman"
```

---

# 📊 Performance Metrics

The following parameters are recorded during execution:

- Total Messages Sent
- Total Packets Sent
- Total Retransmissions
- Packet Loss Percentage
- Timeout Value
- Total Transfer Time
- Communication Status

These metrics are automatically stored in `result_table.csv` for future analysis.

---

# 📸 Expected Output

### Client

```
Reliable UDP Client Started

Packet 1 Sent
ACK Received

Packet 2 Sent
Timeout

Retransmitting...

ACK Received

Communication Successful
```

### Server

```
Reliable UDP Server Started

Packet Received

ACK Sent

Duplicate Packet Detected

Communication Completed Successfully
```

---

# 📈 Experimental Analysis

The communication was tested under multiple packet loss conditions using Mininet.

### Observations

- Increasing packet loss increases retransmissions.
- Higher packet loss results in longer communication time.
- Duplicate packets are successfully detected by the receiver.
- Despite packet loss, reliable communication is maintained through retransmission.

---

# ✅ Results

The implementation successfully demonstrates reliable communication over UDP by employing the Stop-and-Wait ARQ protocol. All packets are delivered correctly even under simulated packet loss conditions, validating the effectiveness of acknowledgements, timeout handling, and retransmission mechanisms.

---

# 🚀 Future Enhancements

Future improvements may include:

- Go-Back-N ARQ implementation
- Selective Repeat ARQ
- Sliding Window Protocol
- CRC-based error detection
- Multi-client communication
- Performance visualization using graphs
- GUI-based monitoring dashboard

---

# 🎓 Conclusion

This assignment provides a practical understanding of implementing reliable communication over an unreliable transport protocol. Through the development of Stop-and-Wait ARQ using Python UDP sockets, important networking concepts such as acknowledgements, retransmissions, timeout management, duplicate detection, and protocol performance analysis are explored. The assignment establishes a strong foundation for advanced transport-layer protocols and reliable network application development.

# Assignment 2: TCP Client-Server Communication

## 📌 Overview

This assignment introduces the fundamentals of **TCP (Transmission Control Protocol)** socket programming by implementing a simple client-server communication system using Python. Unlike UDP, TCP is a **connection-oriented** transport layer protocol that guarantees reliable, ordered, and error-free data delivery between communicating hosts.

The project demonstrates how a server listens for incoming client requests, establishes a connection through the TCP three-way handshake, exchanges data reliably, and gracefully terminates the connection. The implementation provides hands-on experience with socket programming concepts and forms the foundation for developing network applications.

---

## 🎯 Objectives

The objectives of this assignment are:

- Understand the architecture of TCP client-server communication.
- Learn how connection-oriented communication works.
- Implement TCP socket programming using Python.
- Establish communication between a client and a server.
- Exchange data reliably over a network.
- Understand the TCP connection establishment and termination process.
- Analyze the performance and behavior of TCP communication.

---

## 📚 Learning Outcomes

Upon successful completion of this assignment, the following concepts are understood:

- TCP Socket Programming
- Client-Server Architecture
- Connection-Oriented Communication
- Three-Way Handshake
- Reliable Data Transmission
- Blocking Socket Operations
- Data Exchange using TCP
- Connection Termination
- Linux Socket Programming
- Network Programming Fundamentals

---

# 📖 Introduction

The **Transmission Control Protocol (TCP)** is one of the most widely used transport layer protocols in computer networks. It provides reliable, connection-oriented communication between two hosts by ensuring that data is delivered completely, in sequence, and without duplication.

Unlike UDP, TCP establishes a dedicated connection before transmitting data. This connection is maintained throughout the communication session and is terminated only after both communicating devices agree to disconnect.

In this assignment, a TCP server continuously listens for incoming client requests. When a client initiates communication, the server accepts the connection, receives the transmitted message, processes it, and sends an appropriate response back to the client.

---

# 🏗 System Architecture

```
                  TCP Client-Server Communication

               +------------------------+
               |      TCP Client        |
               |      client.py         |
               +-----------+------------+
                           |
                    TCP Connection
                           |
                           ▼
                 ---------------------
                |      Network        |
                 ---------------------
                           |
                           ▼
               +-----------+------------+
               |      TCP Server        |
               |      server.py         |
               +------------------------+
```

---

# 🌐 Network Topology

```
                 +-------------+
                 |   Switch    |
                 |     s1      |
                 +------+------+
                        |
            -------------------------
            |                       |
        +-------+              +-------+
        |  h1   |              |  h2   |
        |Server |              |Client |
        +-------+              +-------+

Server IP : 10.0.0.1
Client IP : 10.0.0.2
Protocol  : TCP
Port      : 5000
```

---

# ⚙️ Working Principle

The communication process consists of the following stages:

### Step 1

The server creates a TCP socket.

---

### Step 2

The server binds the socket to an IP address and port number.

```
Server IP : 10.0.0.1
Port      : 5000
```

---

### Step 3

The server starts listening for incoming client requests.

---

### Step 4

The client creates a TCP socket.

---

### Step 5

The client initiates a connection request to the server.

---

### Step 6

TCP performs the **Three-Way Handshake**.

```
Client ---- SYN -----> Server

Client <--- SYN-ACK --- Server

Client ---- ACK -----> Server
```

Once completed, a reliable communication channel is established.

---

### Step 7

The client sends data to the server.

Example

```
Hello Server
```

---

### Step 8

The server receives the data and processes the request.

---

### Step 9

The server sends an acknowledgement or response.

Example

```
Hello Client
```

---

### Step 10

After communication is completed, both client and server terminate the connection gracefully.

---

# 🔄 TCP Communication Workflow

```
          Client                            Server

             |                                 |
             |------ Connection Request ------>|
             |                                 |
             |<------ Connection Accepted ------|
             |                                 |
             |-------- Send Message ----------->|
             |                                 |
             |<------- Receive Response --------|
             |                                 |
             |------ Close Connection --------->|
             |                                 |
```

---

# 🤝 TCP Three-Way Handshake

```
Client                           Server

   |                                |
   |------ SYN -------------------->|
   |                                |
   |<----- SYN + ACK ---------------|
   |                                |
   |------ ACK -------------------->|
   |                                |

TCP Connection Established
```

---

# 📂 Project Structure

```
Assignment-02-TCP-Client-Server/
│
├── client.py
├── server.py
├── screenshots/
│   ├── server_output.png
│   ├── client_output.png
│   ├── network_topology.png
│   └── ping_test.png
│
└── README.md
```

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming Language |
| TCP Socket | Reliable Communication |
| Socket Module | Network Programming |
| Ubuntu Linux | Development Environment |
| Mininet | Network Simulation |
| Wireshark | Packet Analysis |

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/Shahan-Uz-Zaman/ISEA-Phase3-TezpurUniversity.git
```

Navigate to the assignment folder

```bash
cd Assignment-02-TCP-Client-Server
```

---

# ▶️ Execution Steps

### Start Mininet

```bash
sudo mn
```

---

### Verify Network

```bash
mininet> pingall
```

---

### Run the Server

```bash
mininet> h1 python3 server.py
```

Expected Output

```
TCP Server Started
Listening on Port 5000...
```

---

### Run the Client

```bash
mininet> h2 python3 client.py
```

Expected Output

```
Connected to Server

Message Sent Successfully

Response Received

Connection Closed
```

---

# 📊 Performance Analysis

The following aspects are analyzed during execution:

- Successful TCP connection establishment.
- Reliable message delivery.
- Ordered packet transmission.
- Connection termination.
- End-to-end communication delay.
- Network connectivity.

---

# 📸 Expected Output

### Server

```
TCP Server Started

Waiting for Client...

Client Connected

Message Received:
Hello Server

Response Sent

Connection Closed
```

---

### Client

```
TCP Client Started

Connecting to Server...

Connected Successfully

Message Sent

Server Response:
Hello Client

Connection Closed
```

---

# 🔍 Key Features

- Reliable communication
- Connection-oriented protocol
- Error-free data transmission
- Ordered packet delivery
- Automatic retransmission handled by TCP
- Simple client-server architecture
- Easy to understand implementation
- Linux compatible

---

# 📈 Experimental Observations

The implementation demonstrates the following characteristics of TCP:

- Reliable packet delivery.
- Automatic retransmission of lost packets.
- No duplicate data delivery.
- In-order packet reception.
- Connection remains active until explicitly terminated.
- Communication is unaffected by minor packet loss because TCP manages recovery internally.

---

# ✅ Results

The TCP client and server communicate successfully through a reliable connection-oriented channel. The implementation verifies the correctness of socket creation, connection establishment, data exchange, and connection termination while demonstrating the advantages of TCP over connectionless communication.

---

# 🚀 Future Enhancements

Potential improvements include:

- Multiple client support using multithreading.
- File transfer over TCP.
- Chat application implementation.
- Secure communication using SSL/TLS.
- Logging of client activities.
- GUI-based TCP client.
- Performance benchmarking under different network conditions.

---

# 🎓 Conclusion

This assignment provides practical experience in implementing **TCP-based client-server communication** using Python sockets. It demonstrates the complete lifecycle of a TCP connection, including socket creation, connection establishment through the three-way handshake, reliable data exchange, and graceful termination. The assignment builds a strong foundation for developing advanced network applications and understanding reliable transport-layer communication.

# Assignment 3: Raw Socket Programming and Network Packet Analysis

## 📌 Overview

This assignment focuses on the implementation of **Raw Socket Programming** in Python to capture, analyze, and interpret network packets at the IP layer. Unlike TCP and UDP socket programming, raw sockets provide direct access to packet headers, enabling developers to inspect and process network traffic at a much lower level.

The application captures incoming packets, extracts essential header information such as **IP addresses, protocol type, packet length, Time-To-Live (TTL), TCP flags, and port numbers**, and stores the captured data for further analysis. The collected statistics are visualized using graphs to study network behavior and packet characteristics.

This assignment provides practical exposure to packet-level communication and network monitoring techniques commonly used in cybersecurity, intrusion detection systems, and network diagnostics.

---

# 🎯 Objectives

The objectives of this assignment are:

- Understand the concept of Raw Socket Programming.
- Capture network packets directly from the network interface.
- Parse IPv4 packet headers.
- Analyze TCP, UDP, and ICMP packets.
- Extract packet metadata.
- Store captured packet information.
- Generate graphical analysis from captured data.
- Gain practical knowledge of packet inspection tools.

---

# 📚 Learning Outcomes

After completing this assignment, students will be able to:

- Understand Raw Socket Programming.
- Capture packets from a network interface.
- Decode IPv4 packet headers.
- Interpret TCP, UDP, and ICMP headers.
- Understand packet encapsulation.
- Analyze packet size distribution.
- Analyze TTL variation.
- Visualize captured network traffic.
- Use Wireshark for packet verification.
- Develop basic packet analyzer applications.

---

# 📖 Introduction

Network communication occurs through the exchange of packets across interconnected devices. Each packet contains multiple protocol headers that carry addressing information, routing details, transport layer information, and application data.

Normally, operating systems process these headers internally before delivering application data to user programs. However, **Raw Sockets** allow applications to bypass the transport layer abstraction and directly access the complete network packet.

This capability is widely used in:

- Network Monitoring
- Intrusion Detection Systems (IDS)
- Firewalls
- Packet Sniffers
- Traffic Analysis
- Network Diagnostics
- Security Research

In this assignment, a packet sniffer is developed using Python Raw Sockets to capture live network packets, decode protocol headers, and analyze network behavior.

---

# 🏗 System Architecture

```
                     Internet / Local Network
                               │
                               │
                    Incoming Network Packets
                               │
                               ▼
                    +-----------------------+
                    |    Raw Socket Layer   |
                    +-----------+-----------+
                                │
                    Packet Capture Engine
                                │
            -----------------------------------------
            │                 │                    │
            ▼                 ▼                    ▼
      IP Header         TCP/UDP Header      ICMP Header
            │                 │                    │
            -----------------------------------------
                                │
                        Packet Information
                                │
                                ▼
                       CSV Data Storage
                                │
                                ▼
                     Graph Generation Module
```

---

# 🌐 Network Topology

```
                 +-------------+
                 |   Switch    |
                 |     s1      |
                 +------+------+
                        |
          -------------------------------
          |                             |
      +-------+                   +-------+
      |  h1   |                   |  h2   |
      |Sender |                   |Receiver|
      +-------+                   +-------+

Packet Monitoring using Raw Socket
```

---

# ⚙️ Working Principle

The packet analyzer follows the steps below:

### Step 1

Create a Raw Socket.

```python
socket(AF_INET, SOCK_RAW, IPPROTO_TCP)
```

---

### Step 2

Listen for incoming packets continuously.

---

### Step 3

Receive raw packet bytes.

---

### Step 4

Extract IPv4 Header Information.

Information extracted includes:

- Version
- Header Length
- Total Length
- TTL
- Protocol
- Source IP
- Destination IP

---

### Step 5

Determine the transport layer protocol.

Possible protocols include:

- TCP
- UDP
- ICMP

---

### Step 6

Extract transport layer header.

For TCP packets:

- Source Port
- Destination Port
- Sequence Number
- ACK Number
- Window Size
- TCP Flags

---

### Step 7

Store packet information.

Example:

```
Timestamp
Source IP
Destination IP
Protocol
TTL
Packet Size
```

---

### Step 8

Save all captured packets into

```
packet_data.csv
```

---

### Step 9

Generate graphs from captured statistics.

---

# 🔄 Packet Processing Workflow

```
        Start Program
              │
              ▼
      Create Raw Socket
              │
              ▼
      Wait for Packet
              │
              ▼
      Receive Packet
              │
              ▼
      Extract IP Header
              │
              ▼
    Detect Protocol Type
              │
      ┌───────┼─────────┐
      │       │         │
      ▼       ▼         ▼
     TCP     UDP      ICMP
      │       │         │
      └───────┼─────────┘
              ▼
      Extract Header Fields
              │
              ▼
       Store Packet Data
              │
              ▼
       Generate Statistics
              │
              ▼
       Save Graphs & CSV
```

---

# 📂 Project Structure

```
Assignment-03-Raw-Socket-Programming/
│
├── raw_socket.py
├── packet_data.csv
├── graph/
│   ├── ttl.gnu
│   ├── packet_size.gnu
│   ├── ttl_graph.png
│   └── packet_size_graph.png
│
├── screenshots/
│   ├── wireshark_capture.png
│   ├── raw_socket_output.png
│   ├── packet_analysis.png
│   └── graphs.png
│
└── README.md
```

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming Language |
| Raw Socket API | Packet Capture |
| Socket Library | Network Programming |
| Wireshark | Packet Verification |
| CSV | Data Storage |
| GNUPlot | Graph Generation |
| Ubuntu Linux | Development Platform |

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/Shahan-Uz-Zaman/ISEA-Phase3-TezpurUniversity.git
```

Navigate to the assignment directory

```bash
cd Assignment-03-Raw-Socket-Programming
```

---

# ▶️ Execution Steps

Run the packet analyzer

```bash
sudo python3 raw_socket.py
```

Generate graphs

```bash
gnuplot graph/ttl.gnu
```

```bash
gnuplot graph/packet_size.gnu
```

Open generated graphs

```bash
xdg-open graph/ttl_graph.png
```

---

# 📊 Captured Packet Information

The packet analyzer extracts:

| Field | Description |
|--------|-------------|
| Timestamp | Packet arrival time |
| Source IP | Sender IP Address |
| Destination IP | Receiver IP Address |
| Protocol | TCP / UDP / ICMP |
| TTL | Time-To-Live |
| Packet Length | Total packet size |
| Source Port | Sender Port |
| Destination Port | Receiver Port |
| TCP Flags | SYN, ACK, FIN, etc. |

---

# 📈 Performance Analysis

The collected packet information is analyzed using graphs.

The project visualizes:

- Packet Size Variation
- TTL Distribution
- Protocol Distribution
- Packet Arrival Pattern
- Network Traffic Trend

These graphs provide valuable insights into network performance and packet characteristics.

---

# 📸 Expected Output

Console Output

```
Packet Captured

Source IP      : 10.0.0.2
Destination IP : 10.0.0.1
Protocol        : TCP
TTL             : 64
Packet Size     : 74 Bytes

------------------------------------
```

Generated Files

```
packet_data.csv

ttl_graph.png

packet_size_graph.png
```

---

# 🔍 Key Features

- Live packet capture
- IPv4 header analysis
- TCP header decoding
- UDP packet identification
- ICMP packet detection
- CSV logging
- Graph generation
- Wireshark verification
- Packet statistics
- Lightweight implementation

---

# 📈 Experimental Observations

The captured traffic demonstrates:

- Different packet sizes for different protocols.
- TTL values vary depending on routing paths.
- TCP packets dominate during application communication.
- ICMP packets appear during connectivity testing.
- Packet analysis results match Wireshark captures.

---

# ✅ Results

The packet analyzer successfully captures and decodes live network packets using Raw Sockets. The extracted header information is stored in a CSV file and visualized through graphs, enabling detailed analysis of packet characteristics and network traffic behavior. The results closely match those observed in Wireshark, validating the correctness of the implementation.

---

# 🚀 Future Enhancements

Possible future improvements include:

- IPv6 packet support
- DNS packet analysis
- HTTP protocol decoding
- Live graphical dashboard
- Protocol-wise filtering
- Real-time traffic monitoring
- Packet search functionality
- Intrusion detection rules
- Export to JSON format
- Web-based monitoring interface

---

# 🎓 Conclusion

This assignment provides practical experience in **Raw Socket Programming** and low-level network packet analysis. By directly accessing and decoding packet headers, it demonstrates how network monitoring and packet inspection tools operate internally. The implementation enhances understanding of IPv4, TCP, UDP, and ICMP protocols while developing essential skills in packet capture, protocol analysis, network diagnostics, and cybersecurity.

# Assignment 4: Multi-Client Chat Server

## 📌 Overview

This assignment focuses on the development of a **Multi-Client Chat Server** using **TCP Socket Programming** and **Multithreading** in Python. Unlike a basic client-server application where only one client can communicate with the server at a time, this implementation allows multiple clients to connect simultaneously and exchange messages in real time.

The server manages each connected client in a separate thread, enabling concurrent communication without interrupting other active sessions. It also supports broadcasting messages to all connected users, private messaging between individual clients, displaying the list of online users, and maintaining communication logs for monitoring and analysis.

The project demonstrates the practical implementation of concurrent network programming concepts and forms the foundation for scalable real-time communication systems.

---

# 🎯 Objectives

The objectives of this assignment are to:

- Understand concurrent network programming.
- Implement a multi-threaded TCP server.
- Handle multiple client connections simultaneously.
- Broadcast messages to all connected clients.
- Support private messaging between users.
- Display the list of online users.
- Manage client connections dynamically.
- Maintain server-side communication logs.
- Analyze server performance during concurrent communication.

---

# 📚 Learning Outcomes

After completing this assignment, students will be able to:

- Develop concurrent network applications.
- Understand multi-threaded socket programming.
- Manage multiple client connections.
- Implement broadcasting techniques.
- Design private messaging systems.
- Synchronize shared resources.
- Handle client disconnections gracefully.
- Build scalable client-server applications.

---

# 📖 Introduction

Real-world communication platforms such as **WhatsApp**, **Telegram**, **Slack**, and **Microsoft Teams** allow thousands of users to communicate simultaneously. Such systems require servers capable of managing multiple active client connections efficiently.

A **Multi-Client Chat Server** achieves this by creating an independent thread for every connected client. Each thread continuously listens for incoming messages while allowing the server to accept additional client connections.

Whenever a client sends a message, the server determines whether it is a broadcast message or a private message and forwards it to the appropriate recipients. The server also tracks connected users and updates the online user list whenever a client joins or leaves.

This assignment introduces the concepts of concurrent programming, thread management, synchronization, and real-time communication.

---

# 🏗 System Architecture

```
                    +---------------------------+
                    |      Chat Server          |
                    |       server.py          |
                    +------------+-------------+
                                 |
        ---------------------------------------------------
        |                |                |               |
        |                |                |               |
   +---------+      +---------+      +---------+     +---------+
   | Client1 |      | Client2 |      | Client3 |     | Client4 |
   +---------+      +---------+      +---------+     +---------+
```

---

# 🌐 Network Topology

```
                    +-------------+
                    |   Switch    |
                    |     s1      |
                    +------+------+
                           |
      -------------------------------------------------
      |             |             |                  |
  +-------+     +-------+     +-------+         +-------+
  | Client|     | Client|     | Client|         |Server |
  |  h1   |     |  h2   |     |  h3   |         |  h4   |
  +-------+     +-------+     +-------+         +-------+

           TCP Port : 5000
```

---

# ⚙️ Working Principle

The chat server operates using the following sequence:

### Step 1

The server creates a TCP socket.

---

### Step 2

The server binds to a predefined IP address and port.

---

### Step 3

The server starts listening for incoming client connections.

---

### Step 4

Whenever a client connects,

- Accept the connection
- Receive username
- Create a dedicated thread

---

### Step 5

Each client thread continuously performs:

- Receive messages
- Process commands
- Broadcast messages
- Send private messages
- Detect client disconnection

---

### Step 6

When a message is received,

the server determines whether it is:

- Broadcast message
- Private message
- Online user request
- Exit request

---

### Step 7

The server forwards messages to the intended recipients.

---

### Step 8

If a client disconnects,

- Remove the client
- Update online users
- Notify remaining users

---

# 🔄 Server Workflow

```
              Start Server
                    │
                    ▼
            Create TCP Socket
                    │
                    ▼
             Bind IP and Port
                    │
                    ▼
            Wait for Clients
                    │
                    ▼
          Accept Client Connection
                    │
                    ▼
            Receive Username
                    │
                    ▼
        Create Dedicated Thread
                    │
                    ▼
            Wait for Messages
                    │
        ┌───────────┼────────────┐
        │           │            │
        ▼           ▼            ▼
  Broadcast     Private      User List
   Message      Message       Request
        │           │            │
        └───────────┼────────────┘
                    ▼
          Send Response
                    │
                    ▼
          Client Disconnect?
                    │
          Yes ───────────► Remove Client
                    │
                   No
                    │
                    ▼
           Continue Listening
```

---

# 💬 Supported Features

### Broadcast Messaging

Every message sent by a client is delivered to all connected users.

Example:

```
Alice:
Hello Everyone!
```

---

### Private Messaging

A user can send a message to a specific client.

Example

```
/pm Bob Hello
```

Only Bob receives the message.

---

### Online User List

Clients can request the currently connected users.

Example

```
/users
```

Server Response

```
Alice
Bob
Charlie
David
```

---

### Exit

```
/exit
```

The client disconnects safely from the server.

---

# 📂 Project Structure

```
Assignment-04-Multi-Client-Chat-Server/
│
├── server.py
├── client.py
├── chat_log.csv
├── screenshots/
│   ├── server.png
│   ├── client1.png
│   ├── client2.png
│   ├── private_message.png
│   └── online_users.png
│
└── README.md
```

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming Language |
| TCP Socket | Communication |
| Threading | Concurrent Clients |
| CSV | Chat Logging |
| Ubuntu Linux | Development Platform |
| Mininet | Network Testing |

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/Shahan-Uz-Zaman/ISEA-Phase3-TezpurUniversity.git
```

Navigate to the assignment

```bash
cd Assignment-04-Multi-Client-Chat-Server
```

---

# ▶️ Execution Steps

Start the server

```bash
python3 server.py
```

Open multiple terminals.

Run each client.

```bash
python3 client.py
```

Enter username.

Start chatting.

---

# 📊 Features Implemented

- Multi-client communication
- Broadcast messaging
- Private messaging
- Online user list
- Client join notifications
- Client leave notifications
- Concurrent communication
- CSV logging
- Thread management

---

# 📸 Expected Output

### Server

```
Chat Server Started

Waiting for Clients...

Alice Connected

Bob Connected

Charlie Connected

Broadcast Message Received

Private Message Delivered
```

---

### Client

```
Connected Successfully

Enter Username:
Alice

Welcome Alice

Bob:
Hello Everyone!

Charlie:
Hi Alice
```

---

# 📈 Experimental Analysis

The server was tested with multiple concurrent clients.

### Observations

- Multiple clients communicate simultaneously.
- Each client operates independently.
- Messages are delivered without blocking.
- Private messages reach only intended users.
- Online user list updates dynamically.
- Server remains responsive even with multiple active threads.

---

# 🔍 Key Features

- Multi-threaded server
- Concurrent client handling
- Broadcast communication
- Private messaging
- Online user management
- Client join/leave notification
- CSV logging
- Thread-safe communication
- Scalable architecture
- Linux compatible

---

# ✅ Results

The Multi-Client Chat Server successfully enables concurrent communication among multiple clients using TCP sockets and multithreading. The implementation supports broadcasting, private messaging, online user management, and graceful client disconnection while maintaining efficient server performance and reliable message delivery.

---

# 🚀 Future Enhancements

Potential improvements include:

- GUI-based client interface
- End-to-end encryption
- Group chat functionality
- File sharing support
- Voice communication
- User authentication
- Database integration
- Message history
- Emoji support
- WebSocket implementation

---

# 🎓 Conclusion

This assignment demonstrates the practical implementation of a **Multi-Client Chat Server** using Python TCP sockets and multithreading. It provides hands-on experience in concurrent programming, client-server architecture, thread management, and real-time communication. The project establishes a solid foundation for developing scalable messaging systems and advanced distributed network applications.

# Assignment 5: GUI-Based Multi-Client Chat Application

## 📌 Overview

This assignment extends the functionality of the previous Multi-Client Chat Server by introducing a **Graphical User Interface (GUI)** developed using **Python Tkinter**. The objective is to provide an intuitive and user-friendly interface that allows users to communicate with the server without interacting through the command-line terminal.

The application enables multiple users to connect simultaneously to the chat server, exchange messages in real time, send private messages, view the list of connected users, and gracefully disconnect from the server. By integrating **socket programming**, **multithreading**, and **GUI development**, this assignment demonstrates how network applications can be transformed into user-friendly desktop applications.

The GUI continuously listens for incoming messages using a background thread while keeping the interface responsive for user interactions.

---

# 🎯 Objectives

The objectives of this assignment are to:

- Develop a GUI-based chat client using Python Tkinter.
- Connect the GUI client to the Multi-Client Chat Server.
- Enable real-time communication through an interactive interface.
- Support broadcast and private messaging.
- Display online users dynamically.
- Maintain a responsive interface using multithreading.
- Improve usability compared to command-line applications.

---

# 📚 Learning Outcomes

After completing this assignment, students will be able to:

- Design GUI applications using Tkinter.
- Integrate socket programming with graphical interfaces.
- Implement background threads in GUI applications.
- Handle asynchronous message reception.
- Build interactive network applications.
- Design user-friendly communication systems.
- Understand event-driven programming concepts.

---

# 📖 Introduction

Command-line applications are useful for understanding networking concepts but provide limited user interaction. Modern communication systems require graphical interfaces that simplify user interaction while maintaining real-time communication.

This assignment develops a **GUI-Based Chat Client** that communicates with the previously developed Multi-Client Chat Server. The application provides text fields, buttons, message display windows, and user management features, making the chat application more interactive and easier to use.

To avoid freezing the graphical interface while waiting for incoming messages, a dedicated background thread continuously listens for server messages, allowing the GUI to remain responsive throughout the communication session.

---

# 🏗 System Architecture

```
                    GUI-Based Chat Application

              +-----------------------------+
              |      Chat Server            |
              |        server.py            |
              +-------------+---------------+
                            |
        ---------------------------------------------
        |                   |                      |
        |                   |                      |
 +--------------+   +--------------+      +--------------+
 | GUI Client 1 |   | GUI Client 2 |      | GUI Client 3 |
 |  Tkinter     |   |  Tkinter     |      |  Tkinter     |
 +--------------+   +--------------+      +--------------+
```

---

# 🌐 Network Topology

```
                   +--------------+
                   |    Switch    |
                   |      s1      |
                   +------+-------+
                          |
      -----------------------------------------------
      |               |               |             |
 +---------+     +---------+     +---------+   +---------+
 | Client1 |     | Client2 |     | Client3 |   | Server  |
 |  GUI    |     |  GUI    |     |  GUI    |   |         |
 +---------+     +---------+     +---------+   +---------+

Protocol : TCP
Port     : 5000
```

---

# ⚙️ Working Principle

The application performs the following operations:

### Step 1

The user launches the GUI application.

---

### Step 2

The user enters:

- Username
- Server IP Address
- Port Number

---

### Step 3

The application creates a TCP socket and connects to the server.

---

### Step 4

A background thread starts listening for incoming messages.

---

### Step 5

Whenever the user types a message,

- Read message from input box.
- Send message to server.
- Clear input field.

---

### Step 6

Whenever the server sends a message,

- Receive message.
- Display message inside the chat window.
- Continue listening.

---

### Step 7

The application supports:

- Broadcast Messaging
- Private Messaging
- Online User List
- Exit

---

### Step 8

When the user exits,

- Socket closes.
- GUI terminates safely.

---

# 🔄 Application Workflow

```
             Start Application
                     │
                     ▼
              Open GUI Window
                     │
                     ▼
         Enter Username & Server IP
                     │
                     ▼
             Connect to Server
                     │
                     ▼
         Start Background Thread
                     │
         ┌───────────┼────────────┐
         │                        │
         ▼                        ▼
 Receive Messages          Send Messages
         │                        │
         ▼                        ▼
 Display Chat             Update Chat Window
         │                        │
         └───────────┬────────────┘
                     ▼
             Continue Chatting
                     │
                     ▼
              Disconnect & Exit
```

---

# 🖥 GUI Components

The graphical interface contains:

### Login Window

- Username
- Server IP
- Port Number
- Connect Button

---

### Chat Window

- Chat Display Area
- Message Input Box
- Send Button
- Online Users Button
- Exit Button

---

### User Information

- Connected Username
- Server Status
- Connection Status

---

# 💬 Features

### Broadcast Messaging

Messages are delivered to every connected client.

Example

```
Alice:
Hello Everyone!
```

---

### Private Messaging

Users can send messages privately.

Example

```
/pm Bob Hello
```

---

### Online User List

Displays all active users.

Example

```
Online Users

Alice
Bob
Charlie
David
```

---

### Real-Time Updates

Incoming messages automatically appear in the chat window without interrupting user interaction.

---

# 📂 Project Structure

```
Assignment-05-GUI-Based-Multi-Client-Chat/
│
├── client_gui.py
├── server.py
├── assets/
│   ├── logo.png
│   └── icon.ico
│
├── screenshots/
│   ├── login_window.png
│   ├── chat_window.png
│   ├── private_chat.png
│   ├── online_users.png
│   └── group_chat.png
│
└── README.md
```

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming Language |
| Tkinter | GUI Development |
| TCP Socket | Network Communication |
| Threading | Background Message Reception |
| Ubuntu Linux | Development Platform |
| Git | Version Control |

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/Shahan-Uz-Zaman/ISEA-Phase3-TezpurUniversity.git
```

Navigate to the assignment folder

```bash
cd Assignment-05-GUI-Based-Multi-Client-Chat
```

---

# ▶️ Execution Steps

Start the chat server

```bash
python3 server.py
```

Open another terminal.

Launch the GUI client

```bash
python3 client_gui.py
```

Enter

- Username
- Server IP
- Port

Click

```
Connect
```

Begin chatting.

---

# 📸 Expected GUI

### Login Window

```
--------------------------------
        Chat Application

 Username : ___________

 Server IP: ___________

 Port     : ___________

 [ Connect ]
--------------------------------
```

---

### Chat Window

```
----------------------------------------------

 Connected as Alice

 ------------------------------------------

 Bob :
 Hello Alice

 Alice :
 Hi Bob

 ------------------------------------------

 Message:

 _____________________________

 [ Send ]

----------------------------------------------
```

---

# 📊 Features Implemented

- GUI Login Screen
- Chat Window
- Broadcast Messaging
- Private Messaging
- Online User List
- Background Message Listener
- Responsive Interface
- Graceful Exit
- Multi-user Support

---

# 📈 Experimental Analysis

The GUI application was tested with multiple simultaneous users.

### Observations

- GUI remains responsive during communication.
- Background thread continuously receives messages.
- Messages are displayed instantly.
- Private messaging functions correctly.
- User interface improves usability significantly.
- Multiple GUI clients communicate successfully with the server.

---

# 🔍 Key Features

- User-friendly interface
- Responsive GUI
- Real-time communication
- Multi-client support
- Broadcast messaging
- Private messaging
- Online user management
- Background threading
- Easy connection management
- Cross-platform Python implementation

---

# ✅ Results

The GUI-Based Multi-Client Chat Application successfully integrates **Tkinter**, **TCP socket programming**, and **multithreading** to provide an interactive desktop chat application. Users can communicate efficiently through a graphical interface while maintaining all networking functionalities developed in the previous assignments.

---

# 🚀 Future Enhancements

Possible improvements include:

- Dark Mode support
- Emoji integration
- File sharing
- Image sharing
- Voice messaging
- Video calling
- User authentication
- Chat history storage
- Database integration
- End-to-end encryption
- Notification sounds
- Custom themes

---

# 🎓 Conclusion

This assignment demonstrates the development of a **GUI-Based Multi-Client Chat Application** using Python Tkinter and TCP socket programming. The project combines networking concepts with graphical user interface design to create a responsive and user-friendly communication platform. It enhances practical understanding of event-driven programming, multithreading, GUI development, and real-time client-server communication, serving as a stepping stone toward building modern desktop messaging applications.

# Assignment 6: Advanced Multi-Client Chat Server

## 📌 Overview

This assignment presents the implementation of an **Advanced Multi-Client Chat Server**, extending the functionality developed in the previous assignments. The application provides a robust and scalable client-server communication system capable of handling multiple concurrent users while offering advanced messaging features such as **broadcast communication, private messaging, online user management, chat history, server statistics, and activity logging**.

The server is designed using **TCP Socket Programming** and **Multithreading**, where each connected client is managed through an independent thread. The application emphasizes concurrency, synchronization, efficient resource management, and reliable message delivery, making it suitable for understanding the architecture of modern real-time communication platforms.

This assignment integrates the networking concepts learned throughout the course and demonstrates how advanced communication systems are designed and implemented.

---

# 🎯 Objectives

The objectives of this assignment are to:

- Develop an advanced multi-client chat server using Python.
- Handle multiple simultaneous client connections efficiently.
- Implement real-time broadcast messaging.
- Enable secure private messaging between users.
- Display active users connected to the server.
- Maintain server-side chat history and activity logs.
- Generate communication statistics.
- Improve server scalability and reliability.
- Understand concurrent programming and thread synchronization.

---

# 📚 Learning Outcomes

After completing this assignment, students will be able to:

- Design scalable client-server architectures.
- Implement multithreaded network servers.
- Synchronize shared resources between threads.
- Manage concurrent client sessions.
- Develop advanced messaging features.
- Maintain communication logs.
- Generate server statistics.
- Handle unexpected client disconnections gracefully.
- Understand real-time communication systems.

---

# 📖 Introduction

Real-time messaging platforms require servers capable of handling numerous users simultaneously while ensuring reliable communication, low latency, and efficient resource management. Such applications rely heavily on concurrent programming techniques and efficient client management.

The **Advanced Multi-Client Chat Server** enhances the basic chat server by introducing several additional capabilities including:

- Multiple concurrent clients
- Broadcast communication
- Private messaging
- Online user management
- Chat history
- Server logging
- User activity monitoring
- Communication statistics

The implementation demonstrates how modern messaging applications manage multiple users and maintain continuous communication between distributed clients.

---

# 🏗 System Architecture

```
                 Advanced Multi-Client Chat System

                   +---------------------------+
                   |    Chat Server           |
                   |      server.py          |
                   +------------+------------+
                                |
     ---------------------------------------------------------
     |             |              |              |            |
+---------+   +---------+   +---------+   +---------+   +---------+
| Client1 |   | Client2 |   | Client3 |   | Client4 |   | Client5 |
+---------+   +---------+   +---------+   +---------+   +---------+
      |             |              |              |            |
      ---------------------------------------------------------
                                |
                  Message Processing & Routing
```

---

# 🌐 Network Topology

```
                    +---------------+
                    |     Switch    |
                    |      s1       |
                    +-------+-------+
                            |
---------------------------------------------------------------
|            |             |             |                   |
|            |             |             |                   |
Client 1   Client 2     Client 3     Client 4            Server

Protocol : TCP
Port     : 5000
```

---

# ⚙️ Working Principle

The server operates according to the following workflow.

### Step 1

The server creates a TCP socket.

---

### Step 2

The socket is bound to the specified IP address and port.

---

### Step 3

The server starts listening for incoming client requests.

---

### Step 4

Whenever a client connects:

- Accept connection
- Receive username
- Register client
- Create dedicated communication thread

---

### Step 5

Each client thread continuously listens for incoming messages.

---

### Step 6

The server identifies the message type.

Supported operations include:

- Broadcast Message
- Private Message
- Online User Request
- Chat History Request
- Server Statistics Request
- Client Exit

---

### Step 7

The server processes the request and forwards the appropriate response.

---

### Step 8

Whenever a client disconnects:

- Remove client
- Update online user list
- Notify remaining users
- Save activity log

---

# 🔄 Server Workflow

```
                 Start Server
                       │
                       ▼
              Create TCP Socket
                       │
                       ▼
               Bind IP and Port
                       │
                       ▼
            Wait for Client Request
                       │
                       ▼
              Accept Connection
                       │
                       ▼
             Receive Username
                       │
                       ▼
           Create Client Thread
                       │
                       ▼
             Wait for Messages
                       │
       ┌───────────────┼─────────────────┐
       │               │                 │
       ▼               ▼                 ▼
 Broadcast        Private Chat      User Commands
       │               │                 │
       └───────────────┼─────────────────┘
                       ▼
            Update Server Log
                       │
                       ▼
             Send Appropriate Reply
                       │
                       ▼
          Client Disconnect?
                 │
          Yes ───────► Remove Client
                 │
                No
                 │
                 ▼
         Continue Communication
```

---

# 💬 Features Implemented

## Broadcast Messaging

Messages are delivered to all connected clients.

Example

```
Alice:
Good Morning Everyone!
```

---

## Private Messaging

Allows communication between specific users.

Example

```
/pm Bob Meeting at 3 PM
```

---

## Online User List

Displays all currently connected users.

Example

```
/users
```

Output

```
Alice
Bob
Charlie
David
```

---

## Chat History

Displays previously exchanged messages.

Example

```
/history
```

---

## Server Statistics

Displays communication statistics.

Example

```
/stats
```

Output

```
Connected Users : 5

Messages Sent : 258

Private Messages : 42

Broadcast Messages : 216
```

---

## Client Exit

Safely disconnects from the server.

```
/exit
```

---

# 📂 Project Structure

```
Assignment-06-Advanced-Multi-Client-Chat-Server/
│
├── server.py
├── client.py
├── chat_history.csv
├── server_log.csv
├── statistics.csv
│
├── screenshots/
│   ├── server_console.png
│   ├── multiple_clients.png
│   ├── broadcast_message.png
│   ├── private_message.png
│   ├── chat_history.png
│   ├── online_users.png
│   └── statistics.png
│
└── README.md
```

---

# 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Programming Language |
| TCP Socket | Reliable Communication |
| Threading | Concurrent Client Handling |
| CSV | Chat History & Logs |
| Ubuntu Linux | Development Platform |
| Git & GitHub | Version Control |

---

# 💻 Installation

Clone the repository

```bash
git clone https://github.com/Shahan-Uz-Zaman/ISEA-Phase3-TezpurUniversity.git
```

Navigate to the project directory

```bash
cd Assignment-06-Advanced-Multi-Client-Chat-Server
```

---

# ▶️ Execution Steps

Start the server

```bash
python3 server.py
```

Open multiple terminals.

Run the client application.

```bash
python3 client.py
```

Enter your username.

Begin communication using the supported commands.

---

# 📝 Supported Commands

| Command | Description |
|----------|-------------|
| `/users` | Display online users |
| `/pm <username> <message>` | Send private message |
| `/history` | Display chat history |
| `/stats` | View server statistics |
| `/exit` | Disconnect from server |

---

# 📊 Features Implemented

- Multi-threaded Server
- Multiple Concurrent Clients
- Broadcast Messaging
- Private Messaging
- Online User Management
- Chat History
- Activity Logging
- Server Statistics
- Graceful Client Disconnection
- Thread Synchronization

---

# 📸 Expected Output

### Server Console

```
Advanced Chat Server Started

Waiting for Client Connections...

Alice Connected

Bob Connected

Charlie Connected

Broadcast Message Sent

Private Message Delivered

Client Disconnected
```

---

### Client Console

```
Connected Successfully

Welcome Alice

Bob:
Hello Alice

Charlie:
Good Morning

/users

Alice
Bob
Charlie

/history

Conversation Loaded Successfully
```

---

# 📈 Performance Analysis

The application was evaluated using multiple concurrent client connections.

### Observations

- Multiple users communicate simultaneously without blocking.
- Dedicated threads ensure smooth communication.
- Broadcast messages reach all connected users instantly.
- Private messages are delivered only to intended recipients.
- Online user list updates automatically.
- Chat history and server statistics improve monitoring capabilities.
- Server remains stable during continuous communication.

---

# 🔍 Key Features

- Concurrent Client Management
- Real-Time Communication
- Broadcast Messaging
- Private Messaging
- Online User List
- Chat History
- Server Statistics
- Activity Logging
- Thread Synchronization
- Scalable Architecture

---

# ✅ Results

The Advanced Multi-Client Chat Server successfully supports concurrent communication among multiple users while providing advanced messaging features and efficient client management. The implementation demonstrates reliable message delivery, effective thread handling, server logging, and real-time communication, making it a comprehensive example of modern client-server network application development.

---

# 🚀 Future Enhancements

Future improvements may include:

- User Authentication
- Password Encryption
- End-to-End Encryption
- Group Chat Management
- File Sharing
- Image and Video Transfer
- Voice Communication
- Database Integration
- WebSocket Support
- Cloud Deployment
- Mobile Client Application
- AI-Based Chat Moderation

---

# 🎓 Conclusion

This assignment represents the culmination of the Network Programming laboratory by integrating **TCP Socket Programming**, **Multithreading**, **Concurrent Client Management**, and **Advanced Messaging Features** into a complete communication platform. The project demonstrates the principles behind real-world messaging systems, emphasizing scalability, reliability, and efficient resource management. It provides practical experience in designing robust network applications and establishes a strong foundation for developing enterprise-level communication systems and distributed applications.


---

# Assignment 7: Secure Multi-Client Chat Application

## 📌 Overview

This assignment extends the Advanced Multi-Client Chat Server developed in Assignment 6 by adding practical security mechanisms. The existing TCP multi-client architecture was retained and enhanced with **user registration, authentication, password hashing, input validation, duplicate-login prevention, failed-login protection, session management, logout, and security logging**.

A GUI-based client is used for user interaction, while the server manages authentication and multiple concurrent TCP connections. The application also uses Wireshark to verify TCP communication during login, failed login, authenticated communication, and logout.

---

## 🎯 Objectives

The objectives of this assignment are to:

- Add secure user registration and authentication.
- Implement a Sign Up option in the GUI client.
- Store passwords as SHA-256 hashes instead of plain text.
- Prevent duplicate active logins.
- Validate usernames, passwords, commands, and messages.
- Protect against repeated failed login attempts.
- Manage authenticated user sessions.
- Implement secure logout and inactivity timeout.
- Maintain security logs without storing passwords.
- Verify TCP communication using Wireshark.

---

## 📚 Learning Outcomes

After completing this assignment, the following concepts are understood:

- User Authentication
- User Registration
- Password Hashing
- SHA-256
- Input Validation
- Session Management
- Duplicate Login Prevention
- Failed Login Protection
- Security Logging
- TCP Security Testing
- Wireshark Packet Analysis

---

## 🏗 System Architecture

```text
                  +-------------------------+
                  |       TCP Server        |
                  |       Port 5000         |
                  +-----------+-------------+
                              |
                +-------------+-------------+
                |             |             |
                ▼             ▼             ▼
          +---------+   +---------+   +---------+
          | Client1 |   | Client2 |   | Client3 |
          | Tkinter |   | Tkinter |   | Tkinter |
          +---------+   +---------+   +---------+
                \             |             /
                 \            |            /
                  +-----------+-----------+
                              |
                       Authentication
                              |
                    +---------+---------+
                    |                   |
                    ▼                   ▼
                users.csv       security_log.txt
```

### Security Data Flow

```text
Password
   │
   ▼
SHA-256 Hash
   │
   ▼
users.csv

Login / Logout / Failed Login
   │
   ▼
security_log.txt
```

---

## 🔐 Security Features Implemented

### 1. User Registration

A **Sign Up** option was added to the GUI client. A new user provides a username and password, and the server checks whether the username already exists.

Successful registration allows the user to log in using the same credentials.

### 2. Password Hashing

Passwords are not stored as plain text. The server uses SHA-256 hashing before storing credentials.

```text
Plain Password
      ↓
   SHA-256
      ↓
Password Hash
      ↓
users.csv
```

### 3. Authentication

During login, the submitted password is hashed and compared with the stored hash.

```text
Username + Password
        ↓
   Authentication
        ↓
 ┌──────┴──────┐
 ▼             ▼
Success       Failure
```

### 4. Duplicate Login Prevention

The server maintains active sessions and prevents the same username from creating multiple simultaneous authenticated sessions.

### 5. Input Validation

The server validates:

- Username format
- Password length
- Empty messages
- Unsupported commands
- Message length
- Invalid private-message targets

### 6. Failed Login Protection

Repeated failed login attempts are tracked. After the configured number of failed attempts, the account is temporarily blocked.

### 7. Session Management

Authenticated sessions are tracked by the server. Logout and inactivity timeout remove inactive clients and release their resources.

### 8. Security Logging

Important security events are recorded in:

```text
security_log.txt
```

Examples include:

- Successful login
- Failed login
- Account registration
- Logout
- Blocked login attempts

Passwords are never written to the security log.

---

## ⚙️ Working Principle

```text
                 Start Client
                      │
                      ▼
                 Sign Up / Login
                      │
             ┌────────┴────────┐
             │                 │
          Sign Up             Login
             │                 │
             ▼                 ▼
       Create Account     Verify Credentials
             │                 │
             └────────┬────────┘
                      ▼
                Authentication
                      │
               ┌──────┴──────┐
               │             │
             Valid         Invalid
               │             │
               ▼             ▼
          Enter Chat      Reject/Login
               │
               ▼
       Broadcast / Private
               │
               ▼
          Logout / Timeout
               │
               ▼
         Session Cleanup
```

---

## 📂 Project Structure

```text
Assignment-07-Secure-Multi-Client-Chat/
│
├── server.py
├── client_gui.py
├── users.csv
├── security_log.txt
├── chat_history.csv
├── config.json
│
├── screenshots/
│   ├── signup.png
│   ├── successful_login.png
│   ├── failed_login.png
│   ├── chat.png
│   ├── logout.png
│   └── wireshark_capture.png
│
└── README.md
```

---

## 🛠 Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Application Development |
| TCP Socket | Client-Server Communication |
| Tkinter | GUI Client |
| SHA-256 | Password Hashing |
| CSV | Credential and Data Storage |
| Wireshark | Network Verification |
| Ubuntu Linux | Development Platform |
| Git & GitHub | Version Control |

---

## ▶️ Execution Steps

### Start the Server

```bash
python3 server.py
```

The server listens on TCP port:

```text
5000
```

### Start the GUI Client

```bash
python3 client_gui.py
```

### Create an Account

1. Enter a username.
2. Enter a password.
3. Click **Sign Up**.
4. Wait for the registration-success message.
5. Use the same credentials to log in.

---

## 🧪 Security Testing

| Test Case | Expected Result |
|-----------|-----------------|
| New username registration | Account created |
| Existing username registration | Registration rejected |
| Correct credentials | Login successful |
| Incorrect password | Login rejected |
| Repeated failed login | Temporary account blocking |
| Duplicate active login | Second login rejected |
| Empty username | Rejected |
| Empty password | Rejected |
| Invalid message | Rejected |
| Logout | Session terminated |
| Inactivity timeout | Session removed |

---

## 📡 Wireshark Verification

Wireshark was used to verify TCP traffic generated by the application.

### Display Filter

```text
tcp.port == 5000
```

The following scenarios were captured:

1. Successful login
2. Failed login
3. Authenticated chat communication
4. Logout
5. TCP connection establishment and termination

### Screenshots

Recommended screenshots:

```text
screenshots/
├── successful_login_wireshark.png
├── failed_login_wireshark.png
├── authenticated_communication.png
└── logout_wireshark.png
```

---

## 📊 Results

The secure chat application successfully integrates authentication and security controls with the existing multi-client TCP communication system.

The implementation provides:

- Secure account registration
- Password hashing
- Authenticated sessions
- Duplicate-login prevention
- Failed-login protection
- Input validation
- Session timeout
- Security logging
- Multi-client communication
- Wireshark-verifiable TCP traffic

---

## 🎓 Conclusion

Assignment 7 successfully transforms the previous multi-client chat application into a more secure network application. The project demonstrates how authentication, password hashing, validation, session management, and security logging can be integrated without redesigning the existing TCP communication architecture.

The assignment provides practical experience in securing network applications and verifying their behavior using Wireshark.

---

# Assignment 8: Application Optimization, Scalability and Reliability

## 📌 Overview

Assignment 8 extends the secure multi-client chat application developed in Assignment 7. The main focus is **connection management, reliability, scalability, configuration management, and performance evaluation**.

The existing communication protocol and security features are retained. The server and client are optimized to handle multiple concurrent clients, recover from network failures, clean up disconnected sessions, and use configurable runtime parameters.

Performance is evaluated using **5, 8, and 10 concurrent clients**, with measurements for delay, throughput, CPU usage, and memory usage.

---

## 🎯 Objectives

The objectives of this assignment are to:

- Improve client connection management.
- Detect and clean up disconnected clients.
- Implement socket timeout handling.
- Add automatic client reconnection.
- Implement graceful server shutdown.
- Improve exception handling.
- Support at least 10 concurrent clients.
- Improve thread management.
- Move configurable values to `config.json`.
- Measure application performance.
- Compare baseline and optimized implementations.
- Generate performance graphs.
- Verify TCP communication using Wireshark.

---

## 📚 Learning Outcomes

After completing this assignment, the following concepts are understood:

- Connection Management
- Socket Timeout
- Automatic Reconnection
- Graceful Shutdown
- Exception Handling
- Thread Pool Management
- Concurrent Client Scalability
- Configuration Management
- Performance Benchmarking
- CPU and Memory Analysis
- Network Delay and Throughput
- Wireshark Verification

---

## 🏗 Optimized System Architecture

```text
                         +----------------------+
                         |     TCP Server       |
                         |      Port 5000       |
                         +----------+-----------+
                                    |
                         ThreadPoolExecutor
                                    |
          +------------+------------+------------+
          |            |            |            |
          ▼            ▼            ▼            ▼
      Client 1     Client 2     Client 3     ... Client 10
       Tkinter      Tkinter      Tkinter          Tkinter
          |            |            |                |
          +------------+------------+----------------+
                                    |
                           Connection Management
                                    |
                +-------------------+-------------------+
                |                   |                   |
                ▼                   ▼                   ▼
          Authentication      Session Manager      Cleanup
                |                   |                   |
                ▼                   ▼                   ▼
           users.csv        Timeout/Reconnect      Security Log
```

---

## 🔧 Major Improvements

### 1. Connection Management

The server now detects disconnected clients and removes stale sessions.

When a client disconnects:

```text
Client Disconnect
      ↓
Detect Socket Error / Close
      ↓
Close Socket
      ↓
Remove Client
      ↓
Remove Username Mapping
      ↓
Notify Remaining Clients
      ↓
Write Log Entry
```

This prevents stale connections and unnecessary resource usage.

### 2. Automatic Reconnection

The GUI client attempts to reconnect when the TCP connection is unexpectedly lost.

```text
Connection Lost
      ↓
Reconnect Attempt 1
      ↓
Reconnect Attempt 2
      ↓
Reconnect Attempt 3
      ↓
...
      ↓
Connection Restored
```

### 3. Socket Timeout

Timeout values prevent network operations from blocking indefinitely.

### 4. Graceful Shutdown

The server handles shutdown signals and closes active sockets and worker resources before terminating.

### 5. Improved Exception Handling

Network errors such as:

```text
ConnectionResetError
ConnectionAbortedError
BrokenPipeError
TimeoutError
OSError
```

are handled without crashing the complete server.

---

## 🚀 Scalability Improvement

A controlled thread pool is used for client handling.

```python
ThreadPoolExecutor
```

The number of workers is configurable rather than creating unlimited threads.

The application is tested with:

```text
5 Clients
8 Clients
10 Clients
```

The target is to maintain stable communication without application crashes while handling at least 10 concurrent clients.

---

## ⚙️ Configuration Management

Runtime parameters are stored in:

```text
config.json
```

Example:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "backlog": 20,
    "max_workers": 10,
    "socket_timeout": 5,
    "shutdown_timeout": 5
  },
  "security": {
    "users_file": "users.csv",
    "security_log_file": "security_log.txt",
    "session_timeout": 300,
    "lockout_duration": 60,
    "max_failed_attempts": 5
  },
  "application": {
    "history_file": "chat_history.csv",
    "performance_file": "performance_results.csv",
    "buffer_size": 4096,
    "max_message_length": 1000,
    "max_clients": 10
  }
}
```

This makes the application easier to configure and maintain without modifying the main source code.

---

## 📂 Project Structure

```text
Assignment-08-Optimization-Scalability/
│
├── server.py
├── client_gui.py
├── config.json
├── users.csv
├── security_log.txt
├── chat_history.csv
│
├── benchmark.py
├── generate_graphs.py
├── performance_results.csv
│
├── graphs/
│   ├── delay_comparison.png
│   ├── throughput_comparison.png
│   ├── cpu_comparison.png
│   └── memory_comparison.png
│
├── screenshots/
│   ├── mininet_topology.png
│   ├── five_clients.png
│   ├── eight_clients.png
│   ├── ten_clients.png
│   └── wireshark_capture.png
│
└── README.md
```

---

## 🌐 Mininet Testing

The required Mininet topology is:

```bash
sudo mn --topo single,11
```

The topology provides one switch and sufficient hosts for the 10-client experiment.

### Verify Nodes

```bash
mininet> nodes
```

### Verify Network

```bash
mininet> net
```

### Test Connectivity

```bash
mininet> pingall
```

The application is evaluated using:

```text
5 concurrent clients
8 concurrent clients
10 concurrent clients
```

---

## 📊 Performance Evaluation

A benchmarking program is used to collect actual experimental results.

The measurements include:

- Average delay
- Throughput
- CPU utilization
- Memory utilization
- Number of clients
- Number of messages
- Errors
- Test duration

Results are stored in:

```text
performance_results.csv
```

### Example Commands

```bash
python3 benchmark.py --clients 5 --mode baseline
python3 benchmark.py --clients 8 --mode baseline
python3 benchmark.py --clients 10 --mode baseline
```

For the optimized implementation:

```bash
python3 benchmark.py --clients 5 --mode optimized
python3 benchmark.py --clients 8 --mode optimized
python3 benchmark.py --clients 10 --mode optimized
```

Graphs can then be generated using:

```bash
python3 generate_graphs.py
```

---

## 📈 Performance Result Table

The final experimental values should be filled using the actual benchmark output.

| Clients | Average Delay (ms) | Throughput (msg/s) | CPU (%) | Memory (MB) |
|---------:|-------------------:|--------------------:|--------:|------------:|
| 5 | ___ | ___ | ___ | ___ |
| 8 | ___ | ___ | ___ | ___ |
| 10 | ___ | ___ | ___ | ___ |

### Generated Graphs

```text
graphs/
├── delay_comparison.png
├── throughput_comparison.png
├── cpu_comparison.png
└── memory_comparison.png
```

The graphs compare the baseline Assignment 7 implementation with the optimized Assignment 8 implementation.

---

## 📡 Wireshark Verification

Wireshark is used to verify normal TCP communication after optimization.

### Display Filter

```text
tcp.port == 5000
```

The following traffic can be captured:

- TCP connection establishment
- Client-server communication
- Chat messages
- Client disconnection
- Connection termination

Recommended screenshot:

```text
screenshots/wireshark_capture.png
```

---

## 🧪 Reliability Testing

| Test Case | Expected Result |
|-----------|-----------------|
| Normal connection | Client connects successfully |
| Client closes normally | Server cleans up session |
| Sudden client disconnect | Server detects and removes client |
| Temporary network failure | Client attempts reconnection |
| Socket timeout | Operation does not block indefinitely |
| Server shutdown | Resources are released gracefully |
| 5 clients | Stable communication |
| 8 clients | Stable communication |
| 10 clients | Stable communication |

---

## 📈 Performance Analysis

The Assignment 8 optimization is evaluated by comparing the original and optimized implementations.

The analysis should consider:

- Whether delay increases as client count increases.
- Whether throughput remains stable.
- CPU usage under concurrent connections.
- Memory consumption as clients increase.
- Number of errors or failed connections.
- Stability during the 10-client test.

Actual experimental values should be used in the final report rather than estimated values.

---

## 🔍 Key Features

- Secure User Authentication
- User Registration
- SHA-256 Password Hashing
- Duplicate Login Prevention
- Failed Login Protection
- Session Timeout
- Multi-Client TCP Communication
- Automatic Reconnection
- Connection Cleanup
- Socket Timeout
- Graceful Shutdown
- Thread Pool Management
- Configurable Runtime Parameters
- Performance Benchmarking
- CPU and Memory Monitoring
- Wireshark Verification
- Mininet Scalability Testing

---

## ✅ Results

Assignment 8 extends the secure chat application with improved reliability and scalability. The optimized server is designed to manage multiple concurrent clients using controlled worker threads while handling disconnections and network failures safely.

The configuration system simplifies deployment and testing, while the benchmarking tools provide a structured way to measure delay, throughput, CPU usage, and memory usage for 5, 8, and 10 clients.

---

## 🚀 Future Enhancements

Possible future improvements include:

- Database-backed authentication
- Stronger password hashing such as Argon2 or bcrypt
- TLS/SSL encrypted communication
- Distributed server architecture
- Load balancing
- Redis-based session management
- WebSocket support
- Cloud deployment
- Docker and Kubernetes deployment
- Real-time monitoring dashboard
- Advanced performance monitoring
- Automated load testing

---

## 🎓 Conclusion

Assignment 8 successfully extends the secure multi-client TCP chat application by improving **connection management, reliability, scalability, configuration, and performance evaluation**. Automatic reconnection, timeout handling, graceful shutdown, resource cleanup, controlled thread management, and centralized configuration make the application more robust and maintainable.

Testing with 5, 8, and 10 concurrent clients provides a practical basis for evaluating scalability. Performance measurements and Wireshark verification further demonstrate how the optimized network application behaves under increasing client load.

Together, Assignments 7 and 8 transform the earlier chat application into a more secure, reliable, configurable, and scalable network application.
