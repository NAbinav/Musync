import socket
import pyaudio
import struct
import time

# Audio config
CHUNK = 512
RATE = 44100
CHANNELS = 2
FORMAT = pyaudio.paInt16

TARGET_IP = '192.168.1.16'  # Replace with receiver IP
TARGET_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("Sending audio chunks to", TARGET_IP)

while True:
    data = stream.read(CHUNK, exception_on_overflow=False)
    timestamp = time.perf_counter()
    # Pack timestamp as double (8 bytes) + audio data
    packet = struct.pack('d', timestamp) + data
    sock.sendto(packet, (TARGET_IP, TARGET_PORT))

