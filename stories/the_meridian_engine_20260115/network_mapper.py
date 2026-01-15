"""
THE MERIDIAN ENGINE - Network Traffic Mapper
Real-time visualization of network connections and traffic patterns

Victoria Brassheart's improvised network visualization device
"""

import socket
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
import json

class NetworkMapper:
    """
    Maps and visualizes active network connections in real-time
    Useful for detecting unusual traffic patterns or unauthorized connections
    """
    
    def __init__(self, max_history=1000):
        self.connections = defaultdict(list)
        self.traffic_history = deque(maxlen=max_history)
        self.active_ports = set()
        self.suspicious_patterns = []
        self.monitoring = False
        
    def start_monitoring(self, duration=60):
        """Begin monitoring network activity"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop, args=(duration,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def _monitor_loop(self, duration):
        """Main monitoring loop - scans for active connections"""
        start_time = time.time()
        
        while self.monitoring and (time.time() - start_time) < duration:
            try:
                # Scan common ports for activity
                for port in range(21, 1025):  # Common service ports
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    
                    # Check localhost
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result == 0:
                        self._record_connection('127.0.0.1', port)
                        self.active_ports.add(port)
                    
                    sock.close()
                    
                    if not self.monitoring:
                        break
                        
                # Brief pause between scans
                time.sleep(1)
                
            except Exception as e:
                continue
                
    def _record_connection(self, host, port):
        """Record a detected connection"""
        timestamp = datetime.now()
        connection = {
            'timestamp': timestamp.isoformat(),
            'host': host,
            'port': port,
            'service': self._identify_service(port)
        }
        
        self.connections[f"{host}:{port}"].append(connection)
        self.traffic_history.append(connection)
        
        # Check for suspicious patterns
        self._analyze_pattern(host, port)
        
    def _identify_service(self, port):
        """Identify common services by port number"""
        common_ports = {
            21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S"
        }
        return common_ports.get(port, "UNKNOWN")
        
    def _analyze_pattern(self, host, port):
        """Detect suspicious connection patterns"""
        # Count recent connections to this endpoint
        recent_count = len([c for c in self.traffic_history 
                           if c['host'] == host and c['port'] == port])
        
        # Flag unusual activity
        if recent_count > 10:  # Rapid repeated connections
            pattern = f"HIGH_FREQUENCY: {host}:{port} ({recent_count} connections)"
            if pattern not in self.suspicious_patterns:
                self.suspicious_patterns.append(pattern)
                
        # Flag unusual ports
        if port > 8000:  # High port numbers
            pattern = f"HIGH_PORT: {host}:{port}"
            if pattern not in self.suspicious_patterns:
                self.suspicious_patterns.append(pattern)
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring = False
        
    def get_network_map(self):
        """Return current network topology"""
        nodes = set()
        edges = []
        
        for endpoint, connections in self.connections.items():
            host, port = endpoint.split(':')
            nodes.add(f"LOCAL")
            nodes.add(f"{host}:{port}")
            
            edges.append({
                'source': 'LOCAL',
                'target': f"{host}:{port}",
                'service': connections[-1]['service'] if connections else 'UNKNOWN',
                'connections': len(connections)
            })
            
        return {
            'nodes': list(nodes),
            'edges': edges,
            'total_connections': len(self.traffic_history),
            'active_ports': sorted(list(self.active_ports)),
            'suspicious_patterns': self.suspicious_patterns
        }
        
    def export_analysis(self, filename):
        """Export network analysis to file"""
        analysis = {
            'scan_timestamp': datetime.now().isoformat(),
            'network_map': self.get_network_map(),
            'traffic_history': list(self.traffic_history),
            'summary': {
                'unique_endpoints': len(self.connections),
                'total_traffic': len(self.traffic_history),
                'suspicious_patterns': len(self.suspicious_patterns)
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
            
    def print_status(self):
        """Display current monitoring status"""
        print("=" * 60)
        print("MERIDIAN NETWORK MAPPER - STATUS REPORT")
        print("=" * 60)
        
        network_map = self.get_network_map()
        
        print(f"Active Monitoring: {'YES' if self.monitoring else 'NO'}")
        print(f"Total Connections: {network_map['total_connections']}")
        print(f"Unique Endpoints: {len(self.connections)}")
        print(f"Active Ports: {len(network_map['active_ports'])}")
        
        if network_map['active_ports']:
            print(f"Port Range: {min(network_map['active_ports'])}-{max(network_map['active_ports'])}")
            
        print(f"\nSuspicious Patterns: {len(network_map['suspicious_patterns'])}")
        for pattern in network_map['suspicious_patterns']:
            print(f"  ⚠ {pattern}")
            
        if network_map['edges']:
            print(f"\nRecent Connections:")
            for edge in network_map['edges'][-5:]:  # Last 5
                print(f"  {edge['source']} → {edge['target']} ({edge['service']})")

# Usage example for the story
if __name__ == "__main__":
    # Victoria's network mapper in action
    mapper = NetworkMapper()
    
    print("Initializing Meridian Network Mapper...")
    print("Scanning for active connections...")
    
    mapper.start_monitoring(duration=30)
    
    # Monitor for 30 seconds
    time.sleep(30)
    
    mapper.stop_monitoring()
    mapper.print_status()
    
    # Export findings
    mapper.export_analysis("meridian_network_scan.json")
    print("\nAnalysis exported to meridian_network_scan.json")