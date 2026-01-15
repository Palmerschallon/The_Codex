# Contributing to The Codex

## How Branching Works

Every story in The Codex is a living narrative that can branch into infinite possibilities.

### Continuing a Story

1. **Fork this repository**
2. **Find a story** in `/stories/` that interests you
3. **Read the story.md** to find decision points marked with `<!-- DECISION POINT -->`
4. **Create a branch** from that point:
   ```bash
   git checkout -b my-branch-cosmic-horror
   ```
5. **Run THE CODEX** and continue the narrative
6. **Push your branch** - your continuation lives alongside the original

### Decision Points

Stories mark key moments where the narrative can diverge:

```markdown
<!-- DECISION POINT: What does Elena do next? -->
<!-- Options:
  A) Build a decoder to understand the signal
  B) Shut down all equipment and evacuate
  C) Try to communicate back
-->
```

Each decision point is also a git commit. You can:
- `git log` to see the story's history
- `git checkout <commit>` to return to any moment
- `git branch my-path` to start your own timeline

### Story Structure

```
stories/
├── cosmic_horror_20260115_075500/
│   ├── README.md          # Story metadata
│   ├── story.md           # Full narrative with decision points
│   ├── signal_analyzer.py # Artifacts (working code!)
│   └── decoder.py         # More artifacts...
│
├── cosmic_horror_20260115_075500-elenas_escape/  # A branch!
│   ├── story.md           # Divergent narrative
│   └── evacuation_protocol.py
│
└── cosmic_horror_20260115_075500-dark_communion/  # Another branch!
    ├── story.md           # Different path
    └── signal_transmitter.py
```

### The Code is Real

Every artifact in a story is **functional code**. When the story says Elena writes a "signal decoder," there's an actual Python file that analyzes frequency patterns. You can:

- Run the code outside the story
- Import it into your projects
- Improve it in your branch

### Pull Requests

Want to merge your branch into the main timeline? Create a PR! The community can vote on which branches become "canon" or remain as alternate timelines.

---

*"Every story has infinite endings. Every ending is a new beginning."*
