#!/usr/bin/env python3
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import ipaddress
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

class AndroidNetworkScanner:
    def __init__(self):
        self.found_devices = []
        self.local_ip = None

    def get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                self.local_ip = s.getsockname()[0]
                return self.local_ip
        except Exception:
            return "127.0.0.1"

    def scan_port(self, ip, port=80, timeout=1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((str(ip), port))
                return result == 0
        except:
            return False

    def check_multiple_ports(self, ip):
        common_ports = [22, 23, 53, 80, 443, 8080, 8443, 9000]
        for port in common_ports:
            if self.scan_port(ip, port, timeout=0.5):
                return True
        return False

    def ping_alternative(self, ip):
        try:
            if self.scan_port(ip, 80, timeout=1):
                return True
            return self.check_multiple_ports(ip)
        except:
            return False

    def scan_ip(self, ip):
        if self.ping_alternative(ip):
            device_info = {
                'ip': str(ip),
                'hostname': self.get_hostname(ip),
                'ports': self.get_open_ports(ip)
            }
            self.found_devices.append(device_info)
            return f"Found device: {ip}"

    def get_hostname(self, ip):
        try:
            return socket.gethostbyaddr(str(ip))[0]
        except:
            return "Unknown"

    def get_open_ports(self, ip):
        open_ports = []
        common_ports = [22, 23, 53, 80, 135, 139, 443, 445, 993, 995, 8080, 8443]
        for port in common_ports:
            if self.scan_port(ip, port, timeout=0.3):
                open_ports.append(port)
        return open_ports

    def get_network_range(self):
        local_ip = self.get_local_ip()
        if not local_ip:
            return None
        try:
            network = ipaddress.ip_network(f"{local_ip}/24", strict=False)
            return network
        except:
            return None

    def scan_network(self, max_workers=50):
        network = self.get_network_range()
        if not network:
            return "Could not determine network range"
        result = f"Scanning network: {network}\nLocal IP: {self.local_ip}\nScanning...\n"
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self.scan_ip, network.hosts())
            for res in results:
                if res:
                    result += f"{res}\n"
        end_time = time.time()
        result += f"\nScan completed in {end_time - start_time:.2f} seconds\n"
        return result

    def display_results(self):
        result = f"{len(self.found_devices)} device(s) found:\n\n"
        result += "-" * 70 + "\n"
        for device in self.found_devices:
            ip = device['ip']
            hostname = device['hostname']
            ports = device['ports']
            if ip == self.local_ip:
                result += f"{ip:<15} This Device\n"
            else:
                result += f"{ip:<15} {hostname}\n"
                if ports:
                    result += f"{'':15} Open ports: {', '.join(map(str, ports))}\n"
            result += "-" * 70 + "\n"
        return result

class ScannerApp(App):
    def build(self):
        self.scanner = AndroidNetworkScanner()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.result_label = Label(text="Press the button to start scanning", size_hint=(1, 0.8))
        scan_button = Button(text="Start Network Scan", size_hint=(1, 0.1))
        scan_button.bind(on_press=self.start_scan)
        layout.add_widget(self.result_label)
        layout.add_widget(scan_button)
        scroll_view = ScrollView()
        scroll_view.add_widget(layout)
        return scroll_view

    def start_scan(self, instance):
        self.result_label.text = "Scanning, please wait..."
        threading.Thread(target=self.run_scan).start()

    def run_scan(self):
        result = self.scanner.scan_network()
        result += self.scanner.display_results()
        self.result_label.text = result

if __name__ == '__main__':
    ScannerApp().run()


