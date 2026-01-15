#!/usr/bin/env python3
"""
Professor Morse's Telegraph Signal Monitor
A passive signal analysis system for monitoring multiple communication lines
"""

import time
import threading
from datetime import datetime
from collections import defaultdict, deque
import re

class TelegraphMonitor:
    def __init__(self):
        self.active_lines = {}
        self.message_buffer = defaultdict(deque)
        self.pattern_analysis = defaultdict(int)
        self.monitoring = False
        
    def connect_to_line(self, line_id, frequency=None):
        """Connect to a telegraph line for passive monitoring"""
        self.active_lines[line_id] = {
            'frequency': frequency or 'standard',
            'connected_at': datetime.now(),
            'message_count': 0,
            'last_activity': None
        }
        print(f"[MONITOR] Connected to line {line_id}")
        
    def decode_morse_patterns(self, signal_data):
        """Analyze morse code patterns for frequency and timing"""
        morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z',
            '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7',
            '---..': '8', '----.': '9'
        }
        
        # Split signal into morse tokens
        tokens = signal_data.strip().split(' ')
        decoded = []
        
        for token in tokens:
            if token in morse_dict:
                decoded.append(morse_dict[token])
            elif token == '':
                decoded.append(' ')
                
        return ''.join(decoded)
        
    def analyze_message_patterns(self, message, line_id):
        """Analyze patterns in intercepted messages"""
        timestamp = datetime.now()
        
        # Store in buffer for pattern analysis
        self.message_buffer[line_id].append({
            'timestamp': timestamp,
            'content': message,
            'length': len(message),
            'word_count': len(message.split())
        })
        
        # Keep only recent messages
        if len(self.message_buffer[line_id]) > 100:
            self.message_buffer[line_id].popleft()
            
        # Pattern analysis
        self.pattern_analysis[f"line_{line_id}_activity"] += 1
        if len(message) > 50:
            self.pattern_analysis["long_messages"] += 1
        if re.search(r'\b[A-Z]{3,}\b', message):
            self.pattern_analysis["code_words"] += 1
            
        return {
            'decoded_message': message,
            'timestamp': timestamp,
            'line_id': line_id,
            'suspicious_indicators': self._check_suspicious_patterns(message)
        }
        
    def _check_suspicious_patterns(self, message):
        """Check for unusual patterns that might indicate covert operations"""
        indicators = []
        
        # Frequent numbers (coordinates, times, quantities)
        if len(re.findall(r'\b\d+\b', message)) > 3:
            indicators.append("NUMERIC_HEAVY")
            
        # Repeated words or phrases
        words = message.split()
        if len(words) != len(set(words)):
            indicators.append("REPETITIVE_CONTENT")
            
        # All caps (urgent or coded)
        if message.isupper():
            indicators.append("ALL_CAPS")
            
        # Unusual timing (very short or very long messages)
        if len(message) < 10:
            indicators.append("UNUSUALLY_SHORT")
        elif len(message) > 200:
            indicators.append("UNUSUALLY_LONG")
            
        return indicators
        
    def start_monitoring(self, duration_minutes=30):
        """Begin passive monitoring of all connected lines"""
        self.monitoring = True
        print(f"[MONITOR] Beginning passive surveillance for {duration_minutes} minutes...")
        print("[MONITOR] Press Ctrl+C to stop early")
        
        try:
            # Simulate monitoring (in real use, this would interface with actual hardware)
            start_time = time.time()
            while self.monitoring and (time.time() - start_time) < duration_minutes * 60:
                for line_id in self.active_lines:
                    # Simulate receiving signals (replace with actual signal capture)
                    if self._simulate_activity():
                        signal = self._simulate_signal_capture(line_id)
                        if signal:
                            decoded = self.decode_morse_patterns(signal)
                            result = self.analyze_message_patterns(decoded, line_id)
                            self._display_intercept(result)
                            
                time.sleep(2)  # Check every 2 seconds
                
        except KeyboardInterrupt:
            print("\n[MONITOR] Monitoring stopped by operator")
        finally:
            self.monitoring = False
            
    def _simulate_activity(self):
        """Simulate telegraph activity (replace with real signal detection)"""
        import random
        return random.random() < 0.15  # 15% chance per check
        
    def _simulate_signal_capture(self, line_id):
        """Simulate capturing morse code signals"""
        # Sample intercepted messages for testing
        sample_signals = [
            "... .... .. .--. -- . -. - / .- .-. .-. .. ...- . ... / - --- -- --- .-. .-. --- .--",
            ".--. .- - .-. --- .-.. / ... -.-. .... . -.. ..- .-.. . / -.-. .... .- -. --. . -..",
            "--- .--. . .-. .- - .. --- -. / -... .-.. .- -.-. -.- / ..-. .-. .. -.. .- -.--",
            ".- .-.. .-.. / ..- -. .. - ... / .-. . .--. --- .-. - / ... - .- - ..- ...",
            "... ..- .-. ...- . -.-- / - . .- -- / ..-. --- ..- -. -.. / ... .. --. -. .- .-.. ..."
        ]
        
        import random
        return random.choice(sample_signals)
        
    def _display_intercept(self, result):
        """Display intercepted message with analysis"""
        print(f"\n[{result['timestamp'].strftime('%H:%M:%S')}] LINE-{result['line_id']}")
        print(f"MESSAGE: {result['decoded_message']}")
        if result['suspicious_indicators']:
            print(f"ALERTS: {', '.join(result['suspicious_indicators'])}")
        print("-" * 50)
        
    def generate_report(self):
        """Generate a summary report of monitoring session"""
        print("\n" + "="*60)
        print("TELEGRAPH MONITORING REPORT")
        print("="*60)
        
        total_messages = sum(len(buffer) for buffer in self.message_buffer.values())
        print(f"Total Messages Intercepted: {total_messages}")
        print(f"Active Lines Monitored: {len(self.active_lines)}")
        
        print(f"\nPattern Analysis:")
        for pattern, count in self.pattern_analysis.items():
            print(f"  {pattern}: {count}")
            
        print(f"\nLine Activity Summary:")
        for line_id, info in self.active_lines.items():
            msg_count = len(self.message_buffer.get(line_id, []))
            print(f"  Line {line_id}: {msg_count} messages")
            
if __name__ == "__main__":
    # Professor Morse's monitoring session
    monitor = TelegraphMonitor()
    
    print("Professor Morse's Telegraph Signal Monitor")
    print("Initializing passive surveillance equipment...")
    
    # Connect to the mysterious lines
    monitor.connect_to_line("NORTH", "high_frequency")
    monitor.connect_to_line("EAST", "standard") 
    monitor.connect_to_line("MAIN", "encrypted")
    
    # Begin monitoring
    monitor.start_monitoring(duration_minutes=10)
    
    # Generate report
    monitor.generate_report()