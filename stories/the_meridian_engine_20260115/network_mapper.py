#!/usr/bin/env python3
"""
The Meridian Network Mapper - Victoria Brassheart's Network Analysis Engine
A real-time network topology mapper and signal analysis tool
"""

import socket
import subprocess
import json
import time
import threading
from datetime import datetime
from collections import defaultdict, deque
import ipaddress

class MeridianNetworkMapper:
    def __init__(self):
        self.active_hosts = {}
        self.signal_patterns = defaultdict(list)
        self.network_topology = {}
        self.anomalies = []
        self.monitoring = False
        
    def scan_local_network(self, network_range="192.168.1.0/24"):
        """Scan local network for active devices and open ports"""
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            active_devices = []
            
            print(f"Scanning network {network_range}...")
            for ip in network.hosts():
                if self._ping_host(str(ip)):
                    device_info = self._probe_device(str(ip))
                    if device_info:
                        active_devices.append(device_info)
                        
            return active_devices
        except Exception as e:
            return [{"error": f"Scan failed: {e}"}]
    
    def _ping_host(self, host, timeout=1):
        """Quick ping to check if host is responsive"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', str(timeout), host],
                capture_output=True, timeout=timeout+1
            )
            return result.returncode == 0
        except:
            return False
    
    def _probe_device(self, ip):
        """Gather information about a detected device"""
        device = {
            "ip": ip,
            "timestamp": datetime.now().isoformat(),
            "ports": [],
            "services": {},
            "signal_strength": self._estimate_signal_strength(ip)
        }
        
        # Check common ports
        common_ports = [22, 23, 53, 80, 135, 139, 443, 445, 993, 995]
        for port in common_ports:
            if self._check_port(ip, port):
                device["ports"].append(port)
                service = self._identify_service(port)
                if service:
                    device["services"][port] = service
        
        return device
    
    def _check_port(self, ip, port, timeout=0.5):
        """Check if a specific port is open"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                return result == 0
        except:
            return False
    
    def _identify_service(self, port):
        """Identify likely service based on port number"""
        services = {
            22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 135: "RPC", 139: "NetBIOS",
            143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
            995: "POP3S"
        }
        return services.get(port, f"Unknown-{port}")
    
    def _estimate_signal_strength(self, ip):
        """Estimate signal strength based on response time"""
        try:
            start_time = time.time()
            result = subprocess.run(['ping', '-c', '1', ip], 
                                  capture_output=True, timeout=2)
            response_time = time.time() - start_time
            
            # Convert response time to signal strength (0-100)
            if result.returncode != 0:
                return 0
            
            strength = max(0, min(100, 100 - (response_time * 50)))
            return round(strength, 2)
        except:
            return 0
    
    def monitor_traffic_patterns(self, duration=60):
        """Monitor network traffic patterns for anomalies"""
        self.monitoring = True
        start_time = time.time()
        pattern_data = []
        
        print(f"Monitoring network patterns for {duration} seconds...")
        
        while self.monitoring and (time.time() - start_time) < duration:
            # Sample current network state
            sample = {
                "timestamp": datetime.now().isoformat(),
                "active_connections": self._get_active_connections(),
                "network_load": self._estimate_network_load()
            }
            pattern_data.append(sample)
            time.sleep(2)
        
        # Analyze patterns for anomalies
        anomalies = self._detect_anomalies(pattern_data)
        return {
            "duration": duration,
            "samples": len(pattern_data),
            "anomalies": anomalies,
            "patterns": pattern_data
        }
    
    def _get_active_connections(self):
        """Get count of active network connections"""
        try:
            result = subprocess.run(['netstat', '-an'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                established = len([l for l in lines if 'ESTABLISHED' in l])
                listening = len([l for l in lines if 'LISTEN' in l])
                return {"established": established, "listening": listening}
        except:
            pass
        return {"established": 0, "listening": 0}
    
    def _estimate_network_load(self):
        """Estimate current network load"""
        # This is a simplified estimation
        # In a real scenario, you'd monitor interface statistics
        try:
            with open('/proc/loadavg', 'r') as f:
                load = float(f.read().split()[0])
                return min(100, load * 20)  # Scale to 0-100
        except:
            return 0
    
    def _detect_anomalies(self, pattern_data):
        """Detect unusual patterns in network traffic"""
        if len(pattern_data) < 10:
            return []
        
        anomalies = []
        
        # Check for sudden spikes in connections
        conn_counts = [p["active_connections"]["established"] for p in pattern_data]
        avg_connections = sum(conn_counts) / len(conn_counts)
        
        for i, count in enumerate(conn_counts):
            if count > avg_connections * 2:
                anomalies.append({
                    "type": "connection_spike",
                    "timestamp": pattern_data[i]["timestamp"],
                    "value": count,
                    "baseline": avg_connections
                })
        
        # Check for load anomalies
        loads = [p["network_load"] for p in pattern_data]
        avg_load = sum(loads) / len(loads)
        
        for i, load in enumerate(loads):
            if load > avg_load * 3:
                anomalies.append({
                    "type": "load_spike",
                    "timestamp": pattern_data[i]["timestamp"],
                    "value": load,
                    "baseline": avg_load
                })
        
        return anomalies
    
    def generate_topology_map(self, scan_results):
        """Generate a network topology visualization"""
        topology = {
            "nodes": [],
            "connections": [],
            "summary": {
                "total_devices": len(scan_results),
                "total_ports": sum(len(device.get("ports", [])) for device in scan_results),
                "scan_timestamp": datetime.now().isoformat()
            }
        }
        
        for device in scan_results:
            if "error" in device:
                continue
                
            node = {
                "id": device["ip"],
                "ip": device["ip"],
                "ports": device.get("ports", []),
                "services": device.get("services", {}),
                "signal_strength": device.get("signal_strength", 0),
                "risk_level": self._assess_risk_level(device)
            }
            topology["nodes"].append(node)
        
        return topology
    
    def _assess_risk_level(self, device):
        """Assess security risk level of a device"""
        risk_score = 0
        
        # High-risk ports
        high_risk_ports = [23, 135, 139, 445]  # Telnet, RPC, NetBIOS, SMB
        for port in device.get("ports", []):
            if port in high_risk_ports:
                risk_score += 30
        
        # Many open ports = higher risk
        port_count = len(device.get("ports", []))
        if port_count > 5:
            risk_score += 20
        elif port_count > 10:
            risk_score += 40
        
        # Classify risk level
        if risk_score >= 70:
            return "HIGH"
        elif risk_score >= 40:
            return "MEDIUM"
        elif risk_score > 0:
            return "LOW"
        else:
            return "MINIMAL"
    
    def export_results(self, data, filename=None):
        """Export scan results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meridian_scan_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filename

def main():
    """Main function for standalone operation"""
    print("=== THE MERIDIAN NETWORK MAPPER ===")
    print("Victoria Brassheart's Network Analysis Engine")
    print("Scanning for signals in the brass and steam...")
    print()
    
    mapper = MeridianNetworkMapper()
    
    # Quick network scan
    print("Initiating network scan...")
    devices = mapper.scan_local_network()
    
    if devices and not any("error" in d for d in devices):
        print(f"Detected {len(devices)} active devices")
        
        # Generate topology
        topology = mapper.generate_topology_map(devices)
        
        # Display results
        print("\n=== NETWORK TOPOLOGY ===")
        for node in topology["nodes"]:
            services = ", ".join(node["services"].values()) or "Unknown"
            print(f"Device: {node['ip']}")
            print(f"  Ports: {node['ports']}")
            print(f"  Services: {services}")
            print(f"  Signal Strength: {node['signal_strength']}%")
            print(f"  Risk Level: {node['risk_level']}")
            print()
        
        # Export results
        filename = mapper.export_results({
            "topology": topology,
            "raw_scan": devices
        })
        print(f"Results exported to: {filename}")
        
        # Optional: Monitor patterns
        print("\nMonitor traffic patterns? (y/n): ", end="")
        try:
            if input().lower().startswith('y'):
                print("Monitoring network patterns (60 seconds)...")
                patterns = mapper.monitor_traffic_patterns(60)
                if patterns["anomalies"]:
                    print(f"ALERT: {len(patterns['anomalies'])} anomalies detected!")
                    for anomaly in patterns["anomalies"]:
                        print(f"  {anomaly['type']}: {anomaly['value']} at {anomaly['timestamp']}")
                else:
                    print("No anomalies detected in monitoring period.")
        except KeyboardInterrupt:
            print("\nMonitoring interrupted.")
    
    else:
        print("No devices found or scan failed.")
        if devices:
            for device in devices:
                if "error" in device:
                    print(f"Error: {device['error']}")

if __name__ == "__main__":
    main()