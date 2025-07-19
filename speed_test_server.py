import socket
import sys

HOST = None  # All available interfaces
PORT = 50007
s = None

for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                              socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except OSError:
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except OSError:
        s.close()
        s = None
        continue
    break

if s is None:
    print('Could not open socket')
    sys.exit(1)

print(f"Server is listening on port {PORT}...")

while True:
    try:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(65526)
                if not data:
                    print('Client disconnected')
                    break
                conn.send(data)
    except KeyboardInterrupt:
        print('\nServer stopped by user')
        break
    except Exception as e:
        print(f"Error: {e}")
        continue

s.close()

