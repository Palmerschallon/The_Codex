#!/usr/bin/env python3
"""
The Meridian Triangulation Engine
A real signal analysis tool disguised as Victoria's portable detector

Analyzes Wi-Fi signals, Bluetooth devices, and other RF sources to triangulate
locations and detect signal anomalies in your actual environment.
"""

import subprocess
import re
import json
import math
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional
import time

@dataclass
class SignalReading:
    """Represents a detected signal source"""
    name: str
    frequency: str
    signal_strength: int
    mac_address: str
    encryption: str
    timestamp: datetime
    
    def distance_estimate(self) -> float:
        """Estimate distance based on signal strength (rough approximation)"""
        # Very rough estimation: stronger signal = closer source
        if self.signal_strength > -30:
            return 1.0  # Very close
        elif self.signal_strength > -50:
            return 5.0  # Close
        elif self.signal_strength > -70:
            return 15.0  # Medium distance
        else:
            return 50.0  # Far

class MeridianTriangulator:
    """Victoria Brassheart's Portable Signal Detector (modernized)"""
    
    def __init__(self):
        self.readings_history = []
        self.suspicious_patterns = []
        
    def scan_electromagnetic_spectrum(self) -> List[SignalReading]:
        """Scan for Wi-Fi and Bluetooth signals (the modern equivalent of RF)"""
        signals = []
        
        # Scan Wi-Fi networks
        try:
            # Works on macOS - adapt for other systems
            result = subprocess.run(['airport', '-s'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                signals.extend(self._parse_wifi_scan(result.stdout))
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback for systems without airport command
            print("Wi-Fi scanning unavailable - install wireless tools for full functionality")
        
        # Try to scan Bluetooth devices
        try:
            # This is more complex and system-dependent
            # For now, we'll focus on Wi-Fi which is more universally accessible
            pass
        except Exception:
            pass
            
        return signals
    
    def _parse_wifi_scan(self, scan_output: str) -> List[SignalReading]:
        """Parse airport scan output into SignalReading objects"""
        signals = []
        lines = scan_output.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            # Parse airport output format
            # Network name, MAC, signal strength, encryption, etc.
            parts = line.split()
            if len(parts) >= 6:
                name = parts[0] if parts[0] != '' else "Hidden Network"
                mac = parts[1]
                signal_str = parts[2]
                
                # Extract numeric signal strength
                signal_match = re.search(r'-?\d+', signal_str)
                signal_strength = int(signal_match.group()) if signal_match else -100
                
                # Determine encryption
                encryption = "Unknown"
                if "WPA" in line:
                    encryption = "WPA"
                elif "WEP" in line:
                    encryption = "WEP"
                elif "NONE" in line:
                    encryption = "Open"
                
                signals.append(SignalReading(
                    name=name,
                    frequency="2.4GHz/5GHz",  # Wi-Fi bands
                    signal_strength=signal_strength,
                    mac_address=mac,
                    encryption=encryption,
                    timestamp=datetime.now()
                ))
        
        return signals
    
    def analyze_patterns(self, signals: List[SignalReading]) -> Dict:
        """Look for suspicious patterns in the signals"""
        analysis = {
            "total_signals": len(signals),
            "strongest_signal": None,
            "hidden_networks": 0,
            "open_networks": 0,
            "anomalies": []
        }
        
        if not signals:
            return analysis
        
        # Find strongest signal
        strongest = max(signals, key=lambda s: s.signal_strength)
        analysis["strongest_signal"] = {
            "name": strongest.name,
            "strength": strongest.signal_strength,
            "estimated_distance": f"{strongest.distance_estimate():.1f}m"
        }
        
        # Count network types
        for signal in signals:
            if signal.name == "Hidden Network" or signal.name == "":
                analysis["hidden_networks"] += 1
            if signal.encryption == "Open":
                analysis["open_networks"] += 1
        
        # Look for anomalies
        if analysis["hidden_networks"] > 3:
            analysis["anomalies"].append("Unusually high number of hidden networks detected")
        
        very_strong_signals = [s for s in signals if s.signal_strength > -30]
        if len(very_strong_signals) > 5:
            analysis["anomalies"].append("Multiple very strong signals - possible signal amplification")
        
        return analysis
    
    def triangulate_strongest_sources(self, signals: List[SignalReading], top_n: int = 3) -> List[Dict]:
        """Identify the strongest signal sources for triangulation"""
        if not signals:
            return []
        
        # Sort by signal strength and take top N
        strongest = sorted(signals, key=lambda s: s.signal_strength, reverse=True)[:top_n]
        
        results = []
        for signal in strongest:
            results.append({
                "name": signal.name,
                "mac_address": signal.mac_address,
                "signal_strength": signal.signal_strength,
                "estimated_distance": signal.distance_estimate(),
                "encryption": signal.encryption,
                "frequency": signal.frequency
            })
        
        return results
    
    def continuous_monitoring(self, duration_seconds: int = 30, interval: int = 5):
        """Monitor signals over time to detect changes"""
        print(f"Victoria's detector activated - monitoring for {duration_seconds} seconds...")
        print("Scanning the electromagnetic spectrum of New Cascadia...\n")
        
        end_time = time.time() + duration_seconds
        scan_count = 0
        
        while time.time() < end_time:
            scan_count += 1
            print(f"=== Scan #{scan_count} ===")
            
            signals = self.scan_electromagnetic_spectrum()
            analysis = self.analyze_patterns(signals)
            
            print(f"Signals detected: {analysis['total_signals']}")
            
            if analysis['strongest_signal']:
                print(f"Strongest source: {analysis['strongest_signal']['name']}")
                print(f"Signal strength: {analysis['strongest_signal']['strength']} dBm")
                print(f"Estimated distance: {analysis['strongest_signal']['estimated_distance']}")
            
            if analysis['anomalies']:
                print("🚨 ANOMALIES DETECTED:")
                for anomaly in analysis['anomalies']:
                    print(f"  - {anomaly}")
            
            if analysis['hidden_networks'] > 0:
                print(f"Hidden networks: {analysis['hidden_networks']}")
            
            print("-" * 40)
            
            if time.time() + interval < end_time:
                time.sleep(interval)
        
        print("Monitoring complete. Victoria lowers her detector...")

def main():
    """Run the Meridian Triangulation Engine"""
    detector = MeridianTriangulator()
    
    print("=== THE MERIDIAN TRIANGULATION ENGINE ===")
    print("Victoria Brassheart's Portable Signal Detector")
    print("Analyzing electromagnetic signatures...\n")
    
    # Single scan
    signals = detector.scan_electromagnetic_spectrum()
    analysis = detector.analyze_patterns(signals)
    
    print(f"Total signals detected: {analysis['total_signals']}")
    
    if analysis['strongest_signal']:
        print(f"\nStrongest signal source:")
        print(f"Name: {analysis['strongest_signal']['name']}")
        print(f"Strength: {analysis['strongest_signal']['strength']} dBm")
        print(f"Distance estimate: {analysis['strongest_signal']['estimated_distance']}")
    
    if analysis['anomalies']:
        print(f"\n🚨 Suspicious patterns detected:")
        for anomaly in analysis['anomalies']:
            print(f"  - {anomaly}")
    
    # Show top signal sources for triangulation
    top_sources = detector.triangulate_strongest_sources(signals)
    if top_sources:
        print(f"\nTop signal sources for triangulation:")
        for i, source in enumerate(top_sources, 1):
            print(f"{i}. {source['name']} ({source['signal_strength']} dBm, ~{source['estimated_distance']:.1f}m)")
    
    print(f"\nHidden networks: {analysis['hidden_networks']}")
    print(f"Open networks: {analysis['open_networks']}")

if __name__ == "__main__":
    main()