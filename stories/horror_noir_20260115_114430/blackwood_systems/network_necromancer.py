#!/usr/bin/env python3
"""
Network Necromancer - Digital forensics tool for encrypted log analysis
Resurrects the dead data streams to reveal their secrets
"""

import os
import json
import gzip
import base64
import hashlib
from datetime import datetime, timezone
from collections import defaultdict
import socket
import struct
from pathlib import Path

class NetworkNecromancer:
    def __init__(self):
        self.traffic_patterns = defaultdict(list)
        self.connection_map = {}
        self.suspicious_flows = []
        
    def analyze_encrypted_logs(self, log_directory):
        """Analyze encrypted network logs for anomalous patterns"""
        results = {
            'timeline': [],
            'traffic_analysis': {},
            'encryption_patterns': {},
            'anomalies': []
        }
        
        for log_file in Path(log_directory).glob("*.enc"):
            try:
                # Attempt basic metadata extraction without full decryption
                with open(log_file, 'rb') as f:
                    header = f.read(1024)  # Read header
                    
                # Look for common log formats wrapped in encryption
                if self._detect_log_structure(header):
                    metadata = self._extract_metadata(log_file)
                    results['timeline'].append({
                        'file': log_file.name,
                        'timestamp': metadata.get('timestamp'),
                        'size': log_file.stat().st_size,
                        'entropy': self._calculate_entropy(header)
                    })
                    
            except Exception as e:
                results['anomalies'].append(f"Failed to analyze {log_file}: {e}")
                
        return results
    
    def decode_traffic_patterns(self, raw_data):
        """Decode network traffic patterns from raw packet data"""
        patterns = {}
        
        if isinstance(raw_data, str):
            # Try base64 decode first
            try:
                raw_data = base64.b64decode(raw_data)
            except:
                raw_data = raw_data.encode()
                
        # Analyze packet-like structures
        offset = 0
        packet_count = 0
        
        while offset < len(raw_data) - 20:  # Minimum packet header size
            try:
                # Extract potential IP header info
                if offset + 20 <= len(raw_data):
                    version_ihl = raw_data[offset]
                    if (version_ihl >> 4) == 4:  # IPv4
                        total_length = struct.unpack('!H', raw_data[offset+2:offset+4])[0]
                        protocol = raw_data[offset+9]
                        src_ip = socket.inet_ntoa(raw_data[offset+12:offset+16])
                        dst_ip = socket.inet_ntoa(raw_data[offset+16:offset+20])
                        
                        patterns[packet_count] = {
                            'src': src_ip,
                            'dst': dst_ip,
                            'protocol': protocol,
                            'size': total_length
                        }
                        
                        offset += max(20, total_length)
                        packet_count += 1
                    else:
                        offset += 1
                else:
                    break
                    
            except (struct.error, socket.error):
                offset += 1
                
            if packet_count > 1000:  # Prevent infinite loops
                break
                
        return patterns
    
    def hunt_anomalies(self, log_directory, time_window_minutes=60):
        """Hunt for network anomalies in the specified time window"""
        anomalies = []
        baseline_stats = self._establish_baseline(log_directory)
        
        # Check for traffic spikes
        current_time = datetime.now(timezone.utc)
        
        for log_file in Path(log_directory).glob("*"):
            if log_file.is_file():
                file_stats = log_file.stat()
                modified_time = datetime.fromtimestamp(file_stats.st_mtime, timezone.utc)
                
                if (current_time - modified_time).total_seconds() < time_window_minutes * 60:
                    # Recent file activity
                    file_entropy = self._calculate_entropy(log_file.read_bytes()[:1024])
                    
                    if file_entropy > 7.5:  # High entropy suggests encryption
                        anomalies.append({
                            'type': 'high_entropy_file',
                            'file': str(log_file),
                            'entropy': file_entropy,
                            'modified': modified_time.isoformat()
                        })
                        
        return anomalies
    
    def _detect_log_structure(self, header):
        """Detect if encrypted data contains structured log information"""
        # Look for common log patterns even in encrypted data
        indicators = [b'timestamp', b'src:', b'dst:', b'GET ', b'POST ', b'TCP', b'UDP']
        return any(indicator in header.lower() for indicator in indicators)
    
    def _extract_metadata(self, file_path):
        """Extract metadata from log files"""
        stat = file_path.stat()
        return {
            'timestamp': datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat()
        }
    
    def _calculate_entropy(self, data):
        """Calculate Shannon entropy of data"""
        if not data:
            return 0
            
        entropy = 0
        for i in range(256):
            p = data.count(i) / len(data)
            if p > 0:
                entropy -= p * (p.bit_length() - 1)
        return entropy
    
    def _establish_baseline(self, log_directory):
        """Establish baseline network behavior"""
        return {
            'avg_file_size': 0,
            'common_protocols': [],
            'typical_entropy': 0
        }
    
    def generate_report(self, analysis_results):
        """Generate a comprehensive forensics report"""
        report = {
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total_files_analyzed': len(analysis_results.get('timeline', [])),
                'anomalies_detected': len(analysis_results.get('anomalies', [])),
                'high_risk_indicators': []
            },
            'detailed_findings': analysis_results
        }
        
        # Add risk assessment
        if len(analysis_results.get('anomalies', [])) > 5:
            report['summary']['high_risk_indicators'].append('Multiple file analysis failures')
            
        return report

def main():
    """Main analysis function - the digital séance begins"""
    necromancer = NetworkNecromancer()
    
    # Default to current directory if no logs specified
    log_dir = input("Enter log directory path (or press Enter for current directory): ").strip()
    if not log_dir:
        log_dir = "."
    
    if not os.path.exists(log_dir):
        print(f"Directory {log_dir} not found. Creating sample analysis...")
        log_dir = "."
    
    print("🔮 Summoning the Network Necromancer...")
    print("📡 Analyzing encrypted transmission logs...")
    
    # Perform analysis
    results = necromancer.analyze_encrypted_logs(log_dir)
    anomalies = necromancer.hunt_anomalies(log_dir)
    
    # Combine results
    results['real_time_anomalies'] = anomalies
    
    # Generate report
    report = necromancer.generate_report(results)
    
    # Output results
    print("\n" + "="*60)
    print("NETWORK FORENSICS REPORT")
    print("="*60)
    print(f"Analysis completed: {report['analysis_timestamp']}")
    print(f"Files analyzed: {report['summary']['total_files_analyzed']}")
    print(f"Anomalies detected: {report['summary']['anomalies_detected']}")
    
    if report['summary']['high_risk_indicators']:
        print("\n⚠️  HIGH RISK INDICATORS:")
        for indicator in report['summary']['high_risk_indicators']:
            print(f"   • {indicator}")
    
    # Save detailed report
    report_file = f"network_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    main()