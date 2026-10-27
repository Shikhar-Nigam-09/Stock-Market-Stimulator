import socket, struct, json, time, sys

# Multicast group IP and UDP port matching publisher
GROUP, PORT = "239.1.1.1", 5007
IFACE = "127.0.0.1"                     # keep same as publisher
name = sys.argv[1] if len(sys.argv) > 1 else "server"

# Create UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# Allow multiple sockets/receivers to bind to the exact same port
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
if hasattr(socket, "SO_REUSEPORT"):     # needed on macOS/Linux for 2 receivers
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
sock.bind(("", PORT))

# This is the "subscribe" step (IGMP join)
mreq = struct.pack("4s4s", socket.inet_aton(GROUP), socket.inet_aton(IFACE))
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# Track sequence numbers and loss metrics
last, got, lost = 0, 0, 0
while True:
    data, _ = sock.recvfrom(1024)
    m = json.loads(data)
    got += 1
    # Check for missing sequence numbers (gap detection)
    if last and m["seq"] != last + 1:
        gap = m["seq"] - last - 1
        lost += gap
        print(f"[{name}] GAP: missed {gap} packet(s) before seq {m['seq']}")
    last = m["seq"]
    # Print rolling stats periodically every 100 received packets
    if got % 100 == 0:
        lat = (time.time() - m["ts"]) * 1000
        print(f"[{name}] received={got} lost={lost} latency={lat:.2f} ms")
