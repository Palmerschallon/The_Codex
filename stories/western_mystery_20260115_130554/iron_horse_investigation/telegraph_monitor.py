#!/usr/bin/env python3
"""
Professor Adelaide Morse's Telegraph Signal Analyzer
A tool for monitoring and analyzing telegraph communication patterns
"""

import re
import time
from collections import defaultdict, Counter
from datetime import datetime
import statistics

class TelegraphMonitor:
    """Monitor and analyze morse code patterns and telegraph communications"""
    
    def __init__(self):
        self.morse_code = {
            'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
            'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
            'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
            'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
            'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
            '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
            '8': '---..', '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..',
            ' ': '/'
        }
        self.reverse_morse = {v: k for k, v in self.morse_code.items()}
        self.message_log = []
        self.pattern_stats = defaultdict(int)
        self.timing_analysis = []
        
    def decode_morse(self, morse_text):
        """Convert morse code to readable text"""
        try:
            words = morse_text.split(' / ')
            decoded_words = []
            
            for word in words:
                letters = word.split(' ')
                decoded_letters = []
                for letter in letters:
                    if letter.strip() in self.reverse_morse:
                        decoded_letters.append(self.reverse_morse[letter.strip()])
                    else:
                        decoded_letters.append('?')
                decoded_words.append(''.join(decoded_letters))
            
            return ' '.join(decoded_words)
        except Exception as e:
            return f"DECODE_ERROR: {str(e)}"
    
    def encode_morse(self, text):
        """Convert text to morse code"""
        morse_words = []
        for word in text.upper().split():
            morse_letters = []
            for char in word:
                if char in self.morse_code:
                    morse_letters.append(self.morse_code[char])
                else:
                    morse_letters.append('?')
            morse_words.append(' '.join(morse_letters))
        return ' / '.join(morse_words)
    
    def analyze_signal_patterns(self, messages):
        """Analyze patterns in telegraph messages for anomalies"""
        analysis = {
            'total_messages': len(messages),
            'avg_length': 0,
            'common_patterns': [],
            'timing_anomalies': [],
            'suspicious_repeats': [],
            'frequency_analysis': {},
            'routing_patterns': defaultdict(int)
        }
        
        if not messages:
            return analysis
            
        # Message length analysis
        lengths = [len(msg.get('content', '')) for msg in messages]
        analysis['avg_length'] = round(statistics.mean(lengths), 2)
        analysis['length_std'] = round(statistics.stdev(lengths) if len(lengths) > 1 else 0, 2)
        
        # Pattern detection
        content_patterns = []
        for msg in messages:
            content = msg.get('content', '').upper()
            # Look for repeated sequences
            words = content.split()
            for i in range(len(words)):
                for j in range(i+1, min(i+5, len(words)+1)):
                    pattern = ' '.join(words[i:j])
                    if len(pattern) > 10:  # Only significant patterns
                        content_patterns.append(pattern)
        
        pattern_counts = Counter(content_patterns)
        analysis['common_patterns'] = [(pattern, count) for pattern, count in pattern_counts.most_common(10)]
        analysis['suspicious_repeats'] = [(pattern, count) for pattern, count in pattern_counts.items() if count >= 3]
        
        # Timing analysis
        timestamps = [msg.get('timestamp', 0) for msg in messages if 'timestamp' in msg]
        if len(timestamps) > 1:
            intervals = []
            for i in range(1, len(timestamps)):
                intervals.append(timestamps[i] - timestamps[i-1])
            
            # Look for suspiciously regular intervals
            interval_counts = Counter([round(interval, 1) for interval in intervals])
            regular_intervals = [(interval, count) for interval, count in interval_counts.items() if count >= 3]
            analysis['timing_anomalies'] = regular_intervals
        
        # Route analysis
        for msg in messages:
            origin = msg.get('origin', 'UNKNOWN')
            destination = msg.get('destination', 'UNKNOWN')
            route = f"{origin} -> {destination}"
            analysis['routing_patterns'][route] += 1
        
        return analysis
    
    def detect_cipher_type(self, text):
        """Attempt to identify cipher types in intercepted messages"""
        text = text.strip().upper()
        
        # Simple frequency analysis
        char_freq = Counter(c for c in text if c.isalpha())
        total_chars = sum(char_freq.values())
        
        if total_chars == 0:
            return "NO_TEXT"
        
        # Calculate letter frequency distribution
        freq_dist = {char: count/total_chars for char, count in char_freq.items()}
        
        # English letter frequency (approximate)
        english_freq = {'E': 0.127, 'T': 0.091, 'A': 0.082, 'O': 0.075, 'I': 0.070}
        
        # Check if frequency distribution matches English
        common_chars = [char for char, freq in sorted(freq_dist.items(), key=lambda x: x[1], reverse=True)][:5]
        english_score = sum(1 for char in common_chars if char in english_freq)
        
        # Pattern detection
        if re.match(r'^[A-Z\s]+$', text) and english_score >= 3:
            return "PLAINTEXT"
        elif re.match(r'^[A-Z\s]+$', text) and english_score <= 1:
            return "SUBSTITUTION_CIPHER"
        elif re.match(r'^[0-9\s]+$', text):
            return "NUMERIC_CODE"
        elif len(set(text)) < len(text) * 0.6:  # Low character diversity
            return "BOOK_CIPHER"
        else:
            return "COMPLEX_CIPHER"
    
    def log_message(self, content, origin="UNKNOWN", destination="UNKNOWN", timestamp=None):
        """Log an intercepted message for analysis"""
        if timestamp is None:
            timestamp = time.time()
            
        message = {
            'content': content,
            'origin': origin,
            'destination': destination,
            'timestamp': timestamp,
            'cipher_type': self.detect_cipher_type(content),
            'length': len(content),
            'logged_at': datetime.now().isoformat()
        }
        
        self.message_log.append(message)
        return message
    
    def generate_report(self):
        """Generate a comprehensive analysis report of intercepted traffic"""
        if not self.message_log:
            return "No messages intercepted yet."
            
        analysis = self.analyze_signal_patterns(self.message_log)
        
        report = [
            "=== TELEGRAPH TRAFFIC ANALYSIS REPORT ===",
            f"Analysis Period: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Messages Intercepted: {analysis['total_messages']}",
            f"Average Message Length: {analysis['avg_length']} characters",
            "",
            "ROUTING PATTERNS:",
        ]
        
        for route, count in sorted(analysis['routing_patterns'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {route}: {count} messages")
        
        report.extend([
            "",
            "CIPHER TYPES DETECTED:",
        ])
        
        cipher_counts = Counter(msg['cipher_type'] for msg in self.message_log)
        for cipher_type, count in cipher_counts.items():
            report.append(f"  {cipher_type}: {count} messages")
        
        if analysis['suspicious_repeats']:
            report.extend([
                "",
                "SUSPICIOUS REPEATED PATTERNS:",
            ])
            for pattern, count in analysis['suspicious_repeats']:
                report.append(f"  '{pattern}' repeated {count} times")
        
        if analysis['timing_anomalies']:
            report.extend([
                "",
                "TIMING ANOMALIES:",
            ])
            for interval, count in analysis['timing_anomalies']:
                report.append(f"  {interval}s interval appears {count} times")
        
        return '\n'.join(report)

# Example usage for the story
if __name__ == "__main__":
    monitor = TelegraphMonitor()
    
    # Simulate intercepted messages from the mysterious facility
    sample_messages = [
        "COPPER SHIPMENT DELAYED STOP AWAIT INSTRUCTIONS STOP",
        "XIBXF FXFXF KTZIF VXMGM STOP",  # Encrypted message
        "SURVEYOR TEAMS REPORT ANOMALIES SECTOR 7 STOP",
        "PAYMENT AUTHORIZED AMOUNT 50000 STOP MAINTAIN SECRECY STOP",
        "XIBXF FXFXF KTZIF VXMGM STOP",  # Repeated encrypted message
    ]
    
    # Log the intercepted messages
    for i, msg in enumerate(sample_messages):
        origin = ["DENVER", "UNKNOWN", "PERDITION", "SAN_FRANCISCO", "UNKNOWN"][i]
        destination = ["PERDITION", "BLACKROCK", "MILITARY_POST", "BLACKROCK", "BLACKROCK"][i]
        monitor.log_message(msg, origin, destination)
    
    print(monitor.generate_report())