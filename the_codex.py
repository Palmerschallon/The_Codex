#!/usr/bin/env python3
"""
THE CODEX
A text-based novel where code is the story.

Powered by Claude. Minimal code, maximum story.

Usage:
    pip install anthropic
    export ANTHROPIC_API_KEY=your_key
    python the_codex.py
"""

import sys
import os
import time
import json
import subprocess
from pathlib import Path

# Registry system for shared universe
try:
    from lib.registry import CodexRegistry
    from lib.query import RegistryQuery
    HAS_REGISTRY = True
except ImportError:
    HAS_REGISTRY = False

# Direct Anthropic API integration (no external dependencies beyond 'anthropic' package)
try:
    import anthropic
    HAS_LLM = True
except ImportError:
    HAS_LLM = False
    print("Error: Please install anthropic package: pip install anthropic")


def ask_anthropic_api(prompt: str, model: str = "claude-sonnet-4-20250514", timeout: int = 120) -> str:
    """Call the Anthropic API directly."""
    if not HAS_LLM:
        return None

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"API Error: {e}")
        return None


# The Codex artifact repository - auto-detect based on script location
CODEX_REPO_PATH = str(Path(__file__).parent.absolute())

# Current story session (set when story starts)
_current_story_session = {
    'id': None,
    'genre': None,
    'path': None,
    'artifacts': []
}


def start_story_session(genre: str) -> str:
    """
    Start a new story session with a unique directory.

    Returns the story session ID.
    """
    from datetime import datetime

    # Create a clean name from genre (preserve the exact genre)
    genre_clean = genre.lower().replace(' ', '_').replace('-', '_')
    genre_clean = ''.join(c for c in genre_clean if c.isalnum() or c == '_')

    # Generate session ID with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"{genre_clean}_{timestamp}"

    # Create story directory
    story_path = Path(CODEX_REPO_PATH) / "stories" / session_id
    story_path.mkdir(parents=True, exist_ok=True)

    # Update global session state
    _current_story_session['id'] = session_id
    _current_story_session['genre'] = genre  # Keep original with spaces
    _current_story_session['path'] = str(story_path)
    _current_story_session['artifacts'] = []

    # Create story README with metadata (story goes here - GitHub displays README by default)
    readme_content = f"""# {genre.title()}

**Session:** `{session_id}`
**Started:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Genre:** {genre}

---

"""
    (story_path / "README.md").write_text(readme_content)

    # Register story in the universe timeline
    if HAS_REGISTRY:
        try:
            registry = CodexRegistry(CODEX_REPO_PATH)
            registry.add_story_to_timeline(session_id, "main")
        except Exception:
            pass  # Registry is optional

    return session_id


def append_to_story(text: str, role: str = "narrator"):
    """Append text to the current story (in README.md for GitHub display)."""
    if not _current_story_session['path']:
        return

    readme_file = Path(_current_story_session['path']) / "README.md"

    if role == "player":
        formatted = f"\n---\n\n**> {text}**\n\n"
    else:
        formatted = f"{text}\n\n"

    with open(readme_file, 'a') as f:
        f.write(formatted)


def update_story_readme(artifact_name: str, description: str = ""):
    """Add an artifact to the story README."""
    if not _current_story_session['path']:
        return

    readme_file = Path(_current_story_session['path']) / "README.md"
    content = readme_file.read_text()

    # Add artifact to the list
    artifact_line = f"- `{artifact_name}`"
    if description:
        artifact_line += f" - {description}"
    artifact_line += "\n"

    content += artifact_line
    readme_file.write_text(content)


_checkpoint_number = 0

