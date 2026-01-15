#!/usr/bin/env python3
"""
Network reconnaissance tool - analyzes target infrastructure
Originally developed for penetration testing and security audits
"""

import socket
import threading
import subprocess
import json
from datetime import datetime
import ipaddress

class NetworkRecon:
    def __init__(self):
        self.open_ports = {}
        self.services = {}
        self.vulnerabilities = []
        
    def scan_target(self, target_ip, port_range=(1, 1024)):
        """
        Scan target for open ports and running services
        Returns detailed network fingerprint
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Initiating scan on {target_ip}")
        
        def check_port(ip, port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    self.open_ports[port] = self._identify_service(ip, port)
                sock.close()
            except Exception:
                pass
        
        # Multi-threaded port scanning
        threads = []
        for port in range(port_range[0], port_range[1] + 1):
            thread = threading.Thread(target=check_port, args=(target_ip, port))
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= 50:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for thread in threads:
            thread.join()
            
        return self._generate_report(target_ip)
    
    def _identify_service(self, ip, port):
        """Attempt to identify service running on open port"""
        common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
            53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
            443: "HTTPS", 993: "IMAPS", 995: "POP3S"
        }
        return common_ports.get(port, "Unknown")
    
    def _generate_report(self, target):
        """Generate comprehensive scan report"""
        report = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "open_ports": self.open_ports,
            "total_open": len(self.open_ports),
            "security_notes": []
        }
        
        # Add security observations
        if 21 in self.open_ports:
            report["security_notes"].append("FTP detected - potential for credential interception")
        if 23 in self.open_ports:
            report["security_notes"].append("Telnet detected - unencrypted protocol")
        if 80 in self.open_ports and 443 not in self.open_ports:
            report["security_notes"].append("HTTP without HTTPS - potential security risk")
            
        return report

def main():
    recon = NetworkRecon()
    
    # Example usage
    target = input("Enter target IP address: ")
    
    try:
        # Validate IP address
        ipaddress.ip_address(target)
        
        print(f"Scanning {target}...")
        results = recon.scan_target(target)
        
        print(f"\n--- SCAN RESULTS ---")
        print(f"Target: {results['target']}")
        print(f"Open ports found: {results['total_open']}")
        
        for port, service in results['open_ports'].items():
            print(f"  Port {port}: {service}")
            
        if results['security_notes']:
            print(f"\nSecurity observations:")
            for note in results['security_notes']:
                print(f"  ! {note}")
                
    except ValueError:
        print("Invalid IP address format")
    except Exception as e:
        print(f"Scan failed: {e}")

if __name__ == "__main__":
    main()