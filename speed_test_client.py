import socket
import time

SERVER_IP = '192.168.1.16'  # Replace with your server's IP
PORT = 6000
BUFFER_SIZE = 65536  # 64 KB
TOTAL_MB = 100       # How much to send

total_bytes = TOTAL_MB * 1024 * 1024
data_chunk = b'a' * BUFFER_SIZE  # Dummy data

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, PORT))
print(f"🚀 Sending {TOTAL_MB} MB to {SERVER_IP}:{PORT}...")

start_time = time.time()
sent = 0

while sent < total_bytes:
    s.sendall(data_chunk)
    sent += len(data_chunk)

end_time = time.time()
duration = end_time - start_time
speed_mbps = (sent * 8) / (duration * 1_000_000)

print(f"\n📤 Sent {TOTAL_MB} MB in {duration:.2f} seconds")
print(f"⚡ Speed: {speed_mbps:.2f} Mbps")

s.close()

