#!/usr/bin/env python3
"""
THE CODEX - Demo Mode
Simulates a gameplay session for recording/demonstration.
No API key needed - plays back a pre-scripted story.

Record with: asciinema rec demo.cast
Then upload to asciinema.org or convert to gif
"""

import os
import time
import sys

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def slow_print(text, delay=0.02):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def stream_text(text, char_delay=0.008, line_delay=0.03):
    lines = text.split('\n')
    for line in lines:
        for char in line:
            print(char, end='', flush=True)
            time.sleep(char_delay)
        print()
        time.sleep(line_delay)

def fake_input(prompt, response, delay=1.5):
    """Simulate user typing"""
    print(prompt, end='', flush=True)
    time.sleep(0.5)
    for char in response:
        print(char, end='', flush=True)
        time.sleep(0.08)
    time.sleep(delay)
    print()
    return response

def thinking_animation(text, duration=3):
    """Show a simple single-line loading animation"""
    color = '\033[35m'  # magenta for cyberpunk
    reset = '\033[0m'
    dim = '\033[2m'

    bar_width = 20
    position = 0
    direction = 1

    start_time = time.time()
    while time.time() - start_time < duration:
        bar = ""
        for i in range(bar_width):
            if i == position or i == position - 1 or i == position + 1:
                bar += "█"
            else:
                bar += "░"

        # Single line, just carriage return to overwrite
        print(f'\r    {dim}{text:<30}{reset} {color}[{bar}]{reset}', end='', flush=True)

        position += direction
        if position >= bar_width - 1:
            direction = -1
        elif position <= 0:
            direction = 1

        time.sleep(0.08)

    # Clear the line and move to next
    print(f'\r{" " * 70}\r', end='', flush=True)
    print()

def artifact_box(filename, lines, path):
    """Show the artifact creation box"""
    color = '\033[35m'
    reset = '\033[0m'
    dim = '\033[2m'
    bold = '\033[1m'

    print()
    print(f"    {color}┌{'─' * 50}┐{reset}")
    print(f"    {color}│{reset} {bold}ARTIFACTS CREATED{reset}{' ' * 32}{color}│{reset}")
    print(f"    {color}├{'─' * 50}┤{reset}")
    print(f"    {color}│{reset}  ◆ {filename:<35} {dim}({lines} lines){reset} {color}│{reset}")
    print(f"    {color}│{reset}    {dim}{path}{reset}")
    print(f"    {color}│{reset}{' ' * 49}{color}│{reset}")
    print(f"    {color}├{'─' * 50}┤{reset}")
    print(f"    {color}│{reset}  ↑ {dim}Synced to GitHub{reset}{' ' * 31}{color}│{reset}")
    print(f"    {color}└{'─' * 50}┘{reset}")
    print()

def run_demo():
    clear()
    time.sleep(0.5)

    # === OPENING ===
    print()
    lines = [
        "",
        "        ═══════════════════════════════════════════════════",
        "",
        "                        T H E   C O D E X",
        "",
        "        ═══════════════════════════════════════════════════",
        "",
    ]
    for line in lines:
        print(line)
        time.sleep(0.05)

    time.sleep(0.3)
    slow_print("        A text-based novel where code is the story.")
    print()
    time.sleep(0.2)
    slow_print("        The files you create are real.")
    slow_print("        The code you write executes.")
    slow_print("        The world builds itself around you.")
    print()
    time.sleep(0.5)

    # === MODE SELECT ===
    print("        ┌─────────────────────────────────────────────┐")
    print("        │                                             │")
    print("        │   [1] BUILD   - I know what I want to make  │")
    print("        │   [2] STORY   - I want to explore           │")
    print("        │                                             │")
    print("        └─────────────────────────────────────────────┘")
    print()

    fake_input("        > ", "2")
    print("        [Mode: STORY]")

    # === GENRE SELECT ===
    print()
    print("        What genre? (mystery, horror, scifi western,")
    print("        cyberpunk noir, post-apocalyptic comedy...)")
    print("        Or press Enter for random.")
    print()

    fake_input("        > ", "cyberpunk noir")

    print()
    print("    Story: cyberpunk_noir_20260115_084532")
    print("    Artifacts: github.com/Palmerschallon/The_Codex/stories/cyberpunk_noir_20260115_084532")
    print()
    print("=" * 60)
    print()

    # === OPENING SCENE ===
    thinking_animation("Jacking into the matrix...", duration=4)

    opening = """The neon bled through rain-slicked windows, painting Kira's apartment
in shades of electric blue and warning red. She hadn't slept in three days.
Couldn't afford to—not with half the corps in Neo-Shanghai hunting her.

The data chip in her jacket pocket felt like a death sentence. Forty terabytes
of Nexus Corp's darkest secrets, and she was the only one who knew it existed.

Her terminal flickered. A message from an unknown sender:

    > THEY KNOW WHERE YOU ARE.
    > GET TO THE UNDERCITY.
    > FIND GHOST. HE CAN DECRYPT IT.

The building's security system chimed. Someone was coming up.

What do you do?"""

    stream_text(opening)

    print()
    print("-" * 60)
    print("    Type anything to interact. 'quit' to end.")
    print("-" * 60)

    # === PLAYER ACTION 1 ===
    print()
    fake_input("> ", "hack the building security to see who's coming", delay=2)

    thinking_animation("ICE protocols detected...", duration=3)

    response1 = """Kira's fingers flew across her neural keyboard, the haptic feedback
pulsing against her synapses. Building security was corporate-grade, but she'd
cut her teeth on Nexus systems. This was almost nostalgic.

She wrote a quick intrusion script—something to slip past the ICE without
triggering the countermeasures."""

    stream_text(response1)

    artifact_box(
        "security_scanner.py",
        "89",
        "/stories/cyberpunk_noir_.../security_scanner.py"
    )

    time.sleep(0.5)

    response1b = """The feed resolved into focus. Three figures in the elevator.
Corporate extraction team—she recognized the Nexus tactical gear.
They had maybe ninety seconds before they reached her floor.

But the scanner revealed something else: a maintenance shaft on the
north side of the building, and a gap in their drone coverage.

"Ghost better be worth this," she muttered, grabbing her deck."""

    stream_text(response1b)

    # === PLAYER ACTION 2 ===
    print()
    fake_input("> ", "escape through the maintenance shaft", delay=2)

    thinking_animation("Chrome dreams loading...", duration=3)

    response2 = """The shaft was tight, filled with cables and the hum of the building's
nervous system. Kira pulled herself through, her cybernetic arm finding
grip where flesh would have slipped.

Behind her, she heard the door to her apartment splinter.

Below, the Undercity waited—a maze of forgotten infrastructure where
the corps didn't bother to look. Where people like Ghost made their home.

She dropped into darkness, and the neon world above disappeared."""

    stream_text(response2)

    print()
    print()
    print("    " + "─" * 50)
    print("    \033[2mStory auto-saved to GitHub • checkpoint #2\033[0m")
    print("    " + "─" * 50)
    print()

    time.sleep(2)

    # === END DEMO ===
    print()
    slow_print("    *Demo complete. The story continues...*")
    print()
    slow_print("    Clone the repo and play for real:")
    print()
    print("    git clone https://github.com/Palmerschallon/The_Codex.git")
    print("    python the_codex.py")
    print()
    time.sleep(3)

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n    *Demo interrupted*\n")
