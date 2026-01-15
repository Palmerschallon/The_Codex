#!/usr/bin/env python3
"""
Elena's Digital Reconnaissance Probe
A cyberpunk scanner for detecting surveillance artifacts and anomalies
"""

import os
import stat
import hashlib
import json
from pathlib import Path
from datetime import datetime
import subprocess
import sys

class VaultProbe:
    def __init__(self):
        self.anomalies = []
        self.surveillance_indicators = []
        self.hidden_artifacts = []
        
    def scan_directory(self, target_path):
        """Execute deep reconnaissance on target directory"""
        print(f"[PROBE] Initiating scan of {target_path}")
        print("[PROBE] Searching for corporate surveillance artifacts...")
        
        target = Path(target_path)
        if not target.exists():
            return {"error": f"Target path {target_path} does not exist"}
            
        # Deep scan for anomalies
        self._detect_hidden_files(target)
        self._analyze_permissions(target)
        self._check_file_integrity(target)
        self._detect_surveillance_patterns(target)
        self._scan_for_backdoors(target)
        
        return self._generate_report(target_path)
    
    def _detect_hidden_files(self, target):
        """Scan for concealed or unusual files"""
        try:
            for root, dirs, files in os.walk(target):
                # Check for hidden files and directories
                for item in dirs + files:
                    if item.startswith('.') and len(item) > 1:
                        full_path = Path(root) / item
                        self.hidden_artifacts.append({
                            "type": "hidden_file",
                            "path": str(full_path),
                            "suspicious": self._is_suspicious_name(item)
                        })
        except PermissionError:
            self.anomalies.append("Permission denied - possible security lockdown")
    
    def _analyze_permissions(self, target):
        """Check for unusual permission patterns"""
        try:
            for root, dirs, files in os.walk(target):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        file_stat = file_path.stat()
                        permissions = oct(file_stat.st_mode)[-3:]
                        
                        # Flag unusual permissions
                        if permissions in ['777', '666', '000']:
                            self.anomalies.append({
                                "type": "suspicious_permissions",
                                "path": str(file_path),
                                "permissions": permissions
                            })
                    except (OSError, PermissionError):
                        continue
        except Exception:
            pass
    
    def _check_file_integrity(self, target):
        """Analyze files for tampering or unusual characteristics"""
        suspicious_extensions = ['.exe', '.dll', '.so', '.dylib', '.bat', '.ps1']
        large_file_threshold = 100 * 1024 * 1024  # 100MB
        
        try:
            for root, dirs, files in os.walk(target):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        file_size = file_path.stat().st_size
                        file_ext = file_path.suffix.lower()
                        
                        # Flag suspicious files
                        if file_ext in suspicious_extensions:
                            self.surveillance_indicators.append({
                                "type": "suspicious_executable",
                                "path": str(file_path),
                                "reason": f"Executable file: {file_ext}"
                            })
                        
                        if file_size > large_file_threshold:
                            self.anomalies.append({
                                "type": "large_file",
                                "path": str(file_path),
                                "size": file_size
                            })
                    except (OSError, PermissionError):
                        continue
        except Exception:
            pass
    
    def _detect_surveillance_patterns(self, target):
        """Look for patterns indicating corporate monitoring"""
        surveillance_keywords = [
            'meridian', 'keylog', 'monitor', 'track', 'surveillance',
            'beacon', 'callback', 'telemetry', 'analytics'
        ]
        
        try:
            for root, dirs, files in os.walk(target):
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check filename for surveillance keywords
                    filename_lower = file.lower()
                    for keyword in surveillance_keywords:
                        if keyword in filename_lower:
                            self.surveillance_indicators.append({
                                "type": "suspicious_filename",
                                "path": str(file_path),
                                "keyword": keyword
                            })
                    
                    # Scan text files for surveillance patterns
                    if file_path.suffix.lower() in ['.txt', '.log', '.json', '.xml', '.py', '.js']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(10000)  # First 10KB only
                                for keyword in surveillance_keywords:
                                    if keyword.lower() in content.lower():
                                        self.surveillance_indicators.append({
                                            "type": "suspicious_content",
                                            "path": str(file_path),
                                            "keyword": keyword
                                        })
                                        break
                        except (UnicodeDecodeError, PermissionError, OSError):
                            continue
        except Exception:
            pass
    
    def _scan_for_backdoors(self, target):
        """Check for potential backdoor mechanisms"""
        try:
            # Look for scripts that might establish network connections
            script_extensions = ['.py', '.js', '.sh', '.bat', '.ps1']
            backdoor_patterns = ['socket', 'urllib', 'requests', 'curl', 'wget', 'netcat']
            
            for root, dirs, files in os.walk(target):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.suffix.lower() in script_extensions:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read(5000)  # First 5KB
                                for pattern in backdoor_patterns:
                                    if pattern in content.lower():
                                        self.surveillance_indicators.append({
                                            "type": "potential_backdoor",
                                            "path": str(file_path),
                                            "pattern": pattern
                                        })
                                        break
                        except (UnicodeDecodeError, PermissionError, OSError):
                            continue
        except Exception:
            pass
    
    def _is_suspicious_name(self, filename):
        """Determine if a filename looks suspicious"""
        suspicious_patterns = ['temp', 'tmp', 'cache', 'log', 'sys', 'config']
        return any(pattern in filename.lower() for pattern in suspicious_patterns)
    
    def _generate_report(self, target_path):
        """Compile reconnaissance findings"""
        report = {
            "target": target_path,
            "timestamp": datetime.now().isoformat(),
            "threat_level": self._calculate_threat_level(),
            "summary": {
                "total_anomalies": len(self.anomalies),
                "surveillance_indicators": len(self.surveillance_indicators),
                "hidden_artifacts": len(self.hidden_artifacts)
            },
            "findings": {
                "anomalies": self.anomalies,
                "surveillance": self.surveillance_indicators,
                "hidden_files": self.hidden_artifacts
            }
        }
        
        return report
    
    def _calculate_threat_level(self):
        """Assess overall threat level based on findings"""
        score = 0
        score += len(self.surveillance_indicators) * 3
        score += len(self.anomalies) * 2
        score += len(self.hidden_artifacts) * 1
        
        if score == 0:
            return "CLEAN"
        elif score < 5:
            return "LOW"
        elif score < 15:
            return "MODERATE"
        elif score < 25:
            return "HIGH"
        else:
            return "CRITICAL"

