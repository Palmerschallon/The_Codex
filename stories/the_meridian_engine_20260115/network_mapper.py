#!/usr/bin/env python3
"""
The Meridian Network Mapper - Victoria's field modification to track signal networks

A real network analysis tool for mapping communication patterns and predicting
transmission sources based on signal timing and frequency analysis.
"""

import time
import json
import math
import threading
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

@dataclass
class SignalReading:
    timestamp: float
    frequency: float
    strength: float
    direction: float  # degrees from north
    location: Tuple[float, float]  # lat, lon of receiver

class NetworkMapper:
    """Maps communication networks by analyzing signal patterns and timing"""
    
    def __init__(self):
        self.signal_history = deque(maxlen=1000)
        self.transmission_patterns = defaultdict(list)
        self.network_nodes = {}
        self.prediction_window = 300  # 5 minutes
        
    def add_signal(self, reading: SignalReading):
        """Process a new signal reading and update network map"""
        self.signal_history.append(reading)
        
        # Group signals by frequency for pattern analysis
        freq_key = round(reading.frequency, 1)
        self.transmission_patterns[freq_key].append(reading)
        
        # Triangulate if we have multiple readings
        self._attempt_triangulation(reading)
        
    def _attempt_triangulation(self, new_reading: SignalReading):
        """Try to locate transmission source using multiple readings"""
        recent_readings = [r for r in self.signal_history 
                          if abs(r.frequency - new_reading.frequency) < 0.1
                          and r.timestamp > new_reading.timestamp - 30]
        
        if len(recent_readings) >= 2:
            location = self._triangulate_source(recent_readings)
            if location:
                self.network_nodes[new_reading.frequency] = {
                    'location': location,
                    'last_seen': new_reading.timestamp,
                    'strength': new_reading.strength
                }
    
    def _triangulate_source(self, readings: List[SignalReading]) -> Optional[Tuple[float, float]]:
        """Triangulate transmission source from multiple directional readings"""
        if len(readings) < 2:
            return None
            
        # Simple triangulation using intersection of bearing lines
        # In a real implementation, this would be more sophisticated
        lines = []
        for reading in readings[:3]:  # Use up to 3 readings for accuracy
            # Convert bearing to line equation
            bearing_rad = math.radians(reading.direction)
            x1, y1 = reading.location
            
            # Point along bearing line
            x2 = x1 + math.sin(bearing_rad)
            y2 = y1 + math.cos(bearing_rad)
            
            lines.append(((x1, y1), (x2, y2)))
        
        if len(lines) >= 2:
            intersection = self._line_intersection(lines[0], lines[1])
            return intersection
            
        return None
    
    def _line_intersection(self, line1, line2):
        """Find intersection of two lines"""
        (x1, y1), (x2, y2) = line1
        (x3, y3), (x4, y4) = line2
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None  # Lines are parallel
            
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        
        intersection_x = x1 + t * (x2 - x1)
        intersection_y = y1 + t * (y2 - y1)
        
        return (intersection_x, intersection_y)
    
    def predict_next_transmission(self, frequency: float) -> Optional[datetime]:
        """Predict when the next transmission might occur on this frequency"""
        if frequency not in self.transmission_patterns:
            return None
            
        readings = self.transmission_patterns[frequency]
        if len(readings) < 3:
            return None
            
        # Analyze timing patterns
        recent_readings = [r for r in readings if r.timestamp > time.time() - 3600]
        if len(recent_readings) < 2:
            return None
            
        # Look for periodic patterns in transmission times
        intervals = []
        for i in range(1, len(recent_readings)):
            interval = recent_readings[i].timestamp - recent_readings[i-1].timestamp
            intervals.append(interval)
        
        if intervals:
            # Use median interval as prediction basis
            intervals.sort()
            median_interval = intervals[len(intervals) // 2]
            
            last_transmission = recent_readings[-1].timestamp
            next_transmission = last_transmission + median_interval
            
            return datetime.fromtimestamp(next_transmission)
            
        return None
    
    def get_network_summary(self) -> Dict:
        """Get a summary of the detected network"""
        active_frequencies = []
        
        current_time = time.time()
        for freq, readings in self.transmission_patterns.items():
            recent_activity = [r for r in readings 
                             if current_time - r.timestamp < 1800]  # 30 minutes
            
            if recent_activity:
                next_predicted = self.predict_next_transmission(freq)
                
                active_frequencies.append({
                    'frequency': freq,
                    'last_activity': max(r.timestamp for r in recent_activity),
                    'transmission_count': len(recent_activity),
                    'predicted_next': next_predicted.isoformat() if next_predicted else None,
                    'estimated_location': self.network_nodes.get(freq, {}).get('location')
                })
        
        return {
            'active_frequencies': active_frequencies,
            'total_nodes': len(self.network_nodes),
            'analysis_time': datetime.now().isoformat()
        }
    
    def export_network_data(self, filename: str):
        """Export network analysis for further investigation"""
        data = {
            'network_summary': self.get_network_summary(),
            'signal_history': [
                {
                    'timestamp': r.timestamp,
                    'frequency': r.frequency,
                    'strength': r.strength,
                    'direction': r.direction,
                    'location': r.location
                }
                for r in list(self.signal_history)[-100:]  # Last 100 readings
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

def main():
    """Demonstration of network mapping capabilities"""
    mapper = NetworkMapper()
    
    print("Meridian Network Mapper - Signal Analysis Tool")
    print("=" * 50)
    
    # In a real scenario, this would receive live signal data
    # For demo, we'll show the analysis capabilities
    
    print("\nFeatures:")
    print("- Real-time signal triangulation")
    print("- Pattern analysis and prediction")
    print("- Network topology mapping")
    print("- Export capabilities for investigation")
    
    print(f"\nReady to analyze transmission networks...")
    print("(Use add_signal() method with SignalReading objects)")

if __name__ == "__main__":
    main()