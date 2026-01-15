#!/usr/bin/env python3
"""
Victoria's Signal Interceptor - Brass-Age Radio Intelligence
A sophisticated radio frequency analyzer for intercepting and decoding transmissions

Built for the industrial frequencies of the diesel age, but adaptable
to modern signal analysis needs.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from datetime import datetime
import json
import base64
import re

class BrassAgeInterceptor:
    def __init__(self, sample_rate=44100):
        """Initialize the signal interceptor with period-appropriate settings"""
        self.sample_rate = sample_rate
        self.intercepted_signals = []
        self.frequency_patterns = {}
        
    def analyze_frequency_spectrum(self, audio_data):
        """
        Analyze the frequency spectrum of intercepted signals
        Returns dominant frequencies and their characteristics
        """
        # Perform FFT analysis
        frequencies = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        fft_values = np.fft.fft(audio_data)
        magnitude = np.abs(fft_values)
        
        # Find dominant frequencies
        peaks, _ = signal.find_peaks(magnitude, height=np.max(magnitude) * 0.1)
        dominant_freqs = frequencies[peaks]
        
        return {
            'dominant_frequencies': dominant_freqs.tolist(),
            'peak_magnitudes': magnitude[peaks].tolist(),
            'timestamp': datetime.now().isoformat()
        }
    
    def decode_morse_patterns(self, signal_data, threshold=0.5):
        """
        Detect and decode Morse code patterns in signal data
        """
        # Normalize signal
        normalized = np.abs(signal_data)
        normalized = normalized / np.max(normalized)
        
        # Convert to binary (on/off)
        binary_signal = (normalized > threshold).astype(int)
        
        # Find runs of 1s and 0s
        diff = np.diff(np.concatenate(([0], binary_signal, [0])))
        run_starts = np.where(diff == 1)[0]
        run_ends = np.where(diff == -1)[0]
        
        morse_elements = []
        for start, end in zip(run_starts, run_ends):
            duration = end - start
            if duration > 0:
                morse_elements.append(('signal', duration))
            # Add gap after signal (if not last element)
            if end < len(binary_signal) - 1:
                next_start = run_starts[np.where(run_starts > end)[0]]
                if len(next_start) > 0:
                    gap_duration = next_start[0] - end
                    morse_elements.append(('gap', gap_duration))
        
        return self._interpret_morse_timing(morse_elements)
    
    def _interpret_morse_timing(self, elements):
        """Convert timing elements to dots, dashes, and spaces"""
        if not elements:
            return ""
        
        # Analyze signal durations to determine dot/dash threshold
        signal_durations = [dur for typ, dur in elements if typ == 'signal']
        if not signal_durations:
            return ""
            
        avg_duration = np.mean(signal_durations)
        dot_dash_threshold = avg_duration * 1.5
        
        morse_code = ""
        for element_type, duration in elements:
            if element_type == 'signal':
                if duration < dot_dash_threshold:
                    morse_code += "."
                else:
                    morse_code += "-"
            elif element_type == 'gap':
                # Determine spacing based on gap duration
                if duration > avg_duration * 3:
                    morse_code += " / "  # Word separator
                elif duration > avg_duration:
                    morse_code += " "    # Letter separator
        
        return morse_code.strip()
    
    def intercept_radio_transmission(self, frequency_mhz, duration_seconds=10):
        """
        Simulate intercepting a radio transmission at specified frequency
        In practice, this would interface with SDR hardware
        """
        # Generate realistic-looking signal data for demonstration
        t = np.linspace(0, duration_seconds, int(self.sample_rate * duration_seconds))
        
        # Simulate a modulated signal with some noise
        carrier = np.sin(2 * np.pi * frequency_mhz * 1000 * t)  # Convert MHz to Hz
        modulation = signal.square(2 * np.pi * 5 * t) * 0.5 + 0.5  # 5 Hz modulation
        noise = np.random.normal(0, 0.1, len(t))
        
        intercepted = carrier * modulation + noise
        
        transmission_data = {
            'frequency_mhz': frequency_mhz,
            'duration': duration_seconds,
            'timestamp': datetime.now().isoformat(),
            'signal_data': intercepted.tolist()[:1000],  # Store first 1000 samples
            'analysis': self.analyze_frequency_spectrum(intercepted)
        }
        
        self.intercepted_signals.append(transmission_data)
        return transmission_data
    
    def decode_encrypted_message(self, encoded_message):
        """
        Attempt to decode common encryption schemes used in radio transmissions
        """
        decoders = {
            'base64': self._try_base64_decode,
            'caesar': self._try_caesar_decode,
            'reverse': lambda x: x[::-1],
            'atbash': self._try_atbash_decode
        }
        
        results = {}
        for method, decoder in decoders.items():
            try:
                decoded = decoder(encoded_message)
                if decoded and decoded != encoded_message:
                    results[method] = decoded
            except Exception as e:
                results[method] = f"Decode failed: {str(e)}"
        
        return results
    
    def _try_base64_decode(self, message):
        """Attempt base64 decoding"""
        try:
            # Clean the message of non-base64 characters
            cleaned = re.sub(r'[^A-Za-z0-9+/=]', '', message)
            decoded_bytes = base64.b64decode(cleaned)
            return decoded_bytes.decode('utf-8', errors='ignore')
        except:
            return None
    
    def _try_caesar_decode(self, message):
        """Try all possible Caesar cipher shifts"""
        results = []
        for shift in range(1, 26):
            decoded = ""
            for char in message:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    decoded += chr((ord(char) - base - shift) % 26 + base)
                else:
                    decoded += char
            results.append(f"Shift {shift}: {decoded}")
        return "\n".join(results[:5])  # Return first 5 attempts
    
    def _try_atbash_decode(self, message):
        """Apply Atbash cipher (A=Z, B=Y, etc.)"""
        decoded = ""
        for char in message:
            if char.isalpha():
                if char.isupper():
                    decoded += chr(ord('Z') - (ord(char) - ord('A')))
                else:
                    decoded += chr(ord('z') - (ord(char) - ord('a')))
            else:
                decoded += char
        return decoded
    
    def generate_frequency_report(self):
        """Generate a comprehensive report of all intercepted signals"""
        report = {
            'total_intercepted': len(self.intercepted_signals),
            'frequency_distribution': {},
            'timeline': [],
            'patterns_detected': []
        }
        
        for transmission in self.intercepted_signals:
            freq = transmission['frequency_mhz']
            if freq not in report['frequency_distribution']:
                report['frequency_distribution'][freq] = 0
            report['frequency_distribution'][freq] += 1
            
            report['timeline'].append({
                'timestamp': transmission['timestamp'],
                'frequency': freq,
                'dominant_freq_count': len(transmission['analysis']['dominant_frequencies'])
            })
        
        return report
    
    def save_intercept_log(self, filename="brass_intercepts.json"):
        """Save all intercepted data to file for analysis"""
        with open(filename, 'w') as f:
            json.dump({
                'interceptor_config': {'sample_rate': self.sample_rate},
                'signals': self.intercepted_signals,
                'report': self.generate_frequency_report()
            }, f, indent=2)
        
        return f"Intercept log saved to {filename}"


# Demonstration of the interceptor's capabilities
if __name__ == "__main__":
    print("=== Victoria's Signal Interceptor - Field Test ===")
    print("Initializing brass-age radio intelligence system...")
    
    interceptor = BrassAgeInterceptor()
    
    # Simulate intercepting several transmissions
    test_frequencies = [15.7, 22.3, 89.5, 101.1]  # MHz
    
    print("\nIntercepting transmissions...")
    for freq in test_frequencies:
        print(f"  Monitoring {freq} MHz...")
        transmission = interceptor.intercept_radio_transmission(freq, 5)
        print(f"    Captured signal with {len(transmission['analysis']['dominant_frequencies'])} dominant frequencies")
    
    # Generate report
    report = interceptor.generate_frequency_report()
    print(f"\n=== INTERCEPT SUMMARY ===")
    print(f"Total transmissions intercepted: {report['total_intercepted']}")
    print("Frequency distribution:")
    for freq, count in report['frequency_distribution'].items():
        print(f"  {freq} MHz: {count} transmissions")
    
    print(f"\nFull log saved: {interceptor.save_intercept_log()}")