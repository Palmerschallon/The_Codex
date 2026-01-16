#!/usr/bin/env python3
"""
Neural Resonance Scanner - The Prospector's Mind-Reader
Advanced EEG signal analysis and neural pattern recognition
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.fft import fft, fftfreq
import json
from datetime import datetime

class NeuralResonanceScanner:
    """
    Analyzes neural activity patterns from EEG-like signals
    Originally designed for mining equipment neural interfaces
    """
    
    def __init__(self, sample_rate=250):
        self.sample_rate = sample_rate
        self.frequency_bands = {
            'delta': (0.5, 4),    # Deep sleep, unconscious
            'theta': (4, 8),      # Creativity, memory
            'alpha': (8, 13),     # Relaxed awareness
            'beta': (13, 30),     # Active thinking
            'gamma': (30, 100)    # High-level cognitive processing
        }
        
    def load_neural_data(self, data_source):
        """Load neural data from various sources"""
        if isinstance(data_source, str):
            # Simulate loading from file
            return np.random.randn(1000) * 0.1
        else:
            return np.array(data_source)
    
    def extract_frequency_bands(self, eeg_data):
        """Extract power in different frequency bands"""
        freqs, psd = signal.welch(eeg_data, self.sample_rate)
        
        band_powers = {}
        for band_name, (low, high) in self.frequency_bands.items():
            band_mask = (freqs >= low) & (freqs <= high)
            band_powers[band_name] = np.mean(psd[band_mask])
            
        return band_powers
    
    def detect_cognitive_enhancement_potential(self, eeg_data):
        """
        Analyze neural patterns for enhancement potential
        Higher gamma/beta ratio suggests better neural plasticity
        """
        bands = self.extract_frequency_bands(eeg_data)
        
        # Calculate enhancement metrics
        cognitive_load = bands['beta'] + bands['gamma']
        baseline_activity = bands['alpha'] + bands['theta']
        
        enhancement_potential = cognitive_load / (baseline_activity + 1e-10)
        
        return {
            'enhancement_potential': enhancement_potential,
            'current_state': self._classify_mental_state(bands),
            'band_analysis': bands,
            'recommendations': self._generate_recommendations(bands)
        }
    
    def _classify_mental_state(self, bands):
        """Classify current mental state based on dominant frequency"""
        dominant_band = max(bands.keys(), key=lambda k: bands[k])
        
        states = {
            'delta': 'Deep unconscious processing',
            'theta': 'Creative/intuitive state',
            'alpha': 'Relaxed awareness',
            'beta': 'Active analytical thinking',
            'gamma': 'High-level cognitive processing'
        }
        
        return states.get(dominant_band, 'Unknown state')
    
    def _generate_recommendations(self, bands):
        """Generate enhancement recommendations"""
        recommendations = []
        
        if bands['gamma'] < 0.01:
            recommendations.append("Increase gamma activity through complex problem solving")
        
        if bands['beta'] / bands['alpha'] > 3:
            recommendations.append("Reduce stress - high beta/alpha ratio detected")
            
        if bands['theta'] > bands['beta']:
            recommendations.append("Engage analytical thinking to balance creativity")
            
        return recommendations
    
    def real_time_scan(self, duration_seconds=10):
        """Simulate real-time neural scanning"""
        print(f"Initiating neural scan for {duration_seconds} seconds...")
        print("Please remain still and focus on a complex problem...")
        
        # Simulate real-time data collection
        samples = int(self.sample_rate * duration_seconds)
        
        # Generate realistic EEG-like signal
        t = np.linspace(0, duration_seconds, samples)
        
        # Combine multiple frequency components
        signal_data = (
            0.1 * np.sin(2 * np.pi * 10 * t) +  # Alpha
            0.05 * np.sin(2 * np.pi * 20 * t) + # Beta
            0.02 * np.sin(2 * np.pi * 40 * t) + # Gamma
            0.01 * np.random.randn(samples)      # Noise
        )
        
        analysis = self.detect_cognitive_enhancement_potential(signal_data)
        
        return {
            'raw_data': signal_data,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    scanner = NeuralResonanceScanner()
    result = scanner.real_time_scan(5)
    
    print("\n=== NEURAL RESONANCE SCAN RESULTS ===")
    print(f"Enhancement Potential: {result['analysis']['enhancement_potential']:.3f}")
    print(f"Current State: {result['analysis']['current_state']}")
    print("\nFrequency Band Analysis:")
    for band, power in result['analysis']['band_analysis'].items():
        print(f"  {band.capitalize()}: {power:.4f}")
    
    print("\nRecommendations:")
    for rec in result['analysis']['recommendations']:
        print(f"  • {rec}")