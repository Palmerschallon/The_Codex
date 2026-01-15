#!/usr/bin/env python3
"""
Victoria's Enhanced Location Tracker - Real-time position triangulation system
A practical tool for tracking signal sources using multiple reference points
"""

import math
import time
import json
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SignalReading:
    """A signal strength reading from a specific location"""
    timestamp: float
    location: Tuple[float, float]  # (latitude, longitude)
    signal_strength: float  # in dBm
    frequency: float  # in Hz
    bearing: Optional[float] = None  # in degrees from north

@dataclass
class TrackedTarget:
    """A target being tracked with signal triangulation"""
    target_id: str
    estimated_position: Tuple[float, float]
    confidence: float  # 0.0 to 1.0
    last_updated: float
    signal_readings: List[SignalReading]

class LocationTracker:
    """Real-time location tracking using signal triangulation"""
    
    def __init__(self):
        self.readings: List[SignalReading] = []
        self.targets: Dict[str, TrackedTarget] = {}
        self.reference_points: List[Tuple[float, float]] = []
        
    def add_reference_point(self, lat: float, lon: float):
        """Add a known reference point for triangulation"""
        self.reference_points.append((lat, lon))
        
    def add_signal_reading(self, reading: SignalReading) -> None:
        """Add a new signal strength reading"""
        self.readings.append(reading)
        
        # Keep only recent readings (last 5 minutes)
        cutoff_time = time.time() - 300
        self.readings = [r for r in self.readings if r.timestamp > cutoff_time]
        
    def calculate_distance_from_signal(self, signal_strength: float, 
                                     reference_strength: float = -30.0) -> float:
        """
        Estimate distance based on signal strength using path loss formula
        Returns distance in meters
        """
        if signal_strength >= reference_strength:
            return 1.0  # Very close
            
        # Free space path loss approximation
        path_loss = reference_strength - signal_strength
        # Simplified: every 6dB doubles the distance
        distance = 10 ** (path_loss / 20)
        
        return max(1.0, min(distance, 10000.0))  # Cap between 1m and 10km
    
    def triangulate_position(self, readings: List[SignalReading]) -> Optional[Tuple[float, float]]:
        """
        Triangulate position using multiple signal readings
        Returns (latitude, longitude) or None if insufficient data
        """
        if len(readings) < 3:
            return None
            
        # Use trilateration with least squares approximation
        positions = []
        distances = []
        
        for reading in readings[-3:]:  # Use 3 most recent readings
            distance = self.calculate_distance_from_signal(reading.signal_strength)
            positions.append(reading.location)
            distances.append(distance)
            
        return self._trilaterate(positions, distances)
    
    def _trilaterate(self, positions: List[Tuple[float, float]], 
                    distances: List[float]) -> Optional[Tuple[float, float]]:
        """
        Perform trilateration calculation
        Uses geometric intersection of circles
        """
        if len(positions) < 3 or len(distances) < 3:
            return None
            
        # Convert to Cartesian coordinates for calculation
        x1, y1 = self._lat_lon_to_meters(positions[0])
        x2, y2 = self._lat_lon_to_meters(positions[1])
        x3, y3 = self._lat_lon_to_meters(positions[2])
        
        r1, r2, r3 = distances[0], distances[1], distances[2]
        
        # Trilateration math
        A = 2 * (x2 - x1)
        B = 2 * (y2 - y1)
        C = r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
        D = 2 * (x3 - x2)
        E = 2 * (y3 - y2)
        F = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2
        
        denominator = A * E - B * D
        if abs(denominator) < 1e-6:  # Points are collinear
            return None
            
        x = (C * E - F * B) / denominator
        y = (A * F - D * C) / denominator
        
        return self._meters_to_lat_lon((x, y))
    
    def _lat_lon_to_meters(self, lat_lon: Tuple[float, float]) -> Tuple[float, float]:
        """Convert lat/lon to approximate meter coordinates"""
        lat, lon = lat_lon
        # Rough approximation for local coordinates
        x = lon * 111320 * math.cos(math.radians(lat))
        y = lat * 110540
        return (x, y)
    
    def _meters_to_lat_lon(self, xy: Tuple[float, float]) -> Tuple[float, float]:
        """Convert meter coordinates back to lat/lon"""
        x, y = xy
        lat = y / 110540
        lon = x / (111320 * math.cos(math.radians(lat)))
        return (lat, lon)
    
    def track_target(self, target_id: str, frequency: float, 
                    min_readings: int = 3) -> Optional[TrackedTarget]:
        """
        Track a specific target by frequency
        Returns updated target information
        """
        # Filter readings for this frequency (±100Hz tolerance)
        target_readings = [
            r for r in self.readings 
            if abs(r.frequency - frequency) < 100
        ]
        
        if len(target_readings) < min_readings:
            return None
            
        # Estimate position
        position = self.triangulate_position(target_readings)
        if not position:
            return None
            
        # Calculate confidence based on reading consistency
        confidence = self._calculate_confidence(target_readings)
        
        target = TrackedTarget(
            target_id=target_id,
            estimated_position=position,
            confidence=confidence,
            last_updated=time.time(),
            signal_readings=target_readings
        )
        
        self.targets[target_id] = target
        return target
    
    def _calculate_confidence(self, readings: List[SignalReading]) -> float:
        """Calculate tracking confidence based on reading quality"""
        if len(readings) < 3:
            return 0.0
            
        # Factor in: number of readings, time spread, signal strength consistency
        reading_count_score = min(len(readings) / 10, 1.0)
        
        # Time spread score (better if readings span more time)
        if len(readings) > 1:
            time_span = max(r.timestamp for r in readings) - min(r.timestamp for r in readings)
            time_score = min(time_span / 60, 1.0)  # Max score at 1 minute span
        else:
            time_score = 0.0
            
        # Signal consistency score
        strengths = [r.signal_strength for r in readings]
        if len(strengths) > 1:
            avg_strength = sum(strengths) / len(strengths)
            variance = sum((s - avg_strength) ** 2 for s in strengths) / len(strengths)
            consistency_score = max(0.0, 1.0 - variance / 100)  # Lower variance = higher score
        else:
            consistency_score = 0.5
            
        return (reading_count_score + time_score + consistency_score) / 3
    
    def get_tracking_report(self) -> Dict:
        """Generate a comprehensive tracking report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_readings': len(self.readings),
            'active_targets': len(self.targets),
            'targets': {}
        }
        
        for target_id, target in self.targets.items():
            report['targets'][target_id] = {
                'position': target.estimated_position,
                'confidence': target.confidence,
                'last_updated': datetime.fromtimestamp(target.last_updated).isoformat(),
                'reading_count': len(target.signal_readings)
            }
            
        return report
    
    def export_data(self, filename: str) -> None:
        """Export tracking data to JSON file"""
        data = {
            'readings': [
                {
                    'timestamp': r.timestamp,
                    'location': r.location,
                    'signal_strength': r.signal_strength,
                    'frequency': r.frequency,
                    'bearing': r.bearing
                }
                for r in self.readings
            ],
            'targets': {
                tid: {
                    'position': t.estimated_position,
                    'confidence': t.confidence,
                    'last_updated': t.last_updated
                }
                for tid, t in self.targets.items()
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

# Example usage for signal tracking in urban environments
if __name__ == "__main__":
    tracker = LocationTracker()
    
    # Add some reference points (example coordinates)
    tracker.add_reference_point(45.5152, -122.6784)  # Portland, OR area
    tracker.add_reference_point(45.5200, -122.6700)
    tracker.add_reference_point(45.5100, -122.6850)
    
    print("Location Tracker initialized")
    print("Add signal readings to track transmission sources")
    print("Use track_target() to analyze specific frequencies")