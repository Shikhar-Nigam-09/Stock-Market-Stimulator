import socket, time, random, json

# Multicast group IP and UDP port
GROUP, PORT = "239.1.1.1", 5007
IFACE = "127.0.0.1"   # if nothing arrives, try your Wi-Fi IP here instead

# Create a UDP socket for multicast transmission
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# Set TTL (Time-To-Live) hop limit (2 allows crossing local subnets if routed)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
# Enable loopback so local receivers on the same machine receive the broadcast
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
# Specify outgoing network interface for multicast traffic
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(IFACE))

# Initial stock price baseline
prices = {"RELIANCE": 2900.0, "TCS": 4000.0, "INFY": 1800.0}
seq = 0

# Broadcast market data updates continuously
while True:
    sym = random.choice(list(prices))
    prices[sym] = round(prices[sym] + random.uniform(-1, 1), 2)
    seq += 1
    msg = json.dumps({"seq": seq, "sym": sym, "px": prices[sym], "ts": time.time()})
    if random.random() > 0.05:          # 5% of packets "get lost" on purpose
        sock.sendto(msg.encode(), (GROUP, PORT))
    time.sleep(0.05)                    # about 20 ticks per second
