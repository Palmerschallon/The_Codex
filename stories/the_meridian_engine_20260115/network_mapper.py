#!/usr/bin/env python3
"""
The Meridian Network Mapper - Victoria's Brass-Fitted Signal Tracer
A real-time network analysis tool disguised as a dieselpunk invention.
"""

import socket
import subprocess
import platform
import threading
import time
from collections import defaultdict
import json
from datetime import datetime

class MeridianNetworkMapper:
    """
    Victoria Brassheart's Network Mapping Device
    Maps active network connections and analyzes traffic patterns
    """
    
    def __init__(self):
        self.active_connections = {}
        self.traffic_patterns = defaultdict(list)
        self.suspicious_ports = [22, 23, 80, 443, 3389, 5900, 8080]
        self.monitoring = False
        
    def scan_local_network(self, target_range="192.168.1.0/24"):
        """
        The Brass Frequency Sweeper - scans for active devices
        """
        print(f"[MERIDIAN SCANNER] Sweeping frequency range: {target_range}")
        active_devices = []
        
        # Extract base IP and range
        base_ip = ".".join(target_range.split(".")[:-1])
        
        for i in range(1, 255):
            ip = f"{base_ip}.{i}"
            
            # Use ping to check if device is active
            param = "-n" if platform.system().lower() == "windows" else "-c"
            
            try:
                result = subprocess.run(
                    ["ping", param, "1", "-W", "1000", ip],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    active_devices.append(ip)
                    print(f"[SIGNAL DETECTED] Device at {ip}")
            except subprocess.TimeoutExpired:
                continue
                
        return active_devices
    
    def analyze_open_ports(self, target_ip, port_range=None):
        """
        The Brass Port Analyzer - checks for open communication channels
        """
        if port_range is None:
            port_range = self.suspicious_ports
            
        print(f"[MERIDIAN ANALYZER] Scanning ports on {target_ip}")
        open_ports = []
        
        for port in port_range:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            
            try:
                result = sock.connect_ex((target_ip, port))
                if result == 0:
                    open_ports.append(port)
                    print(f"[OPEN CHANNEL] Port {port} on {target_ip}")
            except:
                pass
            finally:
                sock.close()
                
        return open_ports
    
    def monitor_connections(self, duration=60):
        """
        The Brass Traffic Monitor - watches network activity in real-time
        """
        print(f"[MERIDIAN MONITOR] Beginning {duration}s surveillance sweep...")
        self.monitoring = True
        
        def connection_tracker():
            start_time = time.time()
            while self.monitoring and (time.time() - start_time) < duration:
                try:
                    # Get network connections (platform specific)
                    if platform.system().lower() == "windows":
                        result = subprocess.run(
                            ["netstat", "-an"], 
                            capture_output=True, 
                            text=True
                        )
                    else:
                        result = subprocess.run(
                            ["netstat", "-an"], 
                            capture_output=True, 
                            text=True
                        )
                    
                    timestamp = datetime.now().isoformat()
                    connections = self._parse_netstat_output(result.stdout)
                    
                    for conn in connections:
                        conn_id = f"{conn['local_addr']}:{conn['local_port']}-{conn['remote_addr']}:{conn['remote_port']}"
                        self.traffic_patterns[conn_id].append({
                            'timestamp': timestamp,
                            'state': conn['state'],
                            'protocol': conn['protocol']
                        })
                    
                    time.sleep(5)  # Sample every 5 seconds
                    
                except Exception as e:
                    print(f"[MERIDIAN ERROR] Monitoring error: {e}")
                    
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=connection_tracker)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return monitor_thread
    
    def _parse_netstat_output(self, netstat_output):
        """Parse netstat output into structured connection data"""
        connections = []
        lines = netstat_output.split('\n')
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 4 and (parts[0] in ['TCP', 'UDP']):
                try:
                    protocol = parts[0]
                    local_addr_port = parts[1].rsplit(':', 1)
                    remote_addr_port = parts[2].rsplit(':', 1)
                    state = parts[3] if len(parts) > 3 else "UNKNOWN"
                    
                    if len(local_addr_port) == 2 and len(remote_addr_port) == 2:
                        connections.append({
                            'protocol': protocol,
                            'local_addr': local_addr_port[0],
                            'local_port': local_addr_port[1],
                            'remote_addr': remote_addr_port[0],
                            'remote_port': remote_addr_port[1],
                            'state': state
                        })
                except:
                    continue
                    
        return connections
    
    def generate_network_map(self):
        """
        The Brass Network Cartographer - creates a visual map of discovered networks
        """
        network_map = {
            'timestamp': datetime.now().isoformat(),
            'discovered_devices': [],
            'connection_patterns': {},
            'suspicious_activity': []
        }
        
        # Analyze traffic patterns for suspicious activity
        for conn_id, traffic_history in self.traffic_patterns.items():
            if len(traffic_history) > 10:  # Frequent connections
                network_map['suspicious_activity'].append({
                    'connection': conn_id,
                    'frequency': len(traffic_history),
                    'pattern': 'high_frequency'
                })
                
            network_map['connection_patterns'][conn_id] = {
                'total_connections': len(traffic_history),
                'first_seen': traffic_history[0]['timestamp'] if traffic_history else None,
                'last_seen': traffic_history[-1]['timestamp'] if traffic_history else None
            }
        
        return network_map
    
    def stop_monitoring(self):
        """Stop the network monitoring process"""
        print("[MERIDIAN SCANNER] Shutting down surveillance...")
        self.monitoring = False
    
    def save_intelligence_report(self, filename="meridian_network_intelligence.json"):
        """
        The Brass Intelligence Archive - saves reconnaissance data
        """
        report = self.generate_network_map()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"[MERIDIAN ARCHIVE] Intelligence report saved to {filename}")
        return filename

# Victoria's Quick Deployment Functions
def quick_network_sweep(target_range="192.168.1.0/24"):
    """Victoria's emergency network sweep - one command deployment"""
    mapper = MeridianNetworkMapper()
    print("[MERIDIAN EMERGENCY SWEEP] Deploying brass scanners...")
    
    # Quick scan of local network
    devices = mapper.scan_local_network(target_range)
    
    # Port scan the first few active devices
    for device in devices[:5]:  # Limit to first 5 for speed
        ports = mapper.analyze_open_ports(device)
        if ports:
            print(f"[INTELLIGENCE] Device {device} has open channels: {ports}")
    
    return devices

if __name__ == "__main__":
    print("=" * 60)
    print("VICTORIA BRASSHEART'S MERIDIAN NETWORK MAPPER")
    print("Industrial Network Reconnaissance Device - Model 1934")
    print("=" * 60)
    
    mapper = MeridianNetworkMapper()
    
    # Run a quick network sweep
    print("\n[BRASS DEPLOYMENT] Initializing frequency sweepers...")
    devices = quick_network_sweep()
    
    if devices:
        print(f"\n[MERIDIAN INTELLIGENCE] Discovered {len(devices)} active devices")
        
        # Start monitoring for 30 seconds
        print("\n[SURVEILLANCE MODE] Beginning traffic analysis...")
        monitor_thread = mapper.monitor_connections(30)
        
        time.sleep(30)
        mapper.stop_monitoring()
        
        # Generate and save report
        report_file = mapper.save_intelligence_report()
        print(f"\n[MISSION COMPLETE] Full intelligence report available in {report_file}")
    else:
        print("\n[MERIDIAN REPORT] No active devices detected in range")