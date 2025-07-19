import socket
import time

HOST = '192.168.1.17'  # Replace with Termux device IP or use '127.0.0.1' if on same device
PORT = 50007
DATA_SIZE = 65526
NUM_ITERATIONS = 10  # Number of send/receive cycles
data_to_send = b'a' * DATA_SIZE

total_bytes = 0
total_time = 0

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    for i in range(NUM_ITERATIONS):
        start = time.perf_counter()
        s.sendall(data_to_send)
        received = s.recv(DATA_SIZE)
        end = time.perf_counter()

        if not received:
            break

        elapsed = end - start
        total_time += elapsed
        total_bytes += len(received)

        print(f"Iteration {i+1}: {len(received)} bytes in {elapsed:.6f} seconds")

# Calculate speed
speed_mbps = (total_bytes * 8) / (total_time * 1_000_000)  # bits per second -> megabits/sec
speed_MBps = total_bytes / (total_time * 1024 * 1024)      # bytes per second -> megabytes/sec

print(f"\nTotal: {total_bytes} bytes in {total_time:.6f} seconds")
print(f"Transfer speed: {speed_mbps:.2f} Mbps ({speed_MBps:.2f} MB/s)")

