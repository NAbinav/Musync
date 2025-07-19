import socket
import time

HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 6000
BUFFER_SIZE = 65536  # 64 KB

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print(f"📡 Server listening on port {PORT}...")

conn, addr = s.accept()
print(f"✅ Connected by {addr}")

start_time = time.time()
total_received = 0

while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    total_received += len(data)

end_time = time.time()
duration = end_time - start_time
speed_mbps = (total_received * 8) / (duration * 1_000_000)  # Convert to Mbps

print(f"\n📥 Received {total_received / (1024*1024):.2f} MB in {duration:.2f} seconds")
print(f"⚡ Speed: {speed_mbps:.2f} Mbps")

conn.close()
s.close()

