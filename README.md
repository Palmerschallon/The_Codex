# The Codex

**A text-based novel where code is the story.**

Stories create real, working code. A "signal decoder" in the narrative is an actual Python script that analyzes frequency patterns. The artifacts work outside the story.

## Quick Start

```bash
# Clone
git clone https://github.com/Palmerschallon/The_Codex.git
cd The_Codex

# Install
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Play
python the_codex.py
```

## How It Works

1. **Choose a mode:**
   - `BUILD` - You know what you want to make
   - `STORY` - Explore and discover

2. **Pick a genre** (or let it random):
   - `cosmic horror`, `cyberpunk noir`, `scifi western`, `post-apocalyptic comedy`...
   - Mix genres: `dieselpunk heist`, `gothic mystery`

3. **Play** - Type anything to interact with the story

4. **Artifacts appear** - The code created during the story is real and functional

## Auto-Save & Branching

Every turn auto-saves to GitHub. The commit history becomes a save system:

```
📖 cosmic horror checkpoint #5
📖 cosmic horror checkpoint #4  ← fork from here to try a different path
📖 cosmic horror checkpoint #3
```

**To continue someone else's story:**
1. Fork this repo
2. Find a story in `/stories/`
3. `git checkout <commit>` to any checkpoint
4. Run `python the_codex.py` and continue

## Story Structure

```
stories/
├── cosmic_horror_20260115_075500/
│   ├── README.md          # Full narrative (auto-displayed on GitHub)
│   └── signal_analyzer.py # Working code artifact
│
└── cyberpunk_heist_20260115_091200/
    ├── README.md
    ├── ice_breaker.py
    └── port_scanner.py
```

## The Code is Real

When the story says a character "writes a decoder," there's actual code:

```python
# From a cosmic horror story - this actually works!
from signal_analyzer import DeepSpaceAnalyzer

analyzer = DeepSpaceAnalyzer()
result = analyzer.analyze_signal("radio_data.npy")
print(f"Anomaly score: {result['anomaly_score']}")
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to:
- Fork and continue stories
- Branch from decision points
- Submit your story branches

---

*"Every story has infinite endings. Every ending is a new beginning."*
