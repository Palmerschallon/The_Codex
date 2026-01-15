#!/usr/bin/env python3
"""
Corporate Surveillance Detection Probe - "Echo Scan"
Detects suspicious files, permissions, and network traces
Written by Elena Vasquez - Ghost Protocol Collective
"""

import os
import stat
import hashlib
import socket
import subprocess
import json
from pathlib import Path
from datetime import datetime

class MeridianProbe:
    def __init__(self):
        self.anomalies = []
        self.scan_results = {
            'suspicious_files': [],
            'permission_anomalies': [],
            'network_traces': [],
            'hidden_artifacts': [],
            'metadata_analysis': {}
        }
    
    def scan_directory(self, target_path):
        """Main scanning function - analyzes directory for surveillance traces"""
        print(f"[ECHO SCAN] Initiating probe on: {target_path}")
        print("[ECHO SCAN] Scanning for corporate surveillance patterns...")
        
        target = Path(target_path)
        if not target.exists():
            print(f"[ERROR] Target directory does not exist: {target_path}")
            return self.scan_results
        
        # Scan for suspicious files
        self._scan_suspicious_files(target)
        
        # Analyze permissions
        self._analyze_permissions(target)
        
        # Check for hidden artifacts
        self._scan_hidden_files(target)
        
        # Analyze file metadata
        self._analyze_metadata(target)
        
        # Generate threat assessment
        self._generate_threat_report()
        
        return self.scan_results
    
    def _scan_suspicious_files(self, target):
        """Detect files with suspicious characteristics"""
        suspicious_extensions = ['.dll', '.so', '.bin', '.exe', '.bat', '.ps1', '.vbs']
        corporate_keywords = ['meridian', 'telemetry', 'tracker', 'monitor', 'surveillance']
        
        for root, dirs, files in os.walk(target):
            for file in files:
                filepath = Path(root) / file
                
                # Check extensions
                if filepath.suffix.lower() in suspicious_extensions:
                    self.scan_results['suspicious_files'].append({
                        'path': str(filepath),
                        'reason': f'Suspicious extension: {filepath.suffix}',
                        'size': filepath.stat().st_size if filepath.exists() else 0
                    })
                
                # Check for corporate keywords in filename
                filename_lower = file.lower()
                for keyword in corporate_keywords:
                    if keyword in filename_lower:
                        self.scan_results['suspicious_files'].append({
                            'path': str(filepath),
                            'reason': f'Corporate keyword detected: {keyword}',
                            'threat_level': 'HIGH'
                        })
    
    def _analyze_permissions(self, target):
        """Analyze file permissions for anomalies"""
        for root, dirs, files in os.walk(target):
            for item in files + dirs:
                try:
                    item_path = Path(root) / item
                    file_stat = item_path.stat()
                    mode = file_stat.st_mode
                    
                    # Check for world-writable files (potential backdoors)
                    if mode & stat.S_IWOTH:
                        self.scan_results['permission_anomalies'].append({
                            'path': str(item_path),
                            'issue': 'World-writable permissions',
                            'risk': 'Potential backdoor access'
                        })
                    
                    # Check for setuid/setgid (privilege escalation)
                    if mode & (stat.S_ISUID | stat.S_ISGID):
                        self.scan_results['permission_anomalies'].append({
                            'path': str(item_path),
                            'issue': 'SetUID/SetGID bit set',
                            'risk': 'Privilege escalation vector'
                        })
                        
                except (OSError, PermissionError):
                    # Can't access file - potentially suspicious
                    self.scan_results['permission_anomalies'].append({
                        'path': str(item_path),
                        'issue': 'Access denied',
                        'risk': 'Protected corporate asset'
                    })
    
    def _scan_hidden_files(self, target):
        """Detect hidden files and unusual artifacts"""
        for root, dirs, files in os.walk(target):
            # Include hidden files
            all_items = files + dirs
            for item in all_items:
                if item.startswith('.') and item not in ['.', '..']:
                    item_path = Path(root) / item
                    self.scan_results['hidden_artifacts'].append({
                        'path': str(item_path),
                        'type': 'hidden_file',
                        'note': 'Hidden files may contain surveillance tools'
                    })
    
    def _analyze_metadata(self, target):
        """Analyze directory metadata for patterns"""
        total_files = 0
        total_size = 0
        file_types = {}
        
        for root, dirs, files in os.walk(target):
            for file in files:
                filepath = Path(root) / file
                try:
                    if filepath.exists():
                        file_stat = filepath.stat()
                        total_files += 1
                        total_size += file_stat.st_size
                        
                        ext = filepath.suffix.lower()
                        file_types[ext] = file_types.get(ext, 0) + 1
                        
                except (OSError, PermissionError):
                    continue
        
        self.scan_results['metadata_analysis'] = {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'file_types': file_types,
            'scan_timestamp': datetime.now().isoformat()
        }
    
    def _generate_threat_report(self):
        """Generate overall threat assessment"""
        threat_score = 0
        threat_factors = []
        
        # Calculate threat based on findings
        threat_score += len(self.scan_results['suspicious_files']) * 3
        threat_score += len(self.scan_results['permission_anomalies']) * 2
        threat_score += len(self.scan_results['hidden_artifacts']) * 1
        
        if threat_score == 0:
            threat_level = "CLEAN"
            threat_factors.append("No surveillance traces detected")
        elif threat_score < 5:
            threat_level = "LOW"
            threat_factors.append("Minimal suspicious activity")
        elif threat_score < 10:
            threat_level = "MODERATE"
            threat_factors.append("Some anomalies detected - investigate further")
        else:
            threat_level = "HIGH"
            threat_factors.append("Multiple surveillance indicators - COMPROMISED")
        
        print(f"\n[ECHO SCAN COMPLETE]")
        print(f"Threat Level: {threat_level}")
        print(f"Threat Score: {threat_score}")
        print(f"Files Scanned: {self.scan_results['metadata_analysis'].get('total_files', 0)}")
        
        if self.scan_results['suspicious_files']:
            print(f"\nSUSPICIOUS FILES DETECTED: {len(self.scan_results['suspicious_files'])}")
            for file_info in self.scan_results['suspicious_files']:
                print(f"  • {file_info['path']} - {file_info['reason']}")
        
        if self.scan_results['permission_anomalies']:
            print(f"\nPERMISSION ANOMALIES: {len(self.scan_results['permission_anomalies'])}")
            for perm_info in self.scan_results['permission_anomalies']:
                print(f"  • {perm_info['path']} - {perm_info['issue']}")
        
        if self.scan_results['hidden_artifacts']:
            print(f"\nHIDDEN ARTIFACTS: {len(self.scan_results['hidden_artifacts'])}")
            for hidden in self.scan_results['hidden_artifacts']:
                print(f"  • {hidden['path']}")
        
        return threat_level

def main():
    """Run the probe with command line argument"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python meridian_probe.py <target_directory>")
        print("Example: python meridian_probe.py /home/palmerschallon/ember")
        return
    
    target_dir = sys.argv[1]
    probe = MeridianProbe()
    results = probe.scan_directory(target_dir)
    
    # Optionally save results to file
    results_file = Path("scan_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {results_file}")

if __name__ == "__main__":
    main()