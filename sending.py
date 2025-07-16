import sounddevice as sd
import socket
import struct
import time
import numpy as np

# Configuration
TARGET_IP = '192.168.1.16'  # Replace with your receiver IP
TARGET_PORT = 5005
DEVICE_INDEX = 9  # Your system monitor device index
CHUNK = 2048
BUFFER_SIZE = 65536

# Initialize socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)

# Query device info
device_info = sd.query_devices(DEVICE_INDEX)
RATE = int(device_info['default_samplerate'])
CHANNELS = min(device_info['max_input_channels'], 2)

print(f"Device: {device_info['name']}")
print(f"Sample Rate: {RATE} Hz")
print(f"Channels: {CHANNELS}")
print(f"Chunk Size: {CHUNK}")

# Global variables
sequence_number = 0
packets_sent = 0
start_time = time.time()

def callback(indata, frames, time_info, status):
    global sequence_number, packets_sent
    
    if status:
        print(f"Input status: {status}")
    
    try:
        # Convert float32 to int16 for compatibility
        audio_int16 = (indata * 32767).astype(np.int16)
        
        # Create packet with sequence number and timestamp
        timestamp = time.perf_counter()
        packet = struct.pack('Qd', sequence_number, timestamp) + audio_int16.tobytes()
        
        # Send packet
        sock.sendto(packet, (TARGET_IP, TARGET_PORT))
        
        sequence_number += 1
        packets_sent += 1
        
        # Print stats every 100 packets
        if packets_sent % 100 == 0:
            elapsed = time.time() - start_time
            print(f"Sent {packets_sent} packets in {elapsed:.1f}s ({packets_sent/elapsed:.1f} pps)")
            
    except Exception as e:
        print(f"Callback error: {e}")

def main():
    print(f"Starting audio stream to {TARGET_IP}:{TARGET_PORT}")
    print("Press Ctrl+C to stop...")
    
    try:
        with sd.InputStream(
            device=DEVICE_INDEX,
            channels=CHANNELS,
            samplerate=RATE,
            blocksize=CHUNK,
            latency='low',
            callback=callback,
            dtype=np.float32
        ):
            while True:
                sd.sleep(1000)
                
    except KeyboardInterrupt:
        print(f"\nSender stopped. Sent {packets_sent} packets total.")
    except Exception as e:
        print(f"Stream error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
