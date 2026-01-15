#!/usr/bin/env python3
"""
Victoria's Portable Signal Tracker - Enhanced directional analysis
A real-time signal strength and direction finder for radio frequencies
"""

import numpy as np
import threading
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class SignalReading:
    frequency: float
    strength: float
    direction: float  # degrees from north
    timestamp: float
    confidence: float

class PortableSignalTracker:
    """
    Victoria's brass-and-copper signal tracking device
    Provides real-time directional analysis of radio signals
    """
    
    def __init__(self, antenna_separation: float = 0.5):
        self.antenna_separation = antenna_separation  # meters
        self.is_tracking = False
        self.current_readings: List[SignalReading] = []
        self.target_frequency = None
        self._lock = threading.Lock()
        
    def start_tracking(self, frequency: float = None):
        """Begin tracking signals on specified frequency"""
        self.target_frequency = frequency
        self.is_tracking = True
        self.tracking_thread = threading.Thread(target=self._tracking_loop)
        self.tracking_thread.daemon = True
        self.tracking_thread.start()
        
    def stop_tracking(self):
        """Stop signal tracking"""
        self.is_tracking = False
        if hasattr(self, 'tracking_thread'):
            self.tracking_thread.join()
            
    def _tracking_loop(self):
        """Main tracking loop - simulates antenna array processing"""
        while self.is_tracking:
            # Simulate multiple antenna readings
            readings = self._sample_antennas()
            
            if readings:
                # Calculate direction using phase difference
                direction = self._calculate_direction(readings)
                strength = max(r[1] for r in readings)
                confidence = self._calculate_confidence(readings)
                
                reading = SignalReading(
                    frequency=self.target_frequency or 0.0,
                    strength=strength,
                    direction=direction,
                    timestamp=time.time(),
                    confidence=confidence
                )
                
                with self._lock:
                    self.current_readings.append(reading)
                    # Keep only recent readings
                    cutoff = time.time() - 10.0
                    self.current_readings = [
                        r for r in self.current_readings 
                        if r.timestamp > cutoff
                    ]
            
            time.sleep(0.1)  # 10 readings per second
            
    def _sample_antennas(self) -> List[Tuple[int, float, float]]:
        """Simulate readings from antenna array"""
        # In real implementation, this would interface with radio hardware
        # For simulation, we'll generate realistic signal patterns
        
        if not self.target_frequency:
            return []
            
        readings = []
        num_antennas = 4  # Circular array
        
        for i in range(num_antennas):
            # Simulate signal strength with some noise
            base_strength = 50 + 30 * math.sin(time.time() * 0.5)
            noise = np.random.normal(0, 5)
            strength = max(0, base_strength + noise)
            
            # Simulate phase (for direction finding)
            phase = np.random.uniform(0, 2 * math.pi)
            
            readings.append((i, strength, phase))
            
        return readings
        
    def _calculate_direction(self, readings: List[Tuple[int, float, float]]) -> float:
        """Calculate signal direction from antenna phase differences"""
        if len(readings) < 2:
            return 0.0
            
        # Simple direction finding using strongest signal
        strongest_antenna = max(readings, key=lambda x: x[1])[0]
        
        # Convert antenna position to compass bearing
        # Antenna 0 = North, 1 = East, 2 = South, 3 = West
        direction_map = {0: 0, 1: 90, 2: 180, 3: 270}
        
        return direction_map.get(strongest_antenna, 0)
        
    def _calculate_confidence(self, readings: List[Tuple[int, float, float]]) -> float:
        """Calculate confidence in direction reading"""
        if not readings:
            return 0.0
            
        strengths = [r[1] for r in readings]
        max_strength = max(strengths)
        avg_strength = sum(strengths) / len(strengths)
        
        # Higher confidence when one antenna is clearly strongest
        if avg_strength > 0:
            confidence = (max_strength - avg_strength) / max_strength
            return min(1.0, max(0.0, confidence))
        
        return 0.0
        
    def get_current_reading(self) -> Optional[SignalReading]:
        """Get the most recent signal reading"""
        with self._lock:
            if self.current_readings:
                return self.current_readings[-1]
        return None
        
    def get_average_direction(self, seconds: float = 5.0) -> Tuple[float, float]:
        """Get average direction over specified time period"""
        cutoff = time.time() - seconds
        
        with self._lock:
            recent_readings = [
                r for r in self.current_readings 
                if r.timestamp > cutoff and r.confidence > 0.3
            ]
            
        if not recent_readings:
            return 0.0, 0.0
            
        # Calculate circular mean for directions
        directions_rad = [math.radians(r.direction) for r in recent_readings]
        weights = [r.confidence * r.strength for r in recent_readings]
        
        x_sum = sum(w * math.cos(d) for d, w in zip(directions_rad, weights))
        y_sum = sum(w * math.sin(d) for d, w in zip(directions_rad, weights))
        weight_sum = sum(weights)
        
        if weight_sum > 0:
            avg_direction = math.degrees(math.atan2(y_sum, x_sum))
            if avg_direction < 0:
                avg_direction += 360
                
            confidence = min(1.0, weight_sum / len(recent_readings) / 100)
            return avg_direction, confidence
            
        return 0.0, 0.0
        
    def scan_frequencies(self, freq_range: Tuple[float, float], 
                        step: float = 0.1) -> List[Tuple[float, float]]:
        """Scan across frequency range for strong signals"""
        start_freq, end_freq = freq_range
        strong_signals = []
        
        current_freq = start_freq
        while current_freq <= end_freq:
            # Simulate frequency scanning
            # In real hardware, this would tune the receiver
            
            # Generate realistic frequency response
            strength = self._simulate_frequency_response(current_freq)
            
            if strength > 70:  # Threshold for "strong" signals
                strong_signals.append((current_freq, strength))
                
            current_freq += step
            time.sleep(0.01)  # Brief pause between frequencies
            
        return strong_signals
        
    def _simulate_frequency_response(self, frequency: float) -> float:
        """Simulate signal strength at different frequencies"""
        # Create some interesting frequencies with strong signals
        interesting_freqs = [145.5, 162.3, 173.8, 201.7, 445.2]
        
        max_strength = 0
        for target_freq in interesting_freqs:
            # Gaussian response around interesting frequencies
            diff = abs(frequency - target_freq)
            if diff < 2.0:  # Within 2 MHz
                strength = 100 * math.exp(-0.5 * (diff / 0.5) ** 2)
                max_strength = max(max_strength, strength)
                
        # Add some background noise
        noise = np.random.normal(20, 5)
        return max(0, max_strength + noise)

