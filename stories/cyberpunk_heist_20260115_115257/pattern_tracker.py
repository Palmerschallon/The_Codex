#!/usr/bin/env python3
"""
Elena's Pattern Recognition System
Tracks resonances between code artifacts across time and space
"""

import os
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class PatternTracker:
    def __init__(self, target_directory):
        self.target_dir = Path(target_directory)
        self.resonance_map = defaultdict(list)
        self.temporal_signatures = {}
        
    def calculate_pattern_hash(self, file_path):
        """Generate a hash that identifies pattern resonances, not exact matches"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Create a pattern signature based on structure, not content
            structure_hash = hashlib.sha256()
            
            # Analyze file size patterns
            size_pattern = len(content) % 1000
            structure_hash.update(str(size_pattern).encode())
            
            # Analyze byte frequency patterns (ignore actual values)
            byte_freq = [0] * 256
            for byte in content:
                byte_freq[byte] += 1
            
            # Use frequency distribution shape, not actual frequencies
            freq_pattern = [1 if f > len(content) * 0.01 else 0 for f in byte_freq]
            structure_hash.update(bytes(freq_pattern))
            
            return structure_hash.hexdigest()[:16]
        except Exception:
            return None
    
    def scan_for_resonances(self):
        """Scan target directory for pattern resonances"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'target_directory': str(self.target_dir),
            'resonances': [],
            'temporal_clusters': {},
            'anomaly_score': 0
        }
        
        if not self.target_dir.exists():
            results['error'] = 'Target directory not found'
            return results
        
        pattern_counts = defaultdict(int)
        file_patterns = {}
        
        # Recursively scan all files
        for file_path in self.target_dir.rglob('*'):
            if file_path.is_file():
                pattern = self.calculate_pattern_hash(file_path)
                if pattern:
                    pattern_counts[pattern] += 1
                    file_patterns[str(file_path.relative_to(self.target_dir))] = pattern
                    
                    # Record temporal data
                    try:
                        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        self.temporal_signatures[pattern] = mod_time.isoformat()
                    except Exception:
                        pass
        
        # Identify resonances (patterns appearing multiple times)
        resonant_patterns = {p: c for p, c in pattern_counts.items() if c > 1}
        
        for pattern, count in resonant_patterns.items():
            matching_files = [f for f, p in file_patterns.items() if p == pattern]
            results['resonances'].append({
                'pattern_id': pattern,
                'resonance_count': count,
                'affected_files': matching_files,
                'temporal_signature': self.temporal_signatures.get(pattern, 'unknown')
            })
        
        # Calculate temporal clustering
        time_clusters = defaultdict(list)
        for pattern, timestamp in self.temporal_signatures.items():
            if pattern in resonant_patterns:
                # Group by year-month for clustering
                try:
                    dt = datetime.fromisoformat(timestamp)
                    cluster_key = f"{dt.year}-{dt.month:02d}"
                    time_clusters[cluster_key].append(pattern)
                except Exception:
                    pass
        
        results['temporal_clusters'] = {k: len(v) for k, v in time_clusters.items()}
        
        # Calculate anomaly score based on pattern density
        total_files = len(file_patterns)
        total_resonances = sum(resonant_patterns.values())
        if total_files > 0:
            results['anomaly_score'] = (total_resonances / total_files) * 100
        
        return results
    
    def generate_report(self, output_file=None):
        """Generate a comprehensive pattern analysis report"""
        scan_results = self.scan_for_resonances()
        
        report = f"""
PATTERN RESONANCE ANALYSIS REPORT
Generated: {scan_results['timestamp']}
Target: {scan_results['target_directory']}

ANOMALY SCORE: {scan_results.get('anomaly_score', 0):.2f}%
{'HIGH RESONANCE DETECTED' if scan_results.get('anomaly_score', 0) > 10 else 'NORMAL PATTERNS'}

RESONANT PATTERNS DETECTED: {len(scan_results['resonances'])}

"""
        
        for i, resonance in enumerate(scan_results['resonances'], 1):
            report += f"""
Pattern #{i} - ID: {resonance['pattern_id']}
  Resonance Count: {resonance['resonance_count']}
  Temporal Signature: {resonance['temporal_signature']}
  Affected Files: {len(resonance['affected_files'])}
    {chr(10).join(f"    - {f}" for f in resonance['affected_files'][:5])}
    {'    ... and more' if len(resonance['affected_files']) > 5 else ''}
"""
        
        if scan_results['temporal_clusters']:
            report += f"""
TEMPORAL CLUSTERING:
{chr(10).join(f"  {period}: {count} resonant patterns" for period, count in scan_results['temporal_clusters'].items())}
"""
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
        
        return report, scan_results

def main():
    import sys
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Enter directory to scan for pattern resonances: ")
    
    tracker = PatternTracker(target)
    report, data = tracker.generate_report()
    print(report)
    
    if data.get('anomaly_score', 0) > 15:
        print("\n[WARNING] HIGH ANOMALY SCORE DETECTED")
        print("This directory shows signs of Pattern influence.")

if __name__ == "__main__":
    main()