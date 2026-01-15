#!/usr/bin/env python3
"""
Victoria's Portable Signal Tracker - Real-time frequency analysis and direction finding
A sophisticated signal analysis tool disguised as dieselpunk tech
"""

import numpy as np
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import threading
import queue

class FrequencyTracker:
    """
    Analyzes radio frequencies and tracks signal sources
    Based on Victorian-era direction-finding techniques adapted for modern use
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.signals = {}
        self.tracking_data = []
        self.is_tracking = False
        self.data_queue = queue.Queue()
        
    def analyze_frequency_spectrum(self, signal_data: np.ndarray) -> Dict:
        """
        Perform FFT analysis to identify frequency components
        Returns dominant frequencies and their characteristics
        """
        # Apply window function to reduce spectral leakage
        windowed = signal_data * np.hanning(len(signal_data))
        
        # Perform FFT
        fft_data = np.fft.fft(windowed)
        frequencies = np.fft.fftfreq(len(signal_data), 1/self.sample_rate)
        
        # Calculate power spectrum
        power_spectrum = np.abs(fft_data) ** 2
        
        # Find dominant frequencies
        dominant_indices = np.argsort(power_spectrum)[-10:]  # Top 10 frequencies
        dominant_freqs = frequencies[dominant_indices]
        dominant_powers = power_spectrum[dominant_indices]
        
        return {
            'timestamp': datetime.now().isoformat(),
            'dominant_frequencies': dominant_freqs.tolist(),
            'power_levels': dominant_powers.tolist(),
            'total_energy': np.sum(power_spectrum),
            'frequency_range': [float(np.min(frequencies)), float(np.max(frequencies))]
        }
    
    def triangulate_source(self, readings: List[Dict]) -> Optional[Dict]:
        """
        Use multiple signal strength readings to estimate source location
        Implements basic triangulation based on signal strength
        """
        if len(readings) < 3:
            return None
            
        # Simple triangulation based on signal strength differences
        positions = []
        strengths = []
        
        for reading in readings:
            if 'position' in reading and 'strength' in reading:
                positions.append(reading['position'])
                strengths.append(reading['strength'])
        
        if len(positions) >= 3:
            # Weighted centroid calculation
            total_weight = sum(strengths)
            if total_weight > 0:
                weighted_x = sum(pos[0] * strength for pos, strength in zip(positions, strengths)) / total_weight
                weighted_y = sum(pos[1] * strength for pos, strength in zip(positions, strengths)) / total_weight
                
                return {
                    'estimated_location': [weighted_x, weighted_y],
                    'confidence': min(strengths) / max(strengths) if max(strengths) > 0 else 0,
                    'readings_used': len(readings)
                }
        
        return None
    
    def detect_patterns(self, signal_history: List[Dict]) -> Dict:
        """
        Analyze signal history for patterns - periodic transmissions, encoding schemes
        """
        if len(signal_history) < 2:
            return {'patterns': [], 'confidence': 0}
        
        patterns = []
        timestamps = [datetime.fromisoformat(s['timestamp']) for s in signal_history]
        
        # Check for periodic transmissions
        if len(timestamps) >= 3:
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                        for i in range(len(timestamps)-1)]
            
            # Look for consistent intervals
            avg_interval = np.mean(intervals)
            interval_std = np.std(intervals)
            
            if interval_std < avg_interval * 0.1:  # Low variance indicates periodicity
                patterns.append({
                    'type': 'periodic_transmission',
                    'interval_seconds': avg_interval,
                    'variance': interval_std,
                    'confidence': max(0, 1 - (interval_std / avg_interval))
                })
        
        # Check for frequency hopping
        freq_changes = []
        for i in range(len(signal_history)-1):
            curr_freqs = set(signal_history[i].get('dominant_frequencies', []))
            next_freqs = set(signal_history[i+1].get('dominant_frequencies', []))
            
            if len(curr_freqs & next_freqs) / max(len(curr_freqs | next_freqs), 1) < 0.5:
                freq_changes.append(i)
        
        if len(freq_changes) > len(signal_history) * 0.3:
            patterns.append({
                'type': 'frequency_hopping',
                'hop_rate': len(freq_changes) / len(signal_history),
                'confidence': min(len(freq_changes) / 5, 1.0)
            })
        
        return {
            'patterns': patterns,
            'analysis_timestamp': datetime.now().isoformat(),
            'signals_analyzed': len(signal_history)
        }
    
    def generate_mock_reading(self, base_freq: float = 2400, noise_level: float = 0.1) -> np.ndarray:
        """
        Generate synthetic signal data for testing (simulates radio receiver input)
        """
        duration = 1.0  # 1 second of data
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Create a complex signal with multiple components
        signal = (np.sin(2 * np.pi * base_freq * t) + 
                 0.5 * np.sin(2 * np.pi * (base_freq * 1.5) * t) +
                 0.3 * np.sin(2 * np.pi * (base_freq * 0.8) * t))
        
        # Add noise
        noise = np.random.normal(0, noise_level, len(signal))
        return signal + noise
    
    def start_continuous_monitoring(self, callback=None):
        """
        Start continuous signal monitoring (would interface with actual radio hardware)
        """
        self.is_tracking = True
        
        def monitoring_loop():
            while self.is_tracking:
                # In real implementation, this would read from radio hardware
                mock_signal = self.generate_mock_reading()
                analysis = self.analyze_frequency_spectrum(mock_signal)
                
                self.tracking_data.append(analysis)
                
                if callback:
                    callback(analysis)
                
                time.sleep(1)  # 1-second intervals
        
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.is_tracking = False
    
    def export_tracking_data(self, filename: str = None) -> str:
        """Export all tracking data to JSON file"""
        if filename is None:
            filename = f"signal_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'session_info': {
                'start_time': self.tracking_data[0]['timestamp'] if self.tracking_data else None,
                'end_time': self.tracking_data[-1]['timestamp'] if self.tracking_data else None,
                'total_readings': len(self.tracking_data),
                'sample_rate': self.sample_rate
            },
            'tracking_data': self.tracking_data,
            'patterns': self.detect_patterns(self.tracking_data) if self.tracking_data else {}
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename

# Example usage functions
def demo_tracking_session():
    """Run a demonstration of the tracking system"""
    print("=== Victoria's Signal Tracker - Demo Session ===")
    tracker = FrequencyTracker()
    
    # Simulate multiple readings
    print("Collecting signal samples...")
    for i in range(5):
        mock_data = tracker.generate_mock_reading(base_freq=2400 + i*100)
        analysis = tracker.analyze_frequency_spectrum(mock_data)
        tracker.tracking_data.append(analysis)
        print(f"Reading {i+1}: {len(analysis['dominant_frequencies'])} frequencies detected")
        time.sleep(0.5)
    
    # Analyze patterns
    patterns = tracker.detect_patterns(tracker.tracking_data)
    print(f"\nPattern Analysis: {len(patterns['patterns'])} patterns detected")
    
    # Export results
    filename = tracker.export_tracking_data()
    print(f"Data exported to: {filename}")
    
    return tracker

if __name__ == "__main__":
    demo_tracking_session()