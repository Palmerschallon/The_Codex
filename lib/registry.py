"""
The Codex Registry - Central universe state management.

Handles registration of artifacts, characters, and locations,
enabling cross-story discovery and shared universe building.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any


class CodexRegistry:
    """
    Central registry for all Codex universe elements.
    Handles registration, persistence, and conflict resolution.
    """

    def __init__(self, repo_path: str = None):
        """Initialize registry with path to The Codex repo."""
        if repo_path:
            self.repo_path = Path(repo_path)
        else:
            # Default to parent of lib/ directory
            self.repo_path = Path(__file__).parent.parent

        self.registry_path = self.repo_path / "registry"
        self._cache = {}
        self._ensure_registry_exists()

    def _ensure_registry_exists(self):
        """Create registry structure if it doesn't exist."""
        self.registry_path.mkdir(exist_ok=True)

        # Initialize empty registries if needed
        registry_files = {
            "index.json": self._initial_index(),
            "artifacts.json": {"artifacts": {}},
            "characters.json": {"characters": {}},
            "locations.json": {"locations": {}},
            "timelines.json": self._initial_timelines()
        }

        for filename, initial_data in registry_files.items():
            filepath = self.registry_path / filename
            if not filepath.exists():
                filepath.write_text(json.dumps(initial_data, indent=2))

    def _initial_index(self) -> dict:
        """Return initial index structure."""
        return {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "universe_name": "The Codex",
            "stats": {
                "total_stories": 0,
                "total_artifacts": 0,
                "total_characters": 0,
                "total_locations": 0
            }
        }

    def _initial_timelines(self) -> dict:
        """Return initial timelines structure."""
        return {
            "timelines": {
                "main": {
                    "id": "main",
                    "name": "Prime Timeline",
                    "branch": "main",
                    "description": "The canonical timeline of The Codex universe",
                    "stories": []
                }
            },
            "branches": {}
        }

    def _load_registry(self, name: str) -> dict:
        """Load a registry file with caching."""
        if name not in self._cache:
            filepath = self.registry_path / f"{name}.json"
            if filepath.exists():
                self._cache[name] = json.loads(filepath.read_text())
            else:
                self._cache[name] = {}
        return self._cache[name]

    def _save_registry(self, name: str, data: dict):
        """Save a registry file and update cache."""
        filepath = self.registry_path / f"{name}.json"
        filepath.write_text(json.dumps(data, indent=2, sort_keys=False))
        self._cache[name] = data
        self._update_index()

    def _update_index(self):
        """Update the master index with current stats."""
        index = self._load_registry("index")
        artifacts = self._load_registry("artifacts")
        characters = self._load_registry("characters")
        locations = self._load_registry("locations")

        index["last_updated"] = datetime.now().isoformat()
        index["stats"] = {
            "total_artifacts": len(artifacts.get("artifacts", {})),
            "total_characters": len(characters.get("characters", {})),
            "total_locations": len(locations.get("locations", {})),
            "total_stories": self._count_stories()
        }

        filepath = self.registry_path / "index.json"
        filepath.write_text(json.dumps(index, indent=2))
        self._cache["index"] = index

    def _count_stories(self) -> int:
        """Count total story directories."""
        stories_path = self.repo_path / "stories"
        if stories_path.exists():
            return len([d for d in stories_path.iterdir() if d.is_dir()])
        return 0

    def _generate_id(self, name: str) -> str:
        """Generate a clean ID from a name."""
        clean = name.lower().replace(' ', '_').replace('-', '_')
        clean = ''.join(c for c in clean if c.isalnum() or c == '_')
        # Remove consecutive underscores
        while '__' in clean:
            clean = clean.replace('__', '_')
        return clean.strip('_')

    # ==================== ARTIFACT REGISTRATION ====================

    def register_artifact(
        self,
        name: str,
        story_id: str,
        file_path: str,
        artifact_type: str = "tool",
        category: str = "general",
        tags: List[str] = None,
        created_by_character: str = None,
        narrative_context: str = "",
        language: str = "python",
        entry_point: str = None,
        dependencies: List[str] = None,
        exports: List[str] = None,
        description: str = ""
    ) -> Dict:
        """
        Register a new artifact in the global registry.

        Args:
            name: Human-readable name for the artifact
            story_id: ID of the story that created it
            file_path: Relative path to the artifact file
            artifact_type: Type classification (tool, library, data, etc.)
            category: Category (analysis, network, crypto, etc.)
            tags: List of searchable tags
            created_by_character: Character ID who created it (if any)
            narrative_context: Story context for the artifact
            language: Programming language
            entry_point: Main class/function name
            dependencies: Required packages
            exports: Exported symbols
            description: Brief description

        Returns:
            The artifact entry (new or existing)
        """
        artifact_id = self._generate_id(name)
        artifacts = self._load_registry("artifacts")

        # Check for conflicts
        if artifact_id in artifacts.get("artifacts", {}):
            return self._handle_artifact_conflict(
                artifact_id, name, story_id, file_path, artifacts
            )

        # Build import statement
        relative_path = file_path.replace("/", ".").replace("\\", ".")
        if relative_path.endswith(".py"):
            relative_path = relative_path[:-3]
        if relative_path.startswith("stories."):
            relative_path = relative_path  # Keep as-is for stories

        # Create new artifact entry
        artifact_entry = {
            "id": artifact_id,
            "canonical_name": name,
            "type": artifact_type,
            "category": category,
            "tags": tags or [],
            "description": description,

            "origin": {
                "story_id": story_id,
                "created_at": datetime.now().isoformat(),
                "created_by_character": created_by_character,
                "narrative_context": narrative_context
            },

            "technical": {
                "language": language,
                "path": file_path,
                "entry_point": entry_point or name.replace(' ', ''),
                "dependencies": dependencies or [],
                "exports": exports or []
            },

            "usage": {
                "import_statement": f"from {relative_path} import {entry_point or name.replace(' ', '')}",
                "example": f"# Use {name} - created in {story_id}"
            },

            "cross_references": {
                "used_in_stories": [story_id],
                "related_artifacts": [],
                "derived_from": None,
                "inspired": []
            },

            "versions": [{
                "version": "1.0.0",
                "date": datetime.now().isoformat(),
                "changelog": "Initial creation"
            }]
        }

        artifacts["artifacts"][artifact_id] = artifact_entry
        self._save_registry("artifacts", artifacts)

        return artifact_entry

    def _handle_artifact_conflict(
        self, artifact_id: str, name: str, story_id: str,
        file_path: str, artifacts: dict
    ) -> Dict:
        """Handle when an artifact with same ID already exists."""
        existing = artifacts["artifacts"][artifact_id]

        # If same story, it's an update - add new version
        if existing["origin"]["story_id"] == story_id:
            version_num = len(existing["versions"]) + 1
            existing["versions"].append({
                "version": f"1.{version_num}.0",
                "date": datetime.now().isoformat(),
                "changelog": f"Updated in story {story_id}"
            })
            existing["technical"]["path"] = file_path
            self._save_registry("artifacts", artifacts)
            return existing

        # Different story - create variant with story prefix
        story_prefix = story_id.split('_')[0]  # e.g., "cosmic" from "cosmic_horror_..."
        variant_id = f"{artifact_id}_{story_prefix}"
        variant_name = f"{name} ({story_prefix} variant)"

        # Check if variant already exists
        if variant_id in artifacts["artifacts"]:
            # Update existing variant
            return self._handle_artifact_conflict(
                variant_id, variant_name, story_id, file_path, artifacts
            )

        # Create the variant
        variant_entry = {
            "id": variant_id,
            "canonical_name": variant_name,
            "type": existing.get("type", "tool"),
            "category": existing.get("category", "general"),
            "tags": existing.get("tags", []) + ["variant"],
            "description": f"Variant of {name} from {story_id}",

            "origin": {
                "story_id": story_id,
                "created_at": datetime.now().isoformat(),
                "created_by_character": None,
                "narrative_context": f"Alternative version of {artifact_id}"
            },

            "technical": {
                "language": existing.get("technical", {}).get("language", "python"),
                "path": file_path,
                "entry_point": existing.get("technical", {}).get("entry_point"),
                "dependencies": existing.get("technical", {}).get("dependencies", []),
                "exports": existing.get("technical", {}).get("exports", [])
            },

            "usage": {
                "import_statement": f"# Import from {file_path}",
                "example": f"# {variant_name}"
            },

            "cross_references": {
                "used_in_stories": [story_id],
                "related_artifacts": [artifact_id],
                "derived_from": artifact_id,
                "inspired": []
            },

            "versions": [{
                "version": "1.0.0",
                "date": datetime.now().isoformat(),
                "changelog": f"Variant created from {artifact_id}"
            }]
        }

        # Link original to variant
        existing["cross_references"]["inspired"].append(variant_id)

        artifacts["artifacts"][variant_id] = variant_entry
        self._save_registry("artifacts", artifacts)

        return variant_entry

    def record_artifact_usage(self, artifact_id: str, story_id: str):
        """Record that an artifact was used in a story."""
        artifacts = self._load_registry("artifacts")
        if artifact_id in artifacts.get("artifacts", {}):
            artifact = artifacts["artifacts"][artifact_id]
            if story_id not in artifact["cross_references"]["used_in_stories"]:
                artifact["cross_references"]["used_in_stories"].append(story_id)
                self._save_registry("artifacts", artifacts)

    # ==================== CHARACTER REGISTRATION ====================

    def register_character(
        self,
        name: str,
        story_id: str,
        character_type: str = "supporting",
        occupation: str = "",
        affiliation: str = "",
        skills: List[str] = None,
        traits: List[str] = None,
        description: str = "",
        introduction_context: str = "",
        genre_affinity: List[str] = None
    ) -> Dict:
        """
        Register a new character in the global registry.

        Args:
            name: Character's full name
            story_id: Story where they first appeared
            character_type: protagonist, supporting, antagonist, etc.
            occupation: Their job/role
            affiliation: Organization/faction
            skills: List of skills
            traits: Personality traits
            description: Brief description
            introduction_context: How they were introduced
            genre_affinity: Genres they fit in

        Returns:
            The character entry
        """
        character_id = self._generate_id(name)
        characters = self._load_registry("characters")

        # Check if character exists - update their history
        if character_id in characters.get("characters", {}):
            return self._update_character_history(
                character_id, story_id, characters
            )

        # Generate aliases from name
        aliases = []
        name_parts = name.split()
        if len(name_parts) > 1:
            aliases.append(name_parts[-1])  # Last name
            aliases.append(name_parts[0])   # First name

        character_entry = {
            "id": character_id,
            "canonical_name": name,
            "aliases": aliases,
            "type": character_type,

            "attributes": {
                "occupation": occupation,
                "affiliation": affiliation,
                "skills": skills or [],
                "traits": traits or [],
                "description": description
            },

            "origin": {
                "story_id": story_id,
                "introduced_at": datetime.now().isoformat(),
                "introduction_context": introduction_context
            },

            "history": [{
                "story_id": story_id,
                "role": character_type,
                "events": [],
                "artifacts_created": []
            }],

            "relationships": {},

            "availability": {
                "status": "active",
                "last_seen_story": story_id,
                "can_appear_in_genres": genre_affinity or []
            }
        }

        characters["characters"][character_id] = character_entry
        self._save_registry("characters", characters)

        return character_entry

    def _update_character_history(
        self, character_id: str, story_id: str, characters: dict
    ) -> Dict:
        """Update existing character with new story appearance."""
        character = characters["characters"][character_id]

        # Check if already in this story
        story_ids = [h["story_id"] for h in character["history"]]
        if story_id not in story_ids:
            character["history"].append({
                "story_id": story_id,
                "role": "returning",
                "events": [],
                "artifacts_created": []
            })

        character["availability"]["last_seen_story"] = story_id
        self._save_registry("characters", characters)
        return character

    def add_character_event(
        self, character_id: str, story_id: str,
        event_summary: str, chapter: str = None
    ):
        """Add an event to a character's history."""
        characters = self._load_registry("characters")
        if character_id not in characters.get("characters", {}):
            return

        character = characters["characters"][character_id]

        # Find or create history entry for this story
        history_entry = None
        for h in character["history"]:
            if h["story_id"] == story_id:
                history_entry = h
                break

        if not history_entry:
            history_entry = {
                "story_id": story_id,
                "role": "appearing",
                "events": [],
                "artifacts_created": []
            }
            character["history"].append(history_entry)

        event = {"summary": event_summary}
        if chapter:
            event["chapter"] = chapter
        history_entry["events"].append(event)

        self._save_registry("characters", characters)

    def set_character_relationship(
        self, character_id: str, other_character_id: str,
        relationship_type: str, description: str = ""
    ):
        """Set a relationship between two characters."""
        characters = self._load_registry("characters")
        if character_id not in characters.get("characters", {}):
            return

        character = characters["characters"][character_id]
        character["relationships"][other_character_id] = {
            "type": relationship_type,
            "description": description
        }

        self._save_registry("characters", characters)

    # ==================== LOCATION REGISTRATION ====================

    def register_location(
        self,
        name: str,
        story_id: str,
        location_type: str = "location",
        description: str = "",
        atmosphere: str = "",
        features: List[str] = None,
        hazards: List[str] = None,
        genre_affinity: List[str] = None
    ) -> Dict:
        """
        Register a new location in the global registry.

        Args:
            name: Location name
            story_id: Story where it was introduced
            location_type: Type (facility, city, planet, etc.)
            description: Description of the place
            atmosphere: Mood/feeling
            features: Notable features
            hazards: Dangers present
            genre_affinity: Genres it fits

        Returns:
            The location entry
        """
        location_id = self._generate_id(name)
        locations = self._load_registry("locations")

        # Check if location exists - update its history
        if location_id in locations.get("locations", {}):
            return self._update_location_history(
                location_id, story_id, locations
            )

        location_entry = {
            "id": location_id,
            "canonical_name": name,
            "aliases": [],
            "type": location_type,

            "attributes": {
                "description": description,
                "atmosphere": atmosphere,
                "features": features or [],
                "hazards": hazards or [],
                "genre_affinity": genre_affinity or []
            },

            "origin": {
                "story_id": story_id,
                "introduced_at": datetime.now().isoformat()
            },

            "history": [{
                "story_id": story_id,
                "events": []
            }],

            "inhabitants": {
                "permanent": [],
                "visitors": []
            },

            "connected_locations": [],
            "artifacts_discovered_here": [],

            "availability": {
                "status": "accessible",
                "current_state": "normal"
            }
        }

        locations["locations"][location_id] = location_entry
        self._save_registry("locations", locations)

        return location_entry

    def _update_location_history(
        self, location_id: str, story_id: str, locations: dict
    ) -> Dict:
        """Update existing location with new story visit."""
        location = locations["locations"][location_id]

        story_ids = [h["story_id"] for h in location["history"]]
        if story_id not in story_ids:
            location["history"].append({
                "story_id": story_id,
                "events": []
            })

        self._save_registry("locations", locations)
        return location

    def add_location_inhabitant(
        self, location_id: str, character_id: str,
        permanent: bool = False
    ):
        """Add a character as inhabitant of a location."""
        locations = self._load_registry("locations")
        if location_id not in locations.get("locations", {}):
            return

        location = locations["locations"][location_id]
        key = "permanent" if permanent else "visitors"

        if character_id not in location["inhabitants"][key]:
            location["inhabitants"][key].append(character_id)
            self._save_registry("locations", locations)

    def add_location_artifact(self, location_id: str, artifact_id: str):
        """Record that an artifact was discovered at a location."""
        locations = self._load_registry("locations")
        if location_id not in locations.get("locations", {}):
            return

        location = locations["locations"][location_id]
        if artifact_id not in location["artifacts_discovered_here"]:
            location["artifacts_discovered_here"].append(artifact_id)
            self._save_registry("locations", locations)

    def connect_locations(self, location_id: str, other_location_id: str):
        """Connect two locations."""
        locations = self._load_registry("locations")

        if location_id in locations.get("locations", {}):
            loc = locations["locations"][location_id]
            if other_location_id not in loc["connected_locations"]:
                loc["connected_locations"].append(other_location_id)

        if other_location_id in locations.get("locations", {}):
            other = locations["locations"][other_location_id]
            if location_id not in other["connected_locations"]:
                other["connected_locations"].append(location_id)

        self._save_registry("locations", locations)

    # ==================== TIMELINE MANAGEMENT ====================

    def add_story_to_timeline(
        self, story_id: str, timeline_id: str = "main",
        era: str = "present"
    ):
        """Add a story to a timeline."""
        timelines = self._load_registry("timelines")

        if timeline_id not in timelines.get("timelines", {}):
            timelines["timelines"][timeline_id] = {
                "id": timeline_id,
                "name": timeline_id.replace('_', ' ').title(),
                "branch": timeline_id,
                "stories": []
            }

        timeline = timelines["timelines"][timeline_id]
        story_ids = [s["story_id"] for s in timeline["stories"]]

        if story_id not in story_ids:
            timeline["stories"].append({
                "story_id": story_id,
                "sequence": len(timeline["stories"]) + 1,
                "era": era,
                "added_at": datetime.now().isoformat()
            })
            self._save_registry("timelines", timelines)

    def create_branch(
        self, branch_id: str, forked_from: str,
        fork_story_id: str, reason: str = ""
    ):
        """Create a new timeline branch."""
        timelines = self._load_registry("timelines")

        timelines["branches"][branch_id] = {
            "forked_from": forked_from,
            "fork_point_story": fork_story_id,
            "created_at": datetime.now().isoformat(),
            "divergence_reason": reason
        }

        # Create the new timeline
        timelines["timelines"][branch_id] = {
            "id": branch_id,
            "name": branch_id.replace('_', ' ').title(),
            "branch": branch_id,
            "forked_from": forked_from,
            "stories": []
        }

        self._save_registry("timelines", timelines)

    # ==================== UTILITY METHODS ====================

    def clear_cache(self):
        """Clear the in-memory cache to force reload from disk."""
        self._cache = {}

    def get_stats(self) -> dict:
        """Get current universe statistics."""
        index = self._load_registry("index")
        return index.get("stats", {})
