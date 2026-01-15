"""
The Codex Query Interface - Universe discovery system.

Provides query methods for discovering what exists in the shared universe.
Designed to be called by Claude during story generation.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any


class RegistryQuery:
    """
    Query interface for discovering registry contents.
    Optimized for injecting context into Claude's prompts.
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

    # ==================== ARTIFACT QUERIES ====================

    def find_artifacts(
        self,
        category: str = None,
        tags: List[str] = None,
        language: str = None,
        story_id: str = None,
        search_text: str = None,
        artifact_type: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find artifacts matching criteria.

        Args:
            category: Filter by category (analysis, network, crypto, etc.)
            tags: Filter by tags (any match)
            language: Filter by programming language
            story_id: Filter by originating story
            search_text: Full-text search in name/description
            artifact_type: Filter by type (tool, library, data)
            limit: Maximum results

        Returns:
            List of matching artifact summaries
        """
        data = self._load("artifacts")
        results = []

        for artifact_id, artifact in data.get("artifacts", {}).items():
            # Apply filters
            if category and artifact.get("category") != category:
                continue
            if artifact_type and artifact.get("type") != artifact_type:
                continue
            if tags and not any(t in artifact.get("tags", []) for t in tags):
                continue
            if language and artifact.get("technical", {}).get("language") != language:
                continue
            if story_id:
                origin_story = artifact.get("origin", {}).get("story_id")
                used_in = artifact.get("cross_references", {}).get("used_in_stories", [])
                if story_id != origin_story and story_id not in used_in:
                    continue
            if search_text:
                searchable = " ".join([
                    artifact.get("canonical_name", ""),
                    artifact.get("description", ""),
                    artifact.get("origin", {}).get("narrative_context", ""),
                    " ".join(artifact.get("tags", []))
                ])
                if search_text.lower() not in searchable.lower():
                    continue

            # Return summary
            results.append({
                "id": artifact_id,
                "name": artifact.get("canonical_name"),
                "type": artifact.get("type"),
                "category": artifact.get("category"),
                "description": artifact.get("description", "")[:100],
                "tags": artifact.get("tags", [])[:5],
                "origin_story": artifact.get("origin", {}).get("story_id"),
                "path": artifact.get("technical", {}).get("path"),
                "import": artifact.get("usage", {}).get("import_statement"),
                "times_used": len(artifact.get("cross_references", {}).get("used_in_stories", []))
            })

            if len(results) >= limit:
                break

        return results

    def get_artifact(self, artifact_id: str) -> Optional[Dict]:
        """Get full artifact details by ID."""
        data = self._load("artifacts")
        return data.get("artifacts", {}).get(artifact_id)

    def list_artifact_categories(self) -> List[str]:
        """List all artifact categories in use."""
        data = self._load("artifacts")
        categories = set()
        for artifact in data.get("artifacts", {}).values():
            if cat := artifact.get("category"):
                categories.add(cat)
        return sorted(categories)

    def list_artifact_tags(self) -> List[str]:
        """List all artifact tags in use."""
        data = self._load("artifacts")
        tags = set()
        for artifact in data.get("artifacts", {}).values():
            for tag in artifact.get("tags", []):
                tags.add(tag)
        return sorted(tags)

    # ==================== CHARACTER QUERIES ====================

    def find_characters(
        self,
        character_type: str = None,
        occupation: str = None,
        skills: List[str] = None,
        available_for_genre: str = None,
        story_id: str = None,
        search_text: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find characters matching criteria.

        Args:
            character_type: protagonist, supporting, antagonist, etc.
            occupation: Filter by occupation
            skills: Filter by skills (any match)
            available_for_genre: Filter by genre compatibility
            story_id: Filter by story appearance
            search_text: Full-text search
            limit: Maximum results

        Returns:
            List of matching character summaries
        """
        data = self._load("characters")
        results = []

        for char_id, char in data.get("characters", {}).items():
            attrs = char.get("attributes", {})
            avail = char.get("availability", {})

            # Apply filters
            if character_type and char.get("type") != character_type:
                continue
            if occupation and occupation.lower() not in attrs.get("occupation", "").lower():
                continue
            if skills and not any(s.lower() in [sk.lower() for sk in attrs.get("skills", [])] for s in skills):
                continue
            if available_for_genre:
                genres = avail.get("can_appear_in_genres", [])
                if genres and available_for_genre.lower() not in [g.lower() for g in genres]:
                    continue
            if story_id:
                story_ids = [h["story_id"] for h in char.get("history", [])]
                if story_id not in story_ids:
                    continue
            if search_text:
                searchable = " ".join([
                    char.get("canonical_name", ""),
                    attrs.get("description", ""),
                    attrs.get("occupation", ""),
                    " ".join(char.get("aliases", []))
                ])
                if search_text.lower() not in searchable.lower():
                    continue

            results.append({
                "id": char_id,
                "name": char.get("canonical_name"),
                "type": char.get("type"),
                "occupation": attrs.get("occupation"),
                "skills": attrs.get("skills", [])[:5],
                "traits": attrs.get("traits", [])[:3],
                "description": attrs.get("description", "")[:100],
                "last_seen": avail.get("last_seen_story"),
                "stories_appeared": len(char.get("history", []))
            })

            if len(results) >= limit:
                break

        return results

    def get_character(self, character_id: str) -> Optional[Dict]:
        """Get full character details by ID."""
        data = self._load("characters")
        return data.get("characters", {}).get(character_id)

    def get_character_history(self, character_id: str) -> List[Dict]:
        """Get a character's full history across stories."""
        char = self.get_character(character_id)
        if char:
            return char.get("history", [])
        return []

    def get_character_relationships(self, character_id: str) -> Dict:
        """Get a character's relationships."""
        char = self.get_character(character_id)
        if char:
            return char.get("relationships", {})
        return {}

    # ==================== LOCATION QUERIES ====================

    def find_locations(
        self,
        location_type: str = None,
        genre_affinity: str = None,
        has_artifacts: bool = None,
        story_id: str = None,
        search_text: str = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find locations matching criteria.

        Args:
            location_type: facility, city, planet, etc.
            genre_affinity: Filter by genre compatibility
            has_artifacts: Filter by presence of artifacts
            story_id: Filter by story appearance
            search_text: Full-text search
            limit: Maximum results

        Returns:
            List of matching location summaries
        """
        data = self._load("locations")
        results = []

        for loc_id, loc in data.get("locations", {}).items():
            attrs = loc.get("attributes", {})

            # Apply filters
            if location_type and loc.get("type") != location_type:
                continue
            if genre_affinity:
                genres = attrs.get("genre_affinity", [])
                if genres and genre_affinity.lower() not in [g.lower() for g in genres]:
                    continue
            if has_artifacts is not None:
                artifacts = loc.get("artifacts_discovered_here", [])
                if has_artifacts and not artifacts:
                    continue
                if not has_artifacts and artifacts:
                    continue
            if story_id:
                story_ids = [h["story_id"] for h in loc.get("history", [])]
                if story_id not in story_ids:
                    continue
            if search_text:
                searchable = " ".join([
                    loc.get("canonical_name", ""),
                    attrs.get("description", ""),
                    attrs.get("atmosphere", ""),
                    " ".join(loc.get("aliases", []))
                ])
                if search_text.lower() not in searchable.lower():
                    continue

            results.append({
                "id": loc_id,
                "name": loc.get("canonical_name"),
                "type": loc.get("type"),
                "atmosphere": attrs.get("atmosphere"),
                "description": attrs.get("description", "")[:100],
                "artifacts": loc.get("artifacts_discovered_here", []),
                "inhabitants": len(loc.get("inhabitants", {}).get("permanent", [])),
                "visits": len(loc.get("history", []))
            })

            if len(results) >= limit:
                break

        return results

    def get_location(self, location_id: str) -> Optional[Dict]:
        """Get full location details by ID."""
        data = self._load("locations")
        return data.get("locations", {}).get(location_id)

    def get_location_inhabitants(self, location_id: str) -> Dict:
        """Get a location's inhabitants."""
        loc = self.get_location(location_id)
        if loc:
            return loc.get("inhabitants", {"permanent": [], "visitors": []})
        return {"permanent": [], "visitors": []}

    # ==================== CROSS-ENTITY QUERIES ====================

    def get_story_contents(self, story_id: str) -> Dict:
        """Get all entities from a specific story."""
        return {
            "artifacts": self.find_artifacts(story_id=story_id, limit=100),
            "characters": self.find_characters(story_id=story_id, limit=100),
            "locations": self.find_locations(story_id=story_id, limit=100)
        }

    def search_universe(self, query: str, limit: int = 20) -> Dict:
        """
        Full-text search across all entity types.

        Args:
            query: Search text
            limit: Max results per category

        Returns:
            Dict with artifacts, characters, locations matching query
        """
        return {
            "artifacts": self.find_artifacts(search_text=query, limit=limit),
            "characters": self.find_characters(search_text=query, limit=limit),
            "locations": self.find_locations(search_text=query, limit=limit)
        }

    def get_universe_summary(self) -> Dict:
        """
        Get high-level summary of the universe.
        Designed for prompt injection.
        """
        artifacts = self._load("artifacts")
        characters = self._load("characters")
        locations = self._load("locations")
        index = self._load("index")

        return {
            "stats": index.get("stats", {}),
            "total_artifacts": len(artifacts.get("artifacts", {})),
            "total_characters": len(characters.get("characters", {})),
            "total_locations": len(locations.get("locations", {})),
            "artifact_categories": self.list_artifact_categories(),
            "recent_artifacts": self.find_artifacts(limit=5),
            "recent_characters": self.find_characters(limit=5),
            "recent_locations": self.find_locations(limit=5)
        }

    def get_related_entities(self, entity_type: str, entity_id: str) -> Dict:
        """
        Get entities related to a given entity.

        Args:
            entity_type: 'artifact', 'character', or 'location'
            entity_id: The entity's ID

        Returns:
            Dict of related entities by type
        """
        related = {
            "artifacts": [],
            "characters": [],
            "locations": []
        }

        if entity_type == "artifact":
            artifact = self.get_artifact(entity_id)
            if artifact:
                # Get related artifacts
                refs = artifact.get("cross_references", {})
                for rel_id in refs.get("related_artifacts", []):
                    rel = self.get_artifact(rel_id)
                    if rel:
                        related["artifacts"].append({
                            "id": rel_id,
                            "name": rel.get("canonical_name"),
                            "relation": "related"
                        })
                # Get character who created it
                creator = artifact.get("origin", {}).get("created_by_character")
                if creator:
                    char = self.get_character(creator)
                    if char:
                        related["characters"].append({
                            "id": creator,
                            "name": char.get("canonical_name"),
                            "relation": "creator"
                        })

        elif entity_type == "character":
            char = self.get_character(entity_id)
            if char:
                # Get relationships
                for rel_id, rel_info in char.get("relationships", {}).items():
                    rel_char = self.get_character(rel_id)
                    if rel_char:
                        related["characters"].append({
                            "id": rel_id,
                            "name": rel_char.get("canonical_name"),
                            "relation": rel_info.get("type", "related")
                        })

        elif entity_type == "location":
            loc = self.get_location(entity_id)
            if loc:
                # Get connected locations
                for conn_id in loc.get("connected_locations", []):
                    conn = self.get_location(conn_id)
                    if conn:
                        related["locations"].append({
                            "id": conn_id,
                            "name": conn.get("canonical_name"),
                            "relation": "connected"
                        })
                # Get inhabitants
                for char_id in loc.get("inhabitants", {}).get("permanent", []):
                    char = self.get_character(char_id)
                    if char:
                        related["characters"].append({
                            "id": char_id,
                            "name": char.get("canonical_name"),
                            "relation": "inhabitant"
                        })
                # Get artifacts
                for art_id in loc.get("artifacts_discovered_here", []):
                    art = self.get_artifact(art_id)
                    if art:
                        related["artifacts"].append({
                            "id": art_id,
                            "name": art.get("canonical_name"),
                            "relation": "discovered_here"
                        })

        return related

    # ==================== PROMPT CONTEXT GENERATION ====================

    def build_prompt_context(self, genre: str = None, max_items: int = 5) -> str:
        """
        Build a context string for injecting into Claude's prompt.

        Args:
            genre: Current story genre (for filtering)
            max_items: Max items per category to include

        Returns:
            Formatted string describing the universe
        """
        summary = self.get_universe_summary()

        lines = [
            "=== THE CODEX SHARED UNIVERSE ===",
            "",
            f"Universe contains: {summary['total_artifacts']} artifacts, "
            f"{summary['total_characters']} characters, "
            f"{summary['total_locations']} locations",
            ""
        ]

        # Artifacts
        if summary["recent_artifacts"]:
            lines.append("EXISTING ARTIFACTS (real, importable code):")
            for art in summary["recent_artifacts"][:max_items]:
                lines.append(f"  - {art['name']} ({art['category']}): {art.get('description', 'No description')[:60]}")
                if art.get("import"):
                    lines.append(f"    Import: {art['import']}")
            lines.append("")

        # Characters
        if summary["recent_characters"]:
            lines.append("EXISTING CHARACTERS (can return in stories):")
            for char in summary["recent_characters"][:max_items]:
                lines.append(f"  - {char['name']} ({char['type']}): {char.get('occupation', 'Unknown')}")
                lines.append(f"    Last seen in: {char.get('last_seen', 'Unknown')}")
            lines.append("")

        # Locations
        if summary["recent_locations"]:
            lines.append("EXISTING LOCATIONS (can be revisited):")
            for loc in summary["recent_locations"][:max_items]:
                lines.append(f"  - {loc['name']} ({loc['type']}): {loc.get('atmosphere', 'No atmosphere set')}")
            lines.append("")

        lines.extend([
            "RULES FOR SHARED UNIVERSE:",
            "1. You MAY reference existing artifacts - they are real Python code",
            "2. You MAY bring back existing characters - maintain their traits",
            "3. You MAY revisit existing locations - maintain their atmosphere",
            "4. New elements will be auto-registered to the universe",
            "5. Prefer connections to existing elements over isolated new ones",
            ""
        ])

        return "\n".join(lines)
