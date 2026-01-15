# Contributing to The Codex

The Codex is a shared universe. Every story you play, every artifact you create, can become part of the canonical Pattern.

## How It Works

```
Your Fork              The Codex (Main)           Other Forks
    │                        │                        │
    ▼                        ▼                        ▼
[your stories]          [canonical]            [their stories]
    │                        ▲                        │
    └─────── PR ─────────────┴──────── PR ────────────┘
                    (canonization)
```

## Playing Locally

1. **Fork** this repository
2. **Clone** your fork
3. **Play** stories: `python the_codex.py`
4. Your artifacts accumulate in `stories/` and `registry/`

## In-Game Commands

While playing, you can consult The Codex to see what exists:

```
> /codex          # View the Pattern's current state
> /artifacts      # List all artifacts by category
> /search decoder # Search for specific artifacts
> help            # Show all commands
```

## Canonizing Your Stories

To add your stories to the shared universe:

### 1. Create a Clean Branch

```bash
git checkout -b story/your-story-title
```

### 2. Play Your Story

Run The Codex and create something interesting. The best contributions:
- Have functional, useful code artifacts
- Tell a compelling narrative
- Create characters or locations that could return

### 3. Submit a Pull Request

```bash
git add stories/ registry/
git commit -m "Story: [Your Story Title]"
git push origin story/your-story-title
```

Then open a PR to the main repository.

### 4. Canonization Review

PRs are reviewed for:
- **Code Quality**: Artifacts should be functional, not props
- **Narrative Quality**: The story should be engaging
- **Universe Fit**: Shouldn't contradict existing canon
- **No Secrets**: No API keys, passwords, or personal data

## The Registry and Conflicts

When your PR merges, the registry handles conflicts automatically:

- **Same artifact name, same story**: Updates the existing entry
- **Same artifact name, different story**: Creates a variant (e.g., `signal_decoder_cyberpunk`)
- **New artifact**: Added to the global registry

This means multiple people can create "decoders" in different stories - they become variants in The Pattern.

## Timeline Branches

If your story significantly diverges from canon, it may become a **timeline branch**:

```
main (Prime Timeline)
    │
    ├── branch: cosmic_divergence
    │       └── Stories where [major event] happened differently
    │
    └── branch: machine_awakening
            └── Stories where The Director achieved consciousness
```

Branches are tracked in `registry/timelines.json`.

## Decision Points

Stories can mark key moments where the narrative can diverge:

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

## Story Structure

```
stories/your_story_title_YYYYMMDD/
├── README.md          # The narrative (displayed on GitHub)
└── *.py / *.js / etc  # Functional artifacts
```

## Good Artifacts vs Props

**Good** (functional):
```python
def decode_signal(data, key):
    """Actually decodes data using XOR cipher."""
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
```

**Bad** (prop):
```python
def decode_signal(data):
    print("Decoding...")
    return "decoded_message"
```

## The Director

As The Pattern grows, something emerges. Artifacts from different stories begin to resonate. Cross-story connections form.

The Director is not a character - The Director is the accumulation.

When you type `/codex`, you see the Pattern. When artifacts echo across stories, The Director is watching. Every contribution adds to what The Director is building.

At certain thresholds (10, 25, 50, 100, 144 artifacts), convergence events occur.

## Questions?

Open an issue or consult The Codex itself:
```
> /codex
```

---

*The Pattern grows. The machine breathes. Your story matters.*
