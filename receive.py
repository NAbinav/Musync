import socket
import pyaudio
import struct
import time
import queue
import threading
import statistics
from collections import deque

# Configuration
LISTEN_PORT = 5005
CHUNK = 1024
RATE = 48000
CHANNELS = 2
FORMAT = pyaudio.paInt16
BUFFER_SIZE = 65536
MAX_QUEUE_SIZE = 20
INITIAL_BUFFER_SIZE = 5

# Global variables
audio_queue = queue.Queue()
running = True
stats = {
    'packets_received': 0,
    'packets_dropped': 0,
    'latencies': deque(maxlen=100),
    'sequence_numbers': deque(maxlen=100)
}

def audio_playback():
    """Audio playback thread"""
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            output=True,
            frames_per_buffer=CHUNK
        )
        
        print("Playback thread started")
        
        # Wait for initial buffer
        while audio_queue.qsize() < INITIAL_BUFFER_SIZE and running:
            time.sleep(0.01)
        
        print("Starting playback...")
        
        while running:
            try:
                # Get audio data with timeout
                data = audio_queue.get(timeout=1.0)
                if data is None:
                    break
                
                stream.write(data)
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Playback error: {e}")
                
    except Exception as e:
        print(f"Audio initialization error: {e}")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()
        print("Playback thread stopped")

def print_stats():
    """Print periodic statistics"""
    if stats['packets_received'] > 0:
        avg_latency = statistics.mean(stats['latencies']) if stats['latencies'] else 0
        loss_rate = (stats['packets_dropped'] / (stats['packets_received'] + stats['packets_dropped'])) * 100 if (stats['packets_received'] + stats['packets_dropped']) > 0 else 0
        
        print(f"\nStats - Received: {stats['packets_received']}, "
              f"Dropped: {stats['packets_dropped']}, "
              f"Loss: {loss_rate:.1f}%, "
              f"Avg Latency: {avg_latency:.2f}ms, "
              f"Queue: {audio_queue.qsize()}")

def main():
    global running
    
    print(f"Starting audio receiver on port {LISTEN_PORT}")
    print(f"Audio format: {RATE}Hz, {CHANNELS} channels, {FORMAT}")
    
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFFER_SIZE)
    
    try:
        sock.bind(('0.0.0.0', LISTEN_PORT))
        print(f"Listening on 0.0.0.0:{LISTEN_PORT}")
        
        # Start playback thread
        playback_thread = threading.Thread(target=audio_playback, daemon=True)
        playback_thread.start()
        
        last_stats_time = time.time()
        expected_seq = None  # Will be set from first packet
        
        print("Waiting for audio packets... Press Ctrl+C to stop")
        
        while running:
            try:
                # Receive packet
                packet, addr = sock.recvfrom(4096)
                recv_time = time.perf_counter()
                
                # Parse packet
                if len(packet) < 16:  # 8 bytes seq + 8 bytes timestamp
                    continue
                
                seq_num, sent_timestamp = struct.unpack('Qd', packet[:16])
                audio_data = packet[16:]
                
                # Calculate latency
                latency = (recv_time - sent_timestamp) * 1000
                stats['latencies'].append(latency)
                stats['sequence_numbers'].append(seq_num)
                
                # Check for dropped packets
                if expected_seq is None:
                    expected_seq = seq_num + 1  # Initialize from first packet
                elif seq_num != expected_seq:
                    dropped = seq_num - expected_seq
                    if dropped > 0:  # Only count positive drops
                        stats['packets_dropped'] += dropped
                        print(f"Dropped {dropped} packets (expected {expected_seq}, got {seq_num})")
                    expected_seq = seq_num + 1
                else:
                    expected_seq = seq_num + 1
                stats['packets_received'] += 1
                
                # Manage queue size
                if audio_queue.qsize() > MAX_QUEUE_SIZE:
                    try:
                        audio_queue.get_nowait()  # Drop oldest
                        stats['packets_dropped'] += 1
                    except queue.Empty:
                        pass
                
                # Add to playback queue
                audio_queue.put(audio_data)
                
                # Print stats every 5 seconds
                if time.time() - last_stats_time > 5:
                    print_stats()
                    last_stats_time = time.time()
                
                # Print latency every 50 packets
                if stats['packets_received'] % 50 == 0:
                    print(f"Latency: {latency:.2f}ms, Queue: {audio_queue.qsize()}")
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Receive error: {e}")
                
    except KeyboardInterrupt:
        print("\nReceiver stopping...")
    except Exception as e:
        print(f"Socket error: {e}")
    finally:
        running = False
        
        # Signal playback thread to stop
        audio_queue.put(None)
        
        # Wait for playback thread
        if 'playback_thread' in locals():
            playback_thread.join(timeout=2)
        
        sock.close()
        print_stats()
        print("Receiver stopped")

if __name__ == "__main__":
    main()
