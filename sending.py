import socket
import pyaudio
import struct
import time

# Audio config
CHUNK = 512
RATE = 44100
CHANNELS = 2
FORMAT = pyaudio.paInt16

TARGET_IP = '192.168.1.16'  # Replace with your receiver IP
TARGET_PORT = 5005

def list_input_devices(p):
    print("Available input devices:")
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            print(f"  {i}: {info['name']} (Input channels: {info['maxInputChannels']})")

def main():
    p = pyaudio.PyAudio()
    list_input_devices(p)
    
    device_index = int(input("Enter device index to capture system audio (e.g., Stereo Mix): "))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=CHUNK)

    print(f"Sending audio chunks from device {device_index} to {TARGET_IP}:{TARGET_PORT}")

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            timestamp = time.perf_counter()
            packet = struct.pack('d', timestamp) + data
            sock.sendto(packet, (TARGET_IP, TARGET_PORT))
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        sock.close()

if __name__ == "__main__":
    main()

