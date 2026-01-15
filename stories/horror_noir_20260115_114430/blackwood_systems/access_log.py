#!/usr/bin/env python3
"""
Blackwood Systems - Security Access Log Analyzer
Emergency forensics tool for investigating unusual access patterns
"""

import csv
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re

class AccessLogAnalyzer:
    def __init__(self, log_file=None):
        self.entries = []
        self.suspicious_patterns = []
        
    def load_csv_log(self, file_path):
        """Load access logs from CSV format"""
        try:
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                self.entries = list(reader)
                return len(self.entries)
        except FileNotFoundError:
            print(f"Log file {file_path} not found")
            return 0
    
    def analyze_time_patterns(self):
        """Detect unusual access time patterns"""
        hour_counts = Counter()
        date_counts = defaultdict(int)
        
        for entry in self.entries:
            try:
                timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                hour_counts[timestamp.hour] += 1
                date_counts[timestamp.date()] += 1
            except (KeyError, ValueError):
                continue
        
        # Flag unusual late night activity (2-5 AM)
        late_night_access = sum(hour_counts[h] for h in range(2, 6))
        total_access = sum(hour_counts.values())
        
        if total_access > 0 and (late_night_access / total_access) > 0.3:
            self.suspicious_patterns.append(f"High late-night activity: {late_night_access} accesses between 2-5 AM")
        
        return {
            'hourly_distribution': dict(hour_counts),
            'daily_counts': dict(date_counts),
            'late_night_percentage': late_night_access / total_access if total_access > 0 else 0
        }
    
    def find_simultaneous_access(self, window_minutes=5):
        """Find groups of users accessing systems simultaneously"""
        simultaneous_groups = []
        
        # Sort entries by timestamp
        sorted_entries = sorted(self.entries, key=lambda x: x.get('timestamp', ''))
        
        for i, entry in enumerate(sorted_entries):
            try:
                base_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                group = [entry]
                
                # Look for other entries within the time window
                for j in range(i+1, len(sorted_entries)):
                    other_entry = sorted_entries[j]
                    other_time = datetime.fromisoformat(other_entry['timestamp'].replace('Z', '+00:00'))
                    
                    if other_time - base_time <= timedelta(minutes=window_minutes):
                        group.append(other_entry)
                    else:
                        break
                
                if len(group) >= 5:  # 5 or more simultaneous accesses
                    simultaneous_groups.append({
                        'timestamp': entry['timestamp'],
                        'count': len(group),
                        'users': list(set(e.get('user_id', 'unknown') for e in group))
                    })
            
            except (KeyError, ValueError):
                continue
        
        return simultaneous_groups
    
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        time_analysis = self.analyze_time_patterns()
        simultaneous = self.find_simultaneous_access()
        
        report = {
            'total_entries': len(self.entries),
            'analysis_timestamp': datetime.now().isoformat(),
            'time_patterns': time_analysis,
            'simultaneous_access_events': simultaneous,
            'suspicious_flags': self.suspicious_patterns
        }
        
        return report

def emergency_analysis(log_file):
    """Quick analysis for emergency situations"""
    analyzer = AccessLogAnalyzer()
    entries_loaded = analyzer.load_csv_log(log_file)
    
    if entries_loaded == 0:
        return {"error": "No log data available"}
    
    return analyzer.generate_report()

if __name__ == "__main__":
    # Emergency mode - analyze any CSV log file
    import sys
    if len(sys.argv) > 1:
        result = emergency_analysis(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python access_log.py <log_file.csv>")
        print("Analyzes access patterns for forensic investigation")