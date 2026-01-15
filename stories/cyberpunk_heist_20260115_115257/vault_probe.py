#!/usr/bin/env python3
"""
Corporate Surveillance Detection Probe
Elena's custom scanner for detecting embedded watchers and data miners
"""

import os
import hashlib
import time
import json
from pathlib import Path
from collections import defaultdict
import mimetypes

class VaultProbe:
    def __init__(self):
        self.suspicious_patterns = {
            'hidden_executables': ['.exe', '.com', '.scr', '.pif'],
            'surveillance_extensions': ['.watcher', '.monitor', '.track', '.log'],
            'corporate_signatures': [
                b'MERIDIAN_CORP',
                b'NEURAL_BRIDGE',
                b'MEMORY_EDIT',
                b'ERASURE_PROTOCOL'
            ]
        }
        self.scan_results = defaultdict(list)
        
    def analyze_file_structure(self, root_path):
        """Analyze directory structure for anomalies"""
        structure_data = {
            'total_files': 0,
            'hidden_files': 0,
            'suspicious_files': [],
            'depth_analysis': defaultdict(int),
            'size_anomalies': []
        }
        
        for root, dirs, files in os.walk(root_path):
            depth = len(Path(root).parts) - len(Path(root_path).parts)
            structure_data['depth_analysis'][depth] += len(files)
            
            for file in files:
                file_path = Path(root) / file
                structure_data['total_files'] += 1
                
                # Check for hidden files
                if file.startswith('.'):
                    structure_data['hidden_files'] += 1
                    
                # Check for suspicious extensions
                if any(file.endswith(ext) for ext in self.suspicious_patterns['hidden_executables']):
                    structure_data['suspicious_files'].append(str(file_path))
                    
                # Check for size anomalies
                try:
                    size = file_path.stat().st_size
                    if size == 0 and not file.startswith('.'):
                        structure_data['size_anomalies'].append(f"Empty: {file_path}")
                    elif size > 100_000_000:  # 100MB+
                        structure_data['size_anomalies'].append(f"Large: {file_path} ({size:,} bytes)")
                except OSError:
                    pass
                    
        return structure_data
    
    def scan_for_corporate_signatures(self, root_path):
        """Scan files for corporate surveillance signatures"""
        matches = []
        
        for root, dirs, files in os.walk(root_path):
            for file in files:
                file_path = Path(root) / file
                
                # Only scan readable files under 10MB
                try:
                    if file_path.stat().st_size > 10_000_000:
                        continue
                        
                    # Try to read as binary
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        
                    for signature in self.suspicious_patterns['corporate_signatures']:
                        if signature in content:
                            matches.append({
                                'file': str(file_path),
                                'signature': signature.decode('utf-8', errors='ignore'),
                                'offset': content.find(signature)
                            })
                            
                except (OSError, PermissionError):
                    continue
                    
        return matches
    
    def generate_file_fingerprints(self, root_path):
        """Generate cryptographic fingerprints of all files"""
        fingerprints = {}
        
        for root, dirs, files in os.walk(root_path):
            for file in files:
                file_path = Path(root) / file
                
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        
                    # Generate multiple hashes for verification
                    md5_hash = hashlib.md5(content).hexdigest()
                    sha1_hash = hashlib.sha1(content).hexdigest()
                    
                    fingerprints[str(file_path)] = {
                        'md5': md5_hash,
                        'sha1': sha1_hash,
                        'size': len(content),
                        'modified': file_path.stat().st_mtime
                    }
                    
                except (OSError, PermissionError):
                    continue
                    
        return fingerprints
    
    def deep_scan(self, target_path):
        """Perform comprehensive vault security scan"""
        print(f"[VAULT_PROBE] Initiating deep scan of: {target_path}")
        print("[VAULT_PROBE] Scanning for corporate surveillance...")
        
        target = Path(target_path)
        if not target.exists():
            return {'error': f'Target path does not exist: {target_path}'}
            
        scan_report = {
            'timestamp': time.time(),
            'target': str(target.absolute()),
            'structure': self.analyze_file_structure(target_path),
            'corporate_signatures': self.scan_for_corporate_signatures(target_path),
            'fingerprints': self.generate_file_fingerprints(target_path),
            'threat_level': 'UNKNOWN'
        }
        
        # Assess threat level
        signature_count = len(scan_report['corporate_signatures'])
        suspicious_files = len(scan_report['structure']['suspicious_files'])
        
        if signature_count > 0:
            scan_report['threat_level'] = 'CRITICAL'
        elif suspicious_files > 5:
            scan_report['threat_level'] = 'HIGH'
        elif scan_report['structure']['hidden_files'] > 10:
            scan_report['threat_level'] = 'MEDIUM'
        else:
            scan_report['threat_level'] = 'LOW'
            
        return scan_report
    
    def format_report(self, scan_data):
        """Format scan results for human readability"""
        if 'error' in scan_data:
            return f"ERROR: {scan_data['error']}"
            
        report = []
        report.append("=== VAULT PROBE SECURITY SCAN ===")
        report.append(f"Target: {scan_data['target']}")
        report.append(f"Threat Level: {scan_data['threat_level']}")
        report.append("")
        
        # Structure analysis
        struct = scan_data['structure']
        report.append(f"Files Analyzed: {struct['total_files']}")
        report.append(f"Hidden Files: {struct['hidden_files']}")
        report.append(f"Suspicious Files: {len(struct['suspicious_files'])}")
        
        if struct['suspicious_files']:
            report.append("Suspicious files detected:")
            for f in struct['suspicious_files'][:5]:  # Show first 5
                report.append(f"  - {f}")
                
        # Corporate signatures
        signatures = scan_data['corporate_signatures']
        if signatures:
            report.append(f"\n⚠️  CORPORATE SURVEILLANCE DETECTED: {len(signatures)} signatures")
            for sig in signatures:
                report.append(f"  - {sig['signature']} in {sig['file']}")
        else:
            report.append("\n✓ No corporate surveillance signatures detected")
            
        return "\n".join(report)

def quick_scan(path):
    """Quick scan function for immediate use"""
    probe = VaultProbe()
    results = probe.deep_scan(path)
    return probe.format_report(results)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python vault_probe.py <target_path>")
        sys.exit(1)
        
    target = sys.argv[1]
    print(quick_scan(target))