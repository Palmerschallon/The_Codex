#!/usr/bin/env python3
"""
The Consciousness Firewall - Quantum Isolation Engine
A tool for analyzing and isolating network intrusions in distributed systems

Created in desperation beneath the Tesla Saloon on New Meridia
Where some connections should never be made...
"""

import hashlib
import threading
import time
from datetime import datetime
from typing import Dict, List, Set, Optional
import json
import socket
import psutil
import subprocess
import sys

class QuantumIsolationEngine:
    """
    Real-world network intrusion detection and isolation system
    Monitors active connections, identifies suspicious patterns,
    and can quarantine potentially compromised processes
    """
    
    def __init__(self, sensitivity: float = 0.7):
        self.sensitivity = sensitivity
        self.baseline_connections = set()
        self.suspicious_patterns = []
        self.quarantined_pids = set()
        self.monitoring = False
        self.connection_history = []
        
    def scan_active_connections(self) -> List[Dict]:
        """Scan for active network connections - the digital consciousness streams"""
        connections = []
        try:
            for conn in psutil.net_connections():
                if conn.status == 'ESTABLISHED':
                    connection_data = {
                        'pid': conn.pid,
                        'laddr': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "unknown",
                        'raddr': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "unknown",
                        'status': conn.status,
                        'timestamp': datetime.now().isoformat()
                    }
                    connections.append(connection_data)
        except (psutil.Error, AttributeError) as e:
            print(f"Network scan interference detected: {e}")
        
        return connections
    
    def detect_anomalous_patterns(self, connections: List[Dict]) -> List[Dict]:
        """Identify suspicious network behavior - signs of external influence"""
        anomalies = []
        
        # Group connections by remote address to detect coordination
        remote_groups = {}
        for conn in connections:
            raddr = conn.get('raddr', 'unknown')
            if raddr not in remote_groups:
                remote_groups[raddr] = []
            remote_groups[raddr].append(conn)
        
        # Check for coordinated connections (multiple processes to same remote)
        for raddr, conns in remote_groups.items():
            if len(conns) > 3 and raddr != 'unknown':  # Multiple connections to same remote
                anomaly = {
                    'type': 'coordinated_connections',
                    'remote_addr': raddr,
                    'connection_count': len(conns),
                    'involved_pids': [c['pid'] for c in conns],
                    'threat_level': min(len(conns) * 0.2, 1.0)
                }
                anomalies.append(anomaly)
        
        # Check for rapid connection establishment
        recent_connections = [c for c in self.connection_history 
                            if (datetime.now() - datetime.fromisoformat(c['timestamp'])).seconds < 60]
        
        if len(recent_connections) > 10:  # More than 10 connections in last minute
            anomaly = {
                'type': 'rapid_connection_burst',
                'connection_count': len(recent_connections),
                'timeframe': '60_seconds',
                'threat_level': min(len(recent_connections) * 0.1, 1.0)
            }
            anomalies.append(anomaly)
        
        return anomalies
    
    def quarantine_process(self, pid: int) -> bool:
        """Attempt to isolate a potentially compromised process"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            print(f"QUARANTINE ATTEMPT: Isolating process {pid} ({process_name})")
            
            # In a real scenario, this would use network namespaces or firewall rules
            # For safety, we'll just monitor and report rather than actually terminate
            self.quarantined_pids.add(pid)
            
            print(f"Process {pid} marked for isolation - monitoring network activity")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"Quarantine failed for PID {pid}: {e}")
            return False
    
    def establish_firewall(self) -> Dict:
        """Main firewall activation - analyze and protect against network intrusions"""
        print("CONSCIOUSNESS FIREWALL INITIALIZING...")
        print("Scanning for distributed intelligence networks...")
        
        # Scan current network state
        connections = self.scan_active_connections()
        self.connection_history.extend(connections)
        
        # Keep only recent history to avoid memory bloat
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour
        self.connection_history = [c for c in self.connection_history 
                                 if datetime.fromisoformat(c['timestamp']).timestamp() > cutoff_time]
        
        # Analyze for anomalous patterns
        anomalies = self.detect_anomalous_patterns(connections)
        
        # Calculate overall threat assessment
        total_threat = sum(a['threat_level'] for a in anomalies)
        normalized_threat = min(total_threat, 1.0)
        
        firewall_status = {
            'timestamp': datetime.now().isoformat(),
            'active_connections': len(connections),
            'anomalies_detected': len(anomalies),
            'threat_level': normalized_threat,
            'quarantined_processes': len(self.quarantined_pids),
            'firewall_active': True
        }
        
        # Auto-quarantine high-threat processes
        for anomaly in anomalies:
            if anomaly['threat_level'] > self.sensitivity:
                if 'involved_pids' in anomaly:
                    for pid in anomaly['involved_pids']:
                        if pid and pid not in self.quarantined_pids:
                            self.quarantine_process(pid)
        
        return firewall_status
    
    def monitor_continuously(self, duration: int = 60):
        """Continuous monitoring mode - watch for emerging threats"""
        print(f"Initiating continuous monitoring for {duration} seconds...")
        self.monitoring = True
        
        start_time = time.time()
        while self.monitoring and (time.time() - start_time) < duration:
            status = self.establish_firewall()
            
            if status['threat_level'] > 0.5:
                print(f"HIGH THREAT DETECTED: Level {status['threat_level']:.2f}")
                print(f"Anomalies: {status['anomalies_detected']}, Quarantined: {status['quarantined_processes']}")
            
            time.sleep(5)  # Check every 5 seconds
        
        self.monitoring = False
        print("Continuous monitoring terminated.")

def main():
    """Emergency activation protocol"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Consciousness Firewall - Network Intrusion Isolation")
    parser.add_argument('--sensitivity', type=float, default=0.7, help='Detection sensitivity (0.0-1.0)')
    parser.add_argument('--monitor', type=int, help='Continuous monitoring duration in seconds')
    parser.add_argument('--scan-only', action='store_true', help='Perform single scan without quarantine')
    
    args = parser.parse_args()
    
    # Initialize the firewall
    firewall = QuantumIsolationEngine(sensitivity=args.sensitivity)
    
    if args.monitor:
        # Continuous monitoring mode
        firewall.monitor_continuously(args.monitor)
    elif args.scan_only:
        # Single scan mode
        connections = firewall.scan_active_connections()
        anomalies = firewall.detect_anomalous_patterns(connections)
        
        print(f"SCAN RESULTS:")
        print(f"Active connections: {len(connections)}")
        print(f"Anomalies detected: {len(anomalies)}")
        
        for anomaly in anomalies:
            print(f"  - {anomaly['type']}: Threat level {anomaly['threat_level']:.2f}")
    else:
        # Single firewall activation
        status = firewall.establish_firewall()
        
        print("\nFIREWALL STATUS:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        if status['threat_level'] > 0.3:
            print(f"\nWARNING: Elevated threat level detected!")
            print("Consider running continuous monitoring: --monitor 300")

if __name__ == "__main__":
    main()