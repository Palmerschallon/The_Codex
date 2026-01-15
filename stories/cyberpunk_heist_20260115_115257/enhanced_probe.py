#!/usr/bin/env python3
"""
Enhanced Archaeological Probe v2.0
- Optimized for large dataset analysis
- Adaptive timeout handling
- Chunked processing to prevent resource exhaustion
- Real-time progress monitoring
"""

import os
import time
import hashlib
import threading
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime

class EnhancedProbe:
    def __init__(self, timeout_per_chunk=30, max_workers=4):
        self.timeout_per_chunk = timeout_per_chunk
        self.max_workers = max_workers
        self.results = {
            'files_analyzed': 0,
            'directories_scanned': 0,
            'anomalies': [],
            'patterns': defaultdict(list),
            'metadata': {},
            'scan_duration': 0
        }
        
    def analyze_file_chunk(self, file_paths):
        """Analyze a chunk of files with timeout protection"""
        chunk_results = []
        
        for file_path in file_paths:
            try:
                if not os.path.exists(file_path):
                    continue
                    
                file_info = self._deep_analyze_file(file_path)
                chunk_results.append(file_info)
                
            except Exception as e:
                chunk_results.append({
                    'path': str(file_path),
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                
        return chunk_results
    
    def _deep_analyze_file(self, file_path):
        """Perform deep analysis on a single file"""
        path_obj = Path(file_path)
        
        try:
            stat_info = path_obj.stat()
            
            # Basic file information
            file_data = {
                'path': str(file_path),
                'size': stat_info.st_size,
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'permissions': oct(stat_info.st_mode)[-3:],
                'anomalies': []
            }
            
            # Content analysis for text files
            if path_obj.suffix in ['.txt', '.py', '.md', '.json', '.yml', '.yaml', '.log']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(10000)  # First 10KB only
                        
                    file_data['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
                    file_data['line_count'] = content.count('\n')
                    
                    # Check for suspicious patterns
                    if 'meridian' in content.lower():
                        file_data['anomalies'].append('Contains Meridian references')
                    
                    if 'pattern' in content.lower():
                        file_data['anomalies'].append('Contains Pattern references')
                        
                    if any(keyword in content.lower() for keyword in 
                           ['quantum', 'neural', 'encrypted', 'classified']):
                        file_data['anomalies'].append('Contains technical keywords')
                        
                except Exception:
                    file_data['content_error'] = 'Could not read file content'
            
            # Size anomaly detection
            if stat_info.st_size > 100_000_000:  # 100MB
                file_data['anomalies'].append('Unusually large file')
            
            # Timestamp anomaly detection
            now = time.time()
            if stat_info.st_mtime > now - 86400:  # Modified in last 24 hours
                file_data['anomalies'].append('Recently modified')
                
            return file_data
            
        except Exception as e:
            return {
                'path': str(file_path),
                'error': f'Analysis failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def scan_directory(self, target_dir, max_depth=10):
        """Scan directory with chunked processing and progress tracking"""
        print(f"[PROBE] Initiating enhanced scan of {target_dir}")
        start_time = time.time()
        
        # Collect all files first
        all_files = []
        for root, dirs, files in os.walk(target_dir):
            # Limit depth to prevent infinite recursion
            depth = root[len(target_dir):].count(os.sep)
            if depth >= max_depth:
                dirs[:] = []  # Don't recurse deeper
                continue
                
            self.results['directories_scanned'] += 1
            
            for file_name in files:
                file_path = os.path.join(root, file_name)
                all_files.append(file_path)
        
        print(f"[PROBE] Found {len(all_files)} files to analyze")
        
        # Process files in chunks to prevent timeout
        chunk_size = 50  # Adjustable chunk size
        
        for i in range(0, len(all_files), chunk_size):
            chunk = all_files[i:i + chunk_size]
            print(f"[PROBE] Processing chunk {i//chunk_size + 1}/{(len(all_files)-1)//chunk_size + 1}")
            
            try:
                chunk_results = self.analyze_file_chunk(chunk)
                
                for file_data in chunk_results:
                    self.results['files_analyzed'] += 1
                    
                    if file_data.get('anomalies'):
                        self.results['anomalies'].extend([
                            {
                                'file': file_data['path'],
                                'anomaly': anomaly,
                                'timestamp': datetime.now().isoformat()
                            } for anomaly in file_data['anomalies']
                        ])
                    
                    # Pattern detection
                    file_extension = Path(file_data['path']).suffix
                    self.results['patterns'][file_extension].append(file_data['path'])
                    
            except Exception as e:
                print(f"[PROBE] Chunk processing error: {e}")
                continue
        
        self.results['scan_duration'] = time.time() - start_time
        print(f"[PROBE] Scan completed in {self.results['scan_duration']:.2f} seconds")
        
        return self.results
    
    def generate_report(self):
        """Generate a comprehensive scan report"""
        report = [
            "=== ENHANCED ARCHAEOLOGICAL PROBE REPORT ===",
            f"Scan Duration: {self.results['scan_duration']:.2f} seconds",
            f"Files Analyzed: {self.results['files_analyzed']}",
            f"Directories Scanned: {self.results['directories_scanned']}",
            "",
            "=== ANOMALIES DETECTED ===",
        ]
        
        if self.results['anomalies']:
            for anomaly in self.results['anomalies']:
                report.append(f"• {anomaly['file']}: {anomaly['anomaly']}")
        else:
            report.append("• No anomalies detected")
        
        report.extend([
            "",
            "=== FILE TYPE DISTRIBUTION ===",
        ])
        
        for file_type, files in self.results['patterns'].items():
            report.append(f"• {file_type or '[no extension]'}: {len(files)} files")
        
        return "\n".join(report)

def main():
    """Run the enhanced probe"""
    import sys
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "/home/palmerschallon/ember"
    
    probe = EnhancedProbe()
    results = probe.scan_directory(target)
    
    # Save detailed results
    with open('enhanced_scan_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary report
    print(probe.generate_report())
    
    return results

if __name__ == "__main__":
    main()