def main():
    """Command-line interface for the signal tracker"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Victoria's Signal Tracker")
    parser.add_argument("--frequency", type=float, help="Target frequency to track")
    parser.add_argument("--scan", nargs=2, type=float, metavar=('START', 'END'),
                       help="Scan frequency range")
    parser.add_argument("--duration", type=int, default=30, 
                       help="Tracking duration in seconds")
    
    args = parser.parse_args()
    
    tracker = PortableSignalTracker()
    
    try:
        if args.scan:
            print(f"Scanning frequencies {args.scan[0]} - {args.scan[1]} MHz...")
            signals = tracker.scan_frequencies(tuple(args.scan))
            
            print("\nStrong signals detected:")
            for freq, strength in signals:
                print(f"  {freq:6.1f} MHz: {strength:5.1f} dBm")
                
        elif args.frequency:
            print(f"Tracking frequency {args.frequency} MHz...")
            tracker.start_tracking(args.frequency)
            
            start_time = time.time()
            while time.time() - start_time < args.duration:
                reading = tracker.get_current_reading()
                if reading:
                    direction, confidence = tracker.get_average_direction()
                    print(f"Direction: {direction:6.1f}° "
                          f"Strength: {reading.strength:5.1f} "
                          f"Confidence: {confidence:4.2f}")
                
                time.sleep(1)
                
        else:
            print("Please specify --frequency to track or --scan range")
            
    except KeyboardInterrupt:
        print("\nTracking stopped")
    finally:
        tracker.stop_tracking()

if __name__ == "__main__":
    main()