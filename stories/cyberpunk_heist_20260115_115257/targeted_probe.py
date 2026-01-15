#!/usr/bin/env python3
"""
Elena's Surgical Archaeological Scanner
A targeted reconnaissance tool for large digital excavation sites
"""

import os
import sys
from pathlib import Path
import time
from datetime import datetime

class TargetedArchaeologist:
    def __init__(self):
        self.anomalies = []
        self.scan_start = time.time()
        
    def identify_promising_sites(self, target_dir, max_depth=2):
        """Quick surface scan to identify the most interesting subdirectories"""
        promising_sites = []
        
        try:
            target_path = Path(target_dir)
            if not target_path.exists():
                return [f"Target directory not found: {target_dir}"]
            
            print(f"🔍 Scanning archaeological surface of: {target_dir}")
            
            # Quick directory enumeration
            subdirs = [d for d in target_path.iterdir() if d.is_dir()]
            
            for subdir in subdirs[:20]:  # Limit to first 20 for speed
                try:
                    file_count = len(list(subdir.rglob('*')))
                    size_mb = sum(f.stat().st_size for f in subdir.rglob('*') if f.is_file()) / 1024 / 1024
                    
                    # Look for interesting patterns
                    has_python = any(f.suffix == '.py' for f in subdir.rglob('*.py'))
                    has_config = any(f.name in ['config', '.env', 'settings'] for f in subdir.rglob('*'))
                    
                    score = 0
                    if has_python: score += 2
                    if has_config: score += 1
                    if size_mb > 1: score += 1
                    if file_count > 10: score += 1
                    
                    if score >= 2:
                        promising_sites.append({
                            'path': str(subdir),
                            'score': score,
                            'files': file_count,
                            'size_mb': round(size_mb, 2),
                            'has_python': has_python,
                            'has_config': has_config
                        })
                        
                except (PermissionError, OSError):
                    continue
                    
        except Exception as e:
            return [f"Surface scan failed: {str(e)}"]
            
        # Sort by score
        promising_sites.sort(key=lambda x: x['score'], reverse=True)
        return promising_sites[:5]  # Return top 5 sites
    
    def deep_scan_site(self, site_path):
        """Perform detailed analysis of a specific site"""
        try:
            path = Path(site_path)
            analysis = {
                'path': site_path,
                'total_files': 0,
                'python_files': [],
                'config_files': [],
                'large_files': [],
                'recent_files': [],
                'anomalies': []
            }
            
            current_time = time.time()
            
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        analysis['total_files'] += 1
                        
                        # Python files
                        if file_path.suffix == '.py':
                            analysis['python_files'].append(str(file_path))
                        
                        # Config files
                        if file_path.name in ['config', '.env', 'settings', 'config.json', 'settings.py']:
                            analysis['config_files'].append(str(file_path))
                        
                        # Large files
                        if stat.st_size > 10 * 1024 * 1024:  # > 10MB
                            analysis['large_files'].append({
                                'path': str(file_path),
                                'size_mb': round(stat.st_size / 1024 / 1024, 2)
                            })
                        
                        # Recently modified files
                        if current_time - stat.st_mtime < 30 * 24 * 3600:  # Last 30 days
                            analysis['recent_files'].append({
                                'path': str(file_path),
                                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
                        
                        # Look for anomalies
                        if stat.st_size == 0:
                            analysis['anomalies'].append(f"Empty file: {file_path}")
                        
                        if file_path.name.startswith('.'):
                            analysis['anomalies'].append(f"Hidden file: {file_path}")
                            
                    except (PermissionError, OSError):
                        continue
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}

def main():
    if len(sys.argv) < 2:
        print("Usage: python targeted_probe.py <target_directory> [--deep-scan]")
        return
    
    target = sys.argv[1]
    deep_scan = '--deep-scan' in sys.argv
    
    scanner = TargetedArchaeologist()
    
    print("🏛️  Elena's Archaeological Scanner v2.0")
    print("=" * 50)
    
    # Surface scan
    sites = scanner.identify_promising_sites(target)
    
    if isinstance(sites, list) and len(sites) > 0 and isinstance(sites[0], str):
        print("❌ Error:", sites[0])
        return
    
    if not sites:
        print("🔍 No promising archaeological sites detected.")
        return
    
    print(f"📍 Found {len(sites)} promising excavation sites:")
    print()
    
    for i, site in enumerate(sites, 1):
        print(f"{i}. {site['path']}")
        print(f"   Score: {site['score']}/5 | Files: {site['files']} | Size: {site['size_mb']}MB")
        print(f"   Python: {'✓' if site['has_python'] else '✗'} | Config: {'✓' if site['has_config'] else '✗'}")
        print()
    
    if deep_scan and sites:
        print("🔬 Performing deep analysis of top site...")
        analysis = scanner.deep_scan_site(sites[0]['path'])
        
        if 'error' in analysis:
            print(f"❌ Deep scan failed: {analysis['error']}")
        else:
            print(f"📊 Deep Analysis Results:")
            print(f"   Total files: {analysis['total_files']}")
            print(f"   Python files: {len(analysis['python_files'])}")
            print(f"   Config files: {len(analysis['config_files'])}")
            print(f"   Large files: {len(analysis['large_files'])}")
            print(f"   Recent activity: {len(analysis['recent_files'])} files")
            print(f"   Anomalies detected: {len(analysis['anomalies'])}")

if __name__ == "__main__":
    main()