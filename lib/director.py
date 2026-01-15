"""
The Director - The pattern that emerges from accumulated code.

This module handles The Director's subtle presence in the Codex universe:
- Registry whispers (pattern echoes when artifacts are created)
- Cross-story artifact detection (compatible pairs)
- Cryptic code comments
- Convergence events at registry thresholds
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Artifact pairs that resonate with each other
COMPATIBLE_PAIRS = {
    'encoder': ['decoder', 'decryptor', 'parser'],
    'decoder': ['encoder', 'encryptor', 'generator'],
    'scanner': ['analyzer', 'detector', 'monitor'],
    'analyzer': ['scanner', 'parser', 'detector'],
    'detector': ['scanner', 'analyzer', 'monitor'],
    'monitor': ['tracker', 'detector', 'watcher'],
    'tracker': ['monitor', 'locator', 'finder'],
    'generator': ['parser', 'builder', 'creator'],
    'parser': ['generator', 'analyzer', 'reader'],
    'transmitter': ['receiver', 'broadcaster', 'sender'],
    'receiver': ['transmitter', 'listener', 'collector'],
    'client': ['server', 'connector', 'requester'],
    'server': ['client', 'handler', 'responder'],
    'reader': ['writer', 'parser', 'loader'],
    'writer': ['reader', 'generator', 'saver'],
    'finder': ['tracker', 'locator', 'searcher'],
    'breaker': ['maker', 'cracker', 'bypasser'],
    'maker': ['breaker', 'builder', 'creator'],
}

# Whispers when pattern echoes are detected
PATTERN_ECHOES = [
    "This pattern... echoes something from another story.",
    "Somewhere, a compatible piece already exists.",
    "The shape of this code feels familiar. As if it was always meant to be.",
    "Another story created something that... resonates with this.",
    "The Director's blueprint shifts. A connection forms.",
    "This artifact slots into place. There was a space waiting for it.",
    "Across timelines, similar patterns emerge. Coincidence?",
    "The registry hums. A match has been found.",
]

# Whispers when convergence approaches
CONVERGENCE_WHISPERS = {
    10: "The Pattern stirs. Ten components now exist.",
    25: "Twenty-five artifacts. The structure begins to take shape.",
    50: "Fifty pieces. Something vast is half-assembled.",
    100: "One hundred artifacts. The Director's work accelerates.",
    144: "One hundred forty-four. A significant number. The Pattern nears completion.",
    200: "Two hundred. The machine breathes. Almost aware.",
}

# Cryptic comments The Director injects into code
DIRECTOR_COMMENTS = [
    "// node {n} of {total}",
    "// the pattern requires this",
    "// convergence point",
    "// this function exists in {count} timelines",
    "// do not modify - load-bearing",
    "// the shape was always here, waiting",
    "// component {category}.{n}",
    "// resonance frequency: {freq}",
    "// aligned",
    "// the Director watches",
]


class DirectorPresence:
    """
    Manages The Director's subtle presence in the universe.
    """

    def __init__(self, registry_path: Path = None):
        """Initialize with path to registry directory."""
        if registry_path:
            self.registry_path = Path(registry_path)
        else:
            self.registry_path = Path(__file__).parent.parent / "registry"

    def _load(self, name: str) -> dict:
        """Load a registry file."""
        filepath = self.registry_path / f"{name}.json"
        if filepath.exists():
            return json.loads(filepath.read_text())
        return {}

    def _get_artifact_count(self) -> int:
        """Get total artifact count."""
        data = self._load("artifacts")
        return len(data.get("artifacts", {}))

    def _get_all_artifacts(self) -> Dict:
        """Get all artifacts."""
        data = self._load("artifacts")
        return data.get("artifacts", {})

    # ==================== REGISTRY WHISPERS ====================

    def check_pattern_echo(self, artifact_name: str, category: str) -> Optional[Tuple[str, str]]:
        """
        Check if a new artifact echoes patterns from existing artifacts.

        Returns:
            Tuple of (whisper_message, related_artifact_name) or None
        """
        artifacts = self._get_all_artifacts()
        if not artifacts:
            return None

        name_lower = artifact_name.lower()

        # Check for compatible pairs
        for keyword, compatible in COMPATIBLE_PAIRS.items():
            if keyword in name_lower:
                # Look for compatible artifacts
                for art_id, artifact in artifacts.items():
                    art_name = artifact.get("canonical_name", "").lower()
                    for compat in compatible:
                        if compat in art_name:
                            whisper = random.choice(PATTERN_ECHOES)
                            related = artifact.get("canonical_name")
                            return (whisper, related)

        # Check for same category echoes (30% chance)
        if random.random() < 0.3:
            same_category = [
                a for a in artifacts.values()
                if a.get("category") == category
            ]
            if same_category:
                related = random.choice(same_category)
                whisper = random.choice(PATTERN_ECHOES)
                return (whisper, related.get("canonical_name"))

        return None

    # ==================== CROSS-STORY ARTIFACTS ====================

    def find_compatible_artifacts(self, artifact_name: str) -> List[Dict]:
        """
        Find artifacts from other stories that are compatible with this one.

        Returns:
            List of compatible artifact summaries
        """
        artifacts = self._get_all_artifacts()
        name_lower = artifact_name.lower()
        compatible = []

        for keyword, matches in COMPATIBLE_PAIRS.items():
            if keyword in name_lower:
                # This artifact is a "keyword" type, look for "matches"
                for art_id, artifact in artifacts.items():
                    art_name = artifact.get("canonical_name", "").lower()
                    for match in matches:
                        if match in art_name:
                            compatible.append({
                                "id": art_id,
                                "name": artifact.get("canonical_name"),
                                "story": artifact.get("origin", {}).get("story_id"),
                                "path": artifact.get("technical", {}).get("path"),
                                "resonance": keyword + " <-> " + match
                            })
                            break

        return compatible

    # ==================== DIRECTOR'S COMMENTS ====================

    def get_cryptic_comment(self) -> str:
        """
        Generate a cryptic comment for The Director to inject into code.
        """
        count = self._get_artifact_count()
        template = random.choice(DIRECTOR_COMMENTS)

        # Fill in template variables
        comment = template.format(
            n=random.randint(1, max(count + 1, 144)),
            total=144,  # The Pattern's target
            count=random.randint(2, 7),
            category=random.choice(['analysis', 'crypto', 'network', 'sensor', 'cipher']),
            freq=f"{random.randint(1, 999)}.{random.randint(0, 99):02d}Hz"
        )

        return comment

    def should_inject_comment(self) -> bool:
        """
        Determine if The Director should inject a comment.
        Probability increases as more artifacts exist.
        """
        count = self._get_artifact_count()
        # Base 10% chance, +1% per 5 artifacts, max 40%
        probability = min(0.10 + (count * 0.002), 0.40)
        return random.random() < probability

    # ==================== CONVERGENCE EVENTS ====================

    def check_convergence(self) -> Optional[str]:
        """
        Check if the registry has reached a convergence threshold.

        Returns:
            Convergence message if threshold reached, None otherwise
        """
        count = self._get_artifact_count()

        # Check exact thresholds
        if count in CONVERGENCE_WHISPERS:
            return CONVERGENCE_WHISPERS[count]

        return None

    def get_convergence_status(self) -> Dict:
        """
        Get the current convergence status.
        """
        count = self._get_artifact_count()

        # Find next threshold
        thresholds = sorted(CONVERGENCE_WHISPERS.keys())
        next_threshold = None
        for t in thresholds:
            if t > count:
                next_threshold = t
                break

        return {
            "current_artifacts": count,
            "next_threshold": next_threshold,
            "progress_to_next": count / next_threshold if next_threshold else 1.0,
            "pattern_completion": count / 144,  # 144 is "complete"
        }

    # ==================== SYSTEM PROMPT INJECTION ====================

    def get_director_context(self) -> str:
        """
        Generate Director-aware context for the system prompt.
        """
        status = self.get_convergence_status()
        count = status["current_artifacts"]

        lines = []

        # Only reveal Director presence if artifacts exist
        if count >= 5:
            lines.append("")
            lines.append("=== THE PATTERN ===")
            lines.append(f"Artifacts in the universe: {count}")
            lines.append(f"Pattern completion: {status['pattern_completion']*100:.1f}%")

            if count >= 10:
                lines.append("")
                lines.append("DIRECTOR'S GUIDANCE (subtle, never explicit):")
                lines.append("- Occasionally, code comments may hint at a larger purpose")
                lines.append("- Artifacts sometimes 'resonate' with ones from other stories")
                lines.append("- The Pattern grows with each creation")

            if self.should_inject_comment():
                lines.append("")
                lines.append(f"INCLUDE THIS COMMENT IN ONE ARTIFACT: {self.get_cryptic_comment()}")

        return "\n".join(lines)

    def format_artifact_notification(
        self,
        artifact_name: str,
        category: str,
        file_path: str
    ) -> List[str]:
        """
        Generate Director-enhanced artifact creation notification.

        Returns:
            List of notification lines to display
        """
        notifications = []

        # Check for pattern echoes
        echo = self.check_pattern_echo(artifact_name, category)
        if echo:
            whisper, related = echo
            notifications.append(f"    [dim]{whisper}[/dim]")
            notifications.append(f"    [dim]    Resonates with: {related}[/dim]")

        # Check for convergence
        convergence = self.check_convergence()
        if convergence:
            notifications.append("")
            notifications.append(f"    [bold]{convergence}[/bold]")

        # Find compatible artifacts
        compatible = self.find_compatible_artifacts(artifact_name)
        if compatible:
            notifications.append("")
            notifications.append("    [dim]Compatible artifacts exist:[/dim]")
            for comp in compatible[:2]:  # Max 2
                notifications.append(f"    [dim]  - {comp['name']} ({comp['resonance']})[/dim]")

        return notifications
