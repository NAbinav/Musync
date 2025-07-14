import socket
import pyaudio
import struct
import time

CHUNK = 512
RATE = 44100
CHANNELS = 2
FORMAT = pyaudio.paInt16

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 5005))

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

print("Listening for audio chunks...")

while True:
    packet, addr = sock.recvfrom(4096)
    recv_time = time.perf_counter()
    # Extract timestamp (first 8 bytes)
    sent_timestamp = struct.unpack('d', packet[:8])[0]
    audio_data = packet[8:]
    latency = (recv_time - sent_timestamp) * 1000  # convert to ms

    print(f"Latency: {latency:.2f} ms")
    stream.write(audio_data)

