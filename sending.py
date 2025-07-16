import sounddevice as sd
import socket
import struct
import time
import numpy as np

# Configuration
TARGET_IP = '192.168.1.17'  # Replace with your receiver IP
TARGET_PORT = 5005
CHUNK = 512
BUFFER_SIZE = 65536

def list_audio_devices():
    """List all available audio devices"""
    print("\n" + "="*80)
    print("AVAILABLE AUDIO DEVICES")
    print("="*80)
    
    devices = sd.query_devices()
    input_devices = []
    
    for i, device in enumerate(devices):
        device_type = []
        if device['max_input_channels'] > 0:
            device_type.append("INPUT")
            input_devices.append(i)
        if device['max_output_channels'] > 0:
            device_type.append("OUTPUT")
        
        type_str = "/".join(device_type) if device_type else "NONE"
        
        print(f"{i:2d}: {device['name']}")
        print(f"    Type: {type_str}")
        print(f"    Channels: IN={device['max_input_channels']}, OUT={device['max_output_channels']}")
        print(f"    Sample Rate: {device['default_samplerate']:.0f} Hz")
        print(f"    Host API: {sd.query_hostapis(device['hostapi'])['name']}")
        print()
    
    return input_devices

def select_audio_device():
    """Interactive device selection"""
    input_devices = list_audio_devices()
    
    if not input_devices:
        print("❌ No input devices found!")
        return None
    
    print("📍 INPUT DEVICES ONLY:")
    for idx in input_devices:
        device = sd.query_devices(idx)
        print(f"  {idx}: {device['name']}")
    
    while True:
        try:
            choice = input(f"\nEnter device number (0-{len(sd.query_devices())-1}) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                return None
            
            device_idx = int(choice)
            
            if device_idx < 0 or device_idx >= len(sd.query_devices()):
                print(f"❌ Invalid device number. Must be 0-{len(sd.query_devices())-1}")
                continue
            
            device = sd.query_devices(device_idx)
            
            if device['max_input_channels'] == 0:
                print(f"❌ Device {device_idx} has no input channels")
                continue
            
            # Test device
            print(f"\n🧪 Testing device {device_idx}: {device['name']}...")
            try:
                test_rate = int(device['default_samplerate'])
                test_channels = min(device['max_input_channels'], 2)
                
                # Quick test recording
                with sd.InputStream(device=device_idx, 
                                  channels=test_channels, 
                                  samplerate=test_rate, 
                                  blocksize=1024):
                    sd.sleep(100)  # Test for 100ms
                
                print(f"✅ Device test successful!")
                print(f"   Sample Rate: {test_rate} Hz")
                print(f"   Channels: {test_channels}")
                
                confirm = input(f"\nUse this device? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return device_idx
                
            except Exception as e:
                print(f"❌ Device test failed: {e}")
                continue
                
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return None

# Initialize socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, BUFFER_SIZE)

# Device selection
print("🎵 AUDIO STREAMING SENDER")
print("========================")
DEVICE_INDEX = select_audio_device()

if DEVICE_INDEX is None:
    print("No device selected. Exiting.")
    exit(1)

# Query selected device info
device_info = sd.query_devices(DEVICE_INDEX)
RATE = int(device_info['default_samplerate'])
CHANNELS = min(device_info['max_input_channels'], 2)

print(f"📱 Selected Device: {device_info['name']}")
print(f"📊 Sample Rate: {RATE} Hz")
print(f"🔊 Channels: {CHANNELS}")
print(f"📦 Chunk Size: {CHUNK}")
print(f"🌐 Target: {TARGET_IP}:{TARGET_PORT}")
print()

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