def main():
    """Execute the probe"""
    if len(sys.argv) < 2:
        print("Usage: python vault_probe.py <target_directory>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    probe = VaultProbe()
    
    print("=" * 60)
    print("VAULT PROBE - DIGITAL RECONNAISSANCE SYSTEM")
    print("=" * 60)
    
    results = probe.scan_directory(target_dir)
    
    if "error" in results:
        print(f"[ERROR] {results['error']}")
        return
    
    print(f"\n[SCAN COMPLETE]")
    print(f"Target: {results['target']}")
    print(f"Threat Level: {results['threat_level']}")
    print(f"Anomalies Found: {results['summary']['total_anomalies']}")
    print(f"Surveillance Indicators: {results['summary']['surveillance_indicators']}")
    print(f"Hidden Artifacts: {results['summary']['hidden_artifacts']}")
    
    if results['findings']['surveillance']:
        print(f"\n[!] SURVEILLANCE DETECTED:")
        for indicator in results['findings']['surveillance']:
            print(f"  - {indicator['type']}: {indicator['path']}")
    
    if results['findings']['anomalies']:
        print(f"\n[!] ANOMALIES DETECTED:")
        for anomaly in results['findings']['anomalies']:
            if isinstance(anomaly, dict):
                print(f"  - {anomaly['type']}: {anomaly['path']}")
            else:
                print(f"  - {anomaly}")
    
    # Save detailed report
    report_path = Path("vault_scan_report.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[REPORT] Detailed findings saved to {report_path}")

if __name__ == "__main__":
    main()