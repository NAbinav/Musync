#!/usr/bin/env python3
import ipaddress
import netifaces
import subprocess
import time
import os
import socket
from concurrent.futures import ThreadPoolExecutor

receivers = []
IP = "127.0.0.1"
CLEAR_WHEN_DONE = True
DISCOVERY_PORT = 5006
DISCOVERY_MESSAGE = b"DISCOVER_AUDIO_RECEIVER"
DISCOVERY_RESPONSE = b"AUDIO_RECEIVER_ACTIVE"
DISCOVERY_TIMEOUT = 1.5  # Increased timeout for reliability

def get_mac(ip):
    """Gets the MAC address and hostname from the ARP cache"""
    try:
        # Ensure ARP cache is populated by pinging first
        ping_cmd = ['ping', '-n', '1', ip] if os.name == 'nt' else ['ping', '-c', '1', ip]
        subprocess.call(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        p = os.popen('arp -e ' + str(ip))
        lines = p.readlines()
        if len(lines) < 2:
            return None
        li = [x for x in lines[1].split(' ') if x]
        return li[2], ('Unknown' if li[0] == str(ip) else li[0])
    except (IndexError, OSError):
        return None

def check_receiver(ip):
    """Check if the device responds to a discovery packet on DISCOVERY_PORT"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(DISCOVERY_TIMEOUT)
        sock.sendto(DISCOVERY_MESSAGE, (str(ip), DISCOVERY_PORT))
        data, _ = sock.recvfrom(1024)
        sock.close()
        if data == DISCOVERY_RESPONSE:
            print(f"{ip}: Receiver awake on port 5005 (UDP discovery)")
            return True
        print(f"{ip}: No receiver response (UDP)")
        return False
    except (socket.timeout, socket.error) as e:
        sock.close()
        print(f"{ip}: No receiver response (UDP, error: {e})")
        return False

def check_addr(ip):
    """Check if address is reachable and running the receiver"""
    if ipaddress.ip_address(ip).is_loopback:
        print(f"{ip}: Skipped (loopback address)")
        receivers.append((ip, False))
        return
    if ping(str(ip)):
        is_receiver = check_receiver(ip)
        receivers.append((ip, is_receiver))
    else:
        print(f"{ip}: Not reachable (ping failed)")
        receivers.append((ip, False))

def ping(ip):
    """Pings an address"""
    ping_cmd = ['ping', '-n', '1', ip] if os.name == 'nt' else ['ping', '-c', '1', ip]
    return subprocess.call(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def choose_iface():
    """Prompt user to choose a network interface"""
    print("Available Interfaces:\n")
    ifaces = netifaces.interfaces()
    for n, x in enumerate(ifaces):
        try:
            addr = netifaces.ifaddresses(x).get(netifaces.AF_INET, [{}])[0].get('addr', 'No IP')
            print(f'{n}: {x} ({addr})')
        except:
            print(f'{n}: {x性命

System: * Today's date and time is 12:16 AM IST on Tuesday, July 15, 2025.
