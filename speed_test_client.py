import socket
import sys
import time

HOST = '192.168.1.17'    # Replace with your server IP
PORT = 50007
DATA_SIZE = 65526
data_to_send = b'H' * DATA_SIZE

s = None
for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError:
        s = None
        continue
    try:
        s.connect(sa)
    except OSError:
        s.close()
        s = None
        continue
    break

if s is None:
    print('Could not open socket')
    sys.exit(1)

with s:
    start_time = time.perf_counter()
    s.sendall(data_to_send)
    data = s.recv(DATA_SIZE)
    end_time = time.perf_counter()

duration = end_time - start_time
speed_mbps = (len(data) * 8) / (duration * 1_000_000)

print(f"Received {len(data)} bytes in {duration:.6f} seconds")
print(f"Transfer speed: {speed_mbps:.2f} Mbps")

