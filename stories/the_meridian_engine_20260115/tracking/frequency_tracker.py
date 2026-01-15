#!/usr/bin/env python3
"""
Victoria's Enhanced Frequency Tracker - Real-time signal analysis and prediction
Tracks wireless signals across multiple frequency bands and predicts transmission patterns
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional
import json
from datetime import datetime, timedelta

@dataclass
class SignalReading:
    """Represents a signal detection event"""
    timestamp: float
    frequency: float
    strength: float
    location: Tuple[float, float]  # x, y coordinates
    phase_shift: float

class FrequencyTracker:
    """Victoria's brass-and-copper frequency tracking engine"""
    
    def __init__(self, max_history: int = 1000):
        self.signal_history = deque(maxlen=max_history)
        self.active_frequencies = {}
        self.prediction_model = None
        self.tracking_active = False
        self.location = [0.0, 0.0]  # Current tracker location
        
    def add_signal_reading(self, frequency: float, strength: float, 
                          location: Tuple[float, float] = None) -> SignalReading:
        """Record a new signal detection"""
        if location is None:
            location = tuple(self.location)
            
        reading = SignalReading(
            timestamp=time.time(),
            frequency=frequency,
            strength=strength,
            location=location,
            phase_shift=self._calculate_phase_shift(frequency)
        )
        
        self.signal_history.append(reading)
        self._update_frequency_tracking(reading)
        return reading
    
    def _calculate_phase_shift(self, frequency: float) -> float:
        """Calculate phase shift based on frequency and recent history"""
        if len(self.signal_history) < 2:
            return 0.0
        
        recent_signals = [s for s in self.signal_history 
                         if abs(s.frequency - frequency) < 0.1]
        
        if len(recent_signals) < 2:
            return 0.0
            
        # Simple phase calculation based on time differences
        time_diff = recent_signals[-1].timestamp - recent_signals[-2].timestamp
        return (frequency * time_diff) % (2 * np.pi)
    
    def _update_frequency_tracking(self, reading: SignalReading):
        """Update internal tracking for a specific frequency"""
        freq_key = round(reading.frequency, 1)
        
        if freq_key not in self.active_frequencies:
            self.active_frequencies[freq_key] = {
                'readings': deque(maxlen=100),
                'last_seen': reading.timestamp,
                'strength_trend': deque(maxlen=50),
                'location_history': deque(maxlen=50)
            }
        
        freq_data = self.active_frequencies[freq_key]
        freq_data['readings'].append(reading)
        freq_data['last_seen'] = reading.timestamp
        freq_data['strength_trend'].append(reading.strength)
        freq_data['location_history'].append(reading.location)
    
    def predict_next_transmission(self, frequency: float) -> Optional[dict]:
        """Predict when and where the next transmission might occur"""
        freq_key = round(frequency, 1)
        
        if freq_key not in self.active_frequencies:
            return None
            
        freq_data = self.active_frequencies[freq_key]
        readings = list(freq_data['readings'])
        
        if len(readings) < 3:
            return None
        
        # Analyze timing patterns
        time_intervals = []
        for i in range(1, len(readings)):
            interval = readings[i].timestamp - readings[i-1].timestamp
            time_intervals.append(interval)
        
        if not time_intervals:
            return None
        
        # Simple prediction based on average interval
        avg_interval = np.mean(time_intervals)
        std_interval = np.std(time_intervals)
        
        next_time = freq_data['last_seen'] + avg_interval
        uncertainty = std_interval
        
        # Location prediction (simple extrapolation)
        locations = list(freq_data['location_history'])
        if len(locations) >= 2:
            dx = locations[-1][0] - locations[-2][0]
            dy = locations[-1][1] - locations[-2][1]
            predicted_location = (
                locations[-1][0] + dx,
                locations[-1][1] + dy
            )
        else:
            predicted_location = locations[-1] if locations else (0, 0)
        
        return {
            'predicted_time': next_time,
            'uncertainty_seconds': uncertainty,
            'predicted_location': predicted_location,
            'confidence': min(len(readings) / 10.0, 1.0)  # 0-1 scale
        }
    
    def get_signal_strength_map(self, grid_size: int = 50) -> np.ndarray:
        """Generate a 2D map of signal strengths across the tracking area"""
        # Create coordinate grids
        if not self.signal_history:
            return np.zeros((grid_size, grid_size))
        
        # Get bounds from signal history
        x_coords = [s.location[0] for s in self.signal_history]
        y_coords = [s.location[1] for s in self.signal_history]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        # Ensure non-zero range
        if x_max == x_min:
            x_max += 1
        if y_max == y_min:
            y_max += 1
        
        x_grid = np.linspace(x_min, x_max, grid_size)
        y_grid = np.linspace(y_min, y_max, grid_size)
        
        signal_map = np.zeros((grid_size, grid_size))
        
        # Populate grid with signal strengths
        for reading in self.signal_history:
            # Find closest grid point
            x_idx = np.argmin(np.abs(x_grid - reading.location[0]))
            y_idx = np.argmin(np.abs(y_grid - reading.location[1]))
            
            # Add signal strength (with decay for older signals)
            age_factor = max(0.1, 1.0 - (time.time() - reading.timestamp) / 3600)
            signal_map[y_idx, x_idx] += reading.strength * age_factor
        
        return signal_map
    
    def find_anomalous_patterns(self, threshold: float = 2.0) -> List[dict]:
        """Detect unusual signal patterns that might indicate coordinated activity"""
        anomalies = []
        
        for freq_key, freq_data in self.active_frequencies.items():
            readings = list(freq_data['readings'])
            
            if len(readings) < 5:
                continue
            
            # Check for unusual timing patterns
            time_intervals = []
            for i in range(1, len(readings)):
                interval = readings[i].timestamp - readings[i-1].timestamp
                time_intervals.append(interval)
            
            if time_intervals:
                mean_interval = np.mean(time_intervals)
                std_interval = np.std(time_intervals)
                
                # Look for suspiciously regular intervals
                if std_interval < mean_interval * 0.1 and len(time_intervals) > 3:
                    anomalies.append({
                        'type': 'regular_timing',
                        'frequency': freq_key,
                        'interval': mean_interval,
                        'regularity': 1.0 - (std_interval / mean_interval),
                        'description': f'Highly regular transmissions every {mean_interval:.1f}s'
                    })
            
            # Check for strength anomalies
            strengths = [r.strength for r in readings]
            if len(strengths) > 3:
                mean_strength = np.mean(strengths)
                std_strength = np.std(strengths)
                
                recent_strength = np.mean(strengths[-3:])
                if recent_strength > mean_strength + threshold * std_strength:
                    anomalies.append({
                        'type': 'strength_spike',
                        'frequency': freq_key,
                        'normal_strength': mean_strength,
                        'current_strength': recent_strength,
                        'severity': (recent_strength - mean_strength) / std_strength,
                        'description': f'Signal strength spike on {freq_key} MHz'
                    })
        
        return anomalies
    
    def export_tracking_data(self, filename: str = None):
        """Export tracking data for analysis"""
        if filename is None:
            filename = f"signal_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'export_time': datetime.now().isoformat(),
            'total_readings': len(self.signal_history),
            'active_frequencies': len(self.active_frequencies),
            'readings': [
                {
                    'timestamp': r.timestamp,
                    'frequency': r.frequency,
                    'strength': r.strength,
                    'location': r.location,
                    'phase_shift': r.phase_shift
                }
                for r in self.signal_history
            ],
            'frequency_summary': {
                freq: {
                    'total_readings': len(data['readings']),
                    'last_seen': data['last_seen'],
                    'avg_strength': np.mean(data['strength_trend']) if data['strength_trend'] else 0
                }
                for freq, data in self.active_frequencies.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename

def create_tracker_display(tracker: FrequencyTracker):
    """Create a real-time visualization of the frequency tracker"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    def update_display():
        ax1.clear()
        ax2.clear()
        
        # Plot frequency vs time
        if tracker.signal_history:
            times = [r.timestamp for r in tracker.signal_history]
            frequencies = [r.frequency for r in tracker.signal_history]
            strengths = [r.strength for r in tracker.signal_history]
            
            scatter = ax1.scatter(times, frequencies, c=strengths, 
                                cmap='plasma', alpha=0.7)
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Frequency (MHz)')
            ax1.set_title('Signal Frequency Timeline')
            plt.colorbar(scatter, ax=ax1, label='Signal Strength')
            
            # Plot signal strength map
            signal_map = tracker.get_signal_strength_map()
            im = ax2.imshow(signal_map, cmap='hot', interpolation='bilinear')
            ax2.set_title('Signal Strength Heatmap')
            ax2.set_xlabel('X Coordinate')
            ax2.set_ylabel('Y Coordinate')
            plt.colorbar(im, ax=ax2, label='Signal Strength')
        
        plt.tight_layout()
        plt.pause(0.1)
    
    return update_display

if __name__ == "__main__":
    # Example usage - Victoria's field test
    tracker = FrequencyTracker()
    
    print("Victoria's Enhanced Frequency Tracker - Field Test")
    print("=" * 50)
    
    # Simulate some signal readings
    import random
    
    for i in range(20):
        freq = 145.5 + random.uniform(-0.5, 0.5)
        strength = 50 + random.uniform(-20, 30)
        location = (random.uniform(0, 100), random.uniform(0, 100))
        
        reading = tracker.add_signal_reading(freq, strength, location)
        
        if i % 5 == 0:
            prediction = tracker.predict_next_transmission(freq)
            if prediction:
                print(f"Prediction for {freq:.1f} MHz:")
                print(f"  Next transmission: {prediction['predicted_time']:.1f}")
                print(f"  Confidence: {prediction['confidence']:.2f}")
        
        time.sleep(0.1)
    
    # Check for anomalies
    anomalies = tracker.find_anomalous_patterns()
    if anomalies:
        print("\nAnomalous Patterns Detected:")
        for anomaly in anomalies:
            print(f"  {anomaly['description']}")
    
    # Export data
    export_file = tracker.export_tracking_data()
    print(f"\nTracking data exported to: {export_file}")