#!/usr/bin/env python3
import ipaddress
import netifaces
import subprocess
import time
import os
import socket
from concurrent.futures import ThreadPoolExecutor

addrs = []
IP = "127.0.0.1"
CLEAR_WHEN_DONE = True
PORT = 5005  # Port to check

def get_mac(ip):
    """Gets the mac + name from the ARP cache"""
    p = os.popen('arp -e ' + str(ip))
    try:
        li = [x for x in p.readlines()[1].split(' ') if x]
    except IndexError:
        return None
    return li[2], ('Unknown' if li[0] == str(ip) else li[0])

def check_addr(ip):
    """Check if address is reachable and port 5005 is open"""
    if ping(str(ip)):
        port_open = check_port(str(ip), PORT)
        addrs.append((ip, port_open))

def ping(ip):
    """Pings an address"""
    return subprocess.call(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def check_port(ip, port):
    """Check if a port is open on the given IP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # 1-second timeout for quick scanning
    try:
        result = sock.connect_ex((ip, port))
        return result == 0  # Returns True if port is open
    except socket.error:
        return False
    finally:
        sock.close()

def choose_iface():
    print("Available Interfaces:\n")
    ifaces = netifaces.interfaces()
    for n, x in enumerate(ifaces):
        print('%s: %s' % (n, x))
    return ifaces[int(input('\nChoose interface to scan for devices: '))]

def get_addresses(iface):
    global IP
    addresses = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
    IP = addresses['addr']
    return ipaddress.ip_network(addresses['addr'] + '/' + addresses['netmask'], strict=False)

def executePool(addrs):
    print("\nPinging all addresses in subnet %s and checking port %d." % (str(addrs), PORT))
    print("\n --------  IGNORE TEXT --------\n")
    time.sleep(2)
    with ThreadPoolExecutor(max_workers=len(list(addrs))) as exec:
        exec.map(check_addr, addrs)
    print(" --------  IGNORE TEXT --------\n")

if __name__ == '__main__':
    executePool(get_addresses(choose_iface()))
    if CLEAR_WHEN_DONE:
        subprocess.call('clear')
    print("%s device(s) found.\n" % len(addrs))
    print(f"{'IP':<15} {'MAC':<17} {'Hostname':<15} {'Port 5005':<10}")
    print("-" * 60)
    for addr, port_open in addrs:  # Unpack the tuple
        if str(addr) == IP:
            print(f"{str(addr):<15} {'This Device':<17} {'This Device':<15} {'N/A':<10}")
            continue
        mac = get_mac(addr)
        mac_addr, hostname = mac if mac else ("Unknown", "Unknown")
        port_status = "Open" if port_open else "Closed"
        print(f"{str(addr):<15} {mac_addr:<17} {hostname:<15} {port_status:<10}")
