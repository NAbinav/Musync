import re
import socket

def check_addr(ip):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((ip, 5005))
        print("hello")
        return is_port_open(ip)
    except Exception as e:
        return False

def all_avail_addr(addrs):
    available = []
    for ip in addrs:
        if check_addr(str(ip)):
            print(f"{ip} is available.")
            available.append(ip)
        else:
            print(f"{ip} is NOT available.")
    return available


def is_port_open(ip, port=5005, timeout=0.5):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            print(result)
            return result == 0  # 0 means connection succeeded
    except Exception as e:
        return False