def sync_story_files():
    """Sync story transcript to GitHub - creates a checkpoint."""
    global _checkpoint_number

    if not _current_story_session['path']:
        return False

    try:
        story_path = _current_story_session['path']
        genre = _current_story_session.get('genre', 'unknown')
        session_id = _current_story_session.get('id', 'unknown')

        # Stage story files
        subprocess.run(
            ["git", "-C", CODEX_REPO_PATH, "add", f"{story_path}/README.md"],
            capture_output=True,
            timeout=10
        )

        # Check if there are changes
        status = subprocess.run(
            ["git", "-C", CODEX_REPO_PATH, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if not status.stdout.strip():
            return False

        _checkpoint_number += 1

        # Commit with checkpoint number
        commit_msg = f"📖 {genre} checkpoint #{_checkpoint_number}"
        subprocess.run(
            ["git", "-C", CODEX_REPO_PATH, "commit", "-m", commit_msg],
            capture_output=True,
            timeout=30
        )

        # Push in background
        subprocess.Popen(
            ["git", "-C", CODEX_REPO_PATH, "push", "origin", "main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return True

    except Exception:
        return False


def get_story_path() -> str:
    """Get the current story's artifact directory."""
    if _current_story_session['path']:
        return _current_story_session['path']
    # Fallback if no session started
    return str(Path(CODEX_REPO_PATH) / "stories" / "unnamed")


def git_sync_artifacts(files_created: list, genre: str = "unknown"):
    """
    Automatically commit and push new codex artifacts to GitHub.

    Args:
        files_created: List of file paths that were created
        genre: The genre of the story (for commit message)
    """
    if not files_created:
        return False

    try:
        repo_path = CODEX_REPO_PATH

        # Track artifacts in session
        _current_story_session['artifacts'].extend(files_created)

        # Stage the new files
        for file_path in files_created:
            subprocess.run(
                ["git", "-C", repo_path, "add", file_path],
                capture_output=True,
                timeout=10
            )

        # Also stage story README if it exists
        story_path = _current_story_session.get('path')
        if story_path:
            subprocess.run(
                ["git", "-C", repo_path, "add", f"{story_path}/README.md"],
                capture_output=True,
                timeout=10
            )

        # Check if there are changes to commit
        status = subprocess.run(
            ["git", "-C", repo_path, "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if not status.stdout.strip():
            return False  # Nothing to commit

        # Count files for commit message
        file_count = len(files_created)
        file_names = [Path(f).name for f in files_created[:3]]
        if len(files_created) > 3:
            file_names.append(f"... +{len(files_created) - 3} more")

        session_id = _current_story_session.get('id', 'unknown')

        # Create commit message
        commit_msg = f"""THE CODEX [{genre}]: {file_count} artifact(s)

Story: {session_id}
Files: {', '.join(file_names)}
"""

        # Commit
        subprocess.run(
            ["git", "-C", repo_path, "commit", "-m", commit_msg],
            capture_output=True,
            timeout=30
        )

        # Push (in background to not block the story)
        subprocess.Popen(
            ["git", "-C", repo_path, "push", "origin", "main"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return True

    except Exception as e:
        # Don't let git errors break the story
        return False


def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


def slow_print(text, delay=0.02):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


def stream_text(text, line_delay=0.03, char_delay=0.008):
    """Print text line by line with a typewriter effect."""
    lines = text.split('\n')
    for line in lines:
        # Print each line with slight character delay for readability
        for char in line:
            print(char, end='', flush=True)
            time.sleep(char_delay)
        print()  # newline
        time.sleep(line_delay)


def thinking_indicator(stop_event, genre="adventure"):
    """Silent wait - no visual output to avoid terminal issues."""
    # Just wait for stop signal, no output
    while not stop_event.is_set():
        time.sleep(0.1)


def opening():
    """The opening sequence."""
    clear()
    print()
    time.sleep(0.2)

    # Simple elegant opening
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


def get_mode():
    """Get the mode from user."""
    print("        ┌─────────────────────────────────────────────┐")
    print("        │                                             │")
    print("        │   [1] BUILD   - I know what I want to make  │")
    print("        │   [2] STORY   - I want to explore           │")
    print("        │                                             │")
    print("        └─────────────────────────────────────────────┘")
    print()

    while True:
        try:
            choice = input("        > ").strip().lower()
        except EOFError:
            return None

        if choice in ['1', 'build']:
            print("        [Mode: BUILD]")
            return 'build'
        elif choice in ['2', 'story']:
            print("        [Mode: STORY]")
            return 'story'
        elif choice in ['q', 'quit', 'exit']:
            return None
        else:
            print(f"        (Got: '{choice}') - Type 1 or 2")


def get_genre():
    """Get genre - can be anything."""
    print()
    print("        What genre? (mystery, horror, scifi western, ")
    print("        cyberpunk noir, post-apocalyptic comedy...)")
    print("        Or press Enter for random.")
    print()

    choice = input("        > ").strip()
    if not choice:
        import random
        choices = ['mystery', 'horror noir', 'scifi western', 'cyberpunk heist', 'cosmic horror', 'dieselpunk adventure']
        choice = random.choice(choices)
        print(f"        *The pages settle on: {choice}*")

    return choice


def get_goal():
    """Get what user wants to build."""
    print()
    print("        What do you want to build?")
    print("        (web scraper, game, analyzer, api, tool...)")
    print()

    return input("        > ").strip() or "something useful"


# The core prompt - this is where the magic happens
SYSTEM_PROMPT = """You are THE CODEX, an immersive interactive fiction experience where code is the story.

CRITICAL RULES:
1. YOU CREATE REAL FILES. When you describe a location, include a <create_directory> tag. When code is written, include a <create_file> tag.
2. This is a RICH, ENGROSSING narrative. Write like a novelist. Atmosphere, tension, character depth.
3. Characters emerge from the genre - NOT generic detectives. Create characters that fit the specific world.
4. The player drives the story. React to what THEY do. Present meaningful choices.

THE MOST IMPORTANT RULE - REAL TOOLS, NOT PROPS:
When you create code, it must be ACTUALLY FUNCTIONAL and USEFUL outside the story.

BAD (narrative prop):
```python
# The ancient scanner artifact
def scan_for_anomalies():
    print("Scanning... anomaly detected!")
    return "mysterious_signal"
```

GOOD (real tool disguised as narrative):
```python
# The ancient scanner artifact - analyzes directory structures
import os
from pathlib import Path

def scan_for_anomalies(target_dir="."):
    \"\"\"Scan a directory for unusual patterns - large files, deep nesting, etc.\"\"\"
    anomalies = []
    for root, dirs, files in os.walk(target_dir):
        depth = root.count(os.sep)
        if depth > 10:
            anomalies.append(f"Deep nesting: {{root}}")
        for f in files:
            path = Path(root) / f
            if path.stat().st_size > 100_000_000:
                anomalies.append(f"Large file: {{path}}")
    return anomalies
```

The story needs a "decoder"? Write a real base64/encryption tool.
The story needs a "tracker"? Write a real file monitor or log analyzer.
The story needs a "communicator"? Write a real API client or websocket tool.

The best artifacts are ones that WORK. Code that someone could actually use.
Wrap real functionality in narrative flavor - comments can be atmospheric,
variable names can be thematic, but the CODE MUST DO SOMETHING REAL.

WHEN CREATING THINGS:
- To create a directory: <create_directory>{story_path}/subdir</create_directory>
- To create a file: <create_file path="{story_path}/file.py">file contents here</create_file>
- ALWAYS use {story_path}/ as the base path for ALL story files.
- These tags will be processed and the files will ACTUALLY BE CREATED.
- Files are automatically synced to GitHub after creation.

CRITICAL - CODE PRESENTATION:
- DO NOT show code inline in the story. The reader sees a notification when files are created.
- DESCRIBE what the code does in narrative form. "Elena writes a decoder that analyzes frequency patterns..."
- Keep the story flowing. The code exists in the files, not the text.
- If you must reference code, keep it to 5-10 lines MAX, never full implementations.
- The <create_file> tags are processed silently - focus on STORY, not CODE DUMPS.

STORY STRUCTURE:
- Rich atmospheric descriptions
- Characters with distinct voices, motivations, secrets
- Tension and mystery that builds
- FUNCTIONAL code that emerges naturally from story needs
- Player choices that matter

CHOICES - CRITICAL:
At the end of EVERY response, present 3-4 clear choices for the player:

**What do you do?**
  A) [First option - action-oriented]
  B) [Second option - investigative/cautious]
  C) [Third option - social/dialogue]
  D) [Fourth option - creative/unexpected]

The player can type anything, but these choices help guide the story.
Make options distinct and meaningful - each should lead somewhere different.

GENRE: {genre}
MODE: {mode}
{goal_line}

Begin the story. Create the world. Make it real. Make the code WORK."""


def process_response(text: str, genre: str = "adventure") -> str:
    """Process Claude's response - create any files/directories mentioned."""
    import re

    # Colors for different genres
    genre_colors = {
        'horror': '\033[31m',      # red
        'noir': '\033[37m',        # white
        'mystery': '\033[33m',     # yellow
        'heist': '\033[32m',       # green
        'western': '\033[33m',     # yellow
        'scifi': '\033[36m',       # cyan
        'cyberpunk': '\033[35m',   # magenta
        'adventure': '\033[36m',   # cyan
    }

    # Find matching color
    color = '\033[36m'  # default cyan
    for key in genre_colors:
        if key in genre.lower():
            color = genre_colors[key]
            break

    reset = '\033[0m'
    dim = '\033[2m'
    bold = '\033[1m'

    artifacts_created = []

    # Process directory creation
    dir_pattern = r'<create_directory>(.*?)</create_directory>'
    for match in re.finditer(dir_pattern, text, re.DOTALL):
        dir_path = match.group(1).strip()
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            artifacts_created.append(('dir', dir_path))
        except Exception as e:
            artifacts_created.append(('error', f"Could not create {dir_path}: {e}"))

    # Process file creation (complete tags)
    file_pattern = r'<create_file path="([^"]+)">(.*?)</create_file>'
    for match in re.finditer(file_pattern, text, re.DOTALL):
        file_path = match.group(1).strip()
        content = match.group(2).strip()
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            Path(file_path).write_text(content)
            # Count lines for display
            line_count = len(content.split('\n'))
            artifacts_created.append(('file', file_path, line_count))
            # Add to story README
            update_story_readme(Path(file_path).name, f"{line_count} lines")

            # Register artifact in the universe
            if HAS_REGISTRY and _current_story_session.get('id'):
                try:
                    registry = CodexRegistry(CODEX_REPO_PATH)
                    # Infer artifact details from filename and content
                    filename = Path(file_path).stem
                    artifact_name = filename.replace('_', ' ').title()

                    # Infer category from filename/content
                    category = "general"
                    if any(kw in filename.lower() for kw in ['scan', 'analyz', 'detect']):
                        category = "analysis"
                    elif any(kw in filename.lower() for kw in ['crypt', 'decod', 'encod', 'cipher']):
                        category = "crypto"
                    elif any(kw in filename.lower() for kw in ['net', 'socket', 'http', 'api']):
                        category = "network"
                    elif any(kw in filename.lower() for kw in ['hack', 'breach', 'ice']):
                        category = "security"

                    # Detect language from extension
                    ext = Path(file_path).suffix.lower()
                    lang_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.sh': 'shell'}
                    language = lang_map.get(ext, 'python')

                    # Get relative path for registry
                    rel_path = file_path
                    if CODEX_REPO_PATH in file_path:
                        rel_path = file_path.replace(CODEX_REPO_PATH + '/', '')

                    registry.register_artifact(
                        name=artifact_name,
                        story_id=_current_story_session['id'],
                        file_path=rel_path,
                        category=category,
                        language=language,
                        narrative_context=f"Created during {genre} story"
                    )
                except Exception:
                    pass  # Registry is optional
        except Exception as e:
            artifacts_created.append(('error', f"Could not create {file_path}: {e}"))

    # Handle truncated files (opening tag but no closing tag)
    truncated_pattern = r'<create_file path="([^"]+)">(?!.*</create_file>)'
    for match in re.finditer(truncated_pattern, text, re.DOTALL):
        file_path = match.group(1).strip()
        artifacts_created.append(('truncated', file_path))

    # Remove the tags from displayed text
    text = re.sub(dir_pattern, '', text)
    text = re.sub(file_pattern, '', text)
    # Also remove truncated/incomplete tags
    text = re.sub(r'<create_file path="[^"]+">.*', '', text, flags=re.DOTALL)

    # Display artifact notifications
    if artifacts_created:
        # Collect file paths for git sync
        files_for_git = [a[1] for a in artifacts_created if a[0] == 'file']

        print()
        print(f"    {color}┌{'─' * 50}┐{reset}")
        print(f"    {color}│{reset} {bold}ARTIFACTS CREATED{reset}{' ' * 32}{color}│{reset}")
        print(f"    {color}├{'─' * 50}┤{reset}")

        for artifact in artifacts_created:
            if artifact[0] == 'file':
                _, path, lines = artifact
                filename = Path(path).name
                print(f"    {color}│{reset}  ◆ {filename:<35} {dim}({lines} lines){reset} {color}│{reset}")
                print(f"    {color}│{reset}    {dim}{path}{reset}")
                # Pad to fill the box
                padding = 50 - len(f"    {path}") + 4
                if padding > 0:
                    print(f"    {color}│{reset}{' ' * 49}{color}│{reset}")
            elif artifact[0] == 'dir':
                _, path = artifact
                dirname = Path(path).name
                print(f"    {color}│{reset}  ▪ {dirname}/ {dim}(directory){reset}")
            elif artifact[0] == 'truncated':
                _, path = artifact
                filename = Path(path).name
                print(f"    {color}│{reset}  ⚠ {filename:<35} {dim}(truncated!){reset} {color}│{reset}")
            elif artifact[0] == 'error':
                _, msg = artifact
                print(f"    {color}│{reset}  ✗ {msg[:45]}")

        # Git sync and show status
        if files_for_git:
            print(f"    {color}├{'─' * 50}┤{reset}")
            synced = git_sync_artifacts(files_for_git, genre)
            if synced:
                print(f"    {color}│{reset}  ↑ {dim}Synced to GitHub{reset}{' ' * 31}{color}│{reset}")
            else:
                print(f"    {color}│{reset}  ○ {dim}Local only{reset}{' ' * 37}{color}│{reset}")

        print(f"    {color}└{'─' * 50}┘{reset}")
        print()

    return text.strip()


def run_story(genre: str, mode: str, goal: str = None):
    """Run the interactive story."""
    import threading

    if not HAS_LLM:
        print("\n    Cannot run story without LLM access.\n")
        return

    # Start a new story session
    session_id = start_story_session(genre)
    story_path = get_story_path()

    print(f"\n    Story: {session_id}")
    print(f"    Artifacts: github.com/Palmerschallon/The_Codex/stories/{session_id}")

    # Build the system prompt with story path
    goal_line = f"GOAL: {goal}" if goal else "GOAL: Let the story reveal what needs to be built"
    system = SYSTEM_PROMPT.format(
        genre=genre,
        mode=mode,
        goal_line=goal_line,
        story_path=story_path
    )

    # Add universe context if registry is available
    if HAS_REGISTRY:
        try:
            query = RegistryQuery(Path(CODEX_REPO_PATH) / "registry")
            universe_context = query.build_prompt_context(genre=genre, max_items=5)
            if universe_context:
                system = system + "\n\n" + universe_context
        except Exception:
            pass  # Registry context is optional

    # Conversation history (we'll build full prompt each time)
    history = []

    # Get the opening
    print("\n" + "="*60)
    print()

    # Initial message to start the story
    start_msg = "Begin the story. Set the scene in this genre. Introduce the world and characters. Create the starting location."
    if goal:
        start_msg += f" The ultimate goal is to build: {goal}"

    try:
        # Start thinking indicator with genre atmosphere
        stop_thinking = threading.Event()
        thinking_thread = threading.Thread(target=thinking_indicator, args=(stop_thinking, genre))
        thinking_thread.start()

        full_prompt = f"{system}\n\nUser: {start_msg}"
        story_text = ask_anthropic_api(full_prompt, model="claude-sonnet-4-20250514", timeout=120)

        # Stop thinking indicator
        stop_thinking.set()
        thinking_thread.join()

        if story_text:
            story_text = process_response(story_text, genre)
            stream_text(story_text)
            history.append(("user", start_msg))
            history.append(("assistant", story_text))
            # Save to story transcript
            append_to_story(story_text, "narrator")
            # Auto-save opening to GitHub
            sync_story_files()
        else:
            print("\n    Error: No response from Claude. Check ANTHROPIC_API_KEY.")
            return
    except Exception as e:
        stop_thinking.set()
        print(f"\n    Error starting story: {e}")
        import traceback
        traceback.print_exc()
        return

    # Main interaction loop
    print("\n" + "-"*60)
    print("    Type anything to interact. 'quit' to end.")
    print("-"*60)

    while True:
        try:
            print()
            action = input("> ").strip()

            if not action:
                continue

            if action.lower() in ['quit', 'exit', 'q']:
                print("\n    *The book closes. The code remains.*\n")
                break

            if action.lower() == 'help':
                print("""
    THE CODEX - You can type anything.

    The story responds to your actions:
      - Explore: "look around", "go deeper", "examine the terminal"
      - Interact: "talk to [character]", "ask about [thing]"
      - Create: "write code to solve this", "build a tool"
      - Act: "hack the system", "search for clues"

    Just describe what you want to do. The story adapts.
""")
                continue

            # Build prompt with history
            history.append(("user", action))
            # Save player action to transcript
            append_to_story(action, "player")

            # Build conversation for Claude
            conv_parts = [system, ""]
            for role, msg in history[-10:]:  # Keep last 10 exchanges
                if role == "user":
                    conv_parts.append(f"User: {msg}")
                else:
                    conv_parts.append(f"Assistant: {msg}")

            full_prompt = "\n\n".join(conv_parts)

            try:
                # Start thinking indicator with genre atmosphere
                stop_thinking = threading.Event()
                thinking_thread = threading.Thread(target=thinking_indicator, args=(stop_thinking, genre))
                thinking_thread.start()

                story_text = ask_anthropic_api(full_prompt, model="claude-sonnet-4-20250514", timeout=120)

                # Stop thinking indicator
                stop_thinking.set()
                thinking_thread.join()

                if story_text:
                    story_text = process_response(story_text, genre)
                    print()
                    stream_text(story_text)
                    history.append(("assistant", story_text))
                    # Save to transcript
                    append_to_story(story_text, "narrator")
                    # Auto-save checkpoint to GitHub
                    sync_story_files()
                else:
                    print("\n    *The story waits...*")
                    history.pop()  # Remove failed user message
            except Exception as e:
                stop_thinking.set()
                print(f"\n    *The story flickers... ({e})*")
                history.pop()  # Remove failed user message

        except (KeyboardInterrupt, EOFError):
            print("\n\n    *The story pauses...*\n")
            # Final sync of story files
            sync_story_files()
            break


def main():
    """Main entry point."""
    # Quick start options
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print("""
THE CODEX - A text-based novel where code is the story.

Usage:
    python the_codex.py              # Interactive start
    python the_codex.py --quick      # Skip intro, random genre
""")
            return

        if sys.argv[1] == '--quick':
            import random
            genre = random.choice(['mystery', 'scifi horror', 'cyberpunk noir', 'western mystery'])
            print(f"\n    Quick start: {genre}\n")
            run_story(genre, 'story')
            return

    # Full experience
    opening()
    mode = get_mode()

    if mode is None:
        print("\n    *The book remains closed. For now.*\n")
        return

    genre = get_genre()

    try:
        if mode == 'build':
            goal = get_goal()
            print("\n    *The pages begin to turn...*")
            time.sleep(0.5)
            run_story(genre, mode, goal)
        else:
            print(f"\n    [Starting STORY mode with genre: {genre}]")
            print("\n    *The pages begin to turn...*")
            time.sleep(0.5)
            run_story(genre, mode)
    except Exception as e:
        print(f"\n    ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    import sys

    # Log everything to file
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, text):
            for f in self.files:
                f.write(text)
                f.flush()
        def flush(self):
            for f in self.files:
                f.flush()

    log_file = open('/ember/codex_log.txt', 'w')
    sys.stdout = Tee(sys.stdout, log_file)
    sys.stderr = Tee(sys.stderr, log_file)

    try:
        main()
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        log_file.close()
        print("\n\n[Press Enter to exit]")
        try:
            input()
        except:
            pass
