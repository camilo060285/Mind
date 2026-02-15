"""Character Asset Manager for NewscastStudio.

Manages consistent character generation across episodes using:
- Text embeddings for character descriptions
- Reference image embeddings
- Fixed seeds for reproducibility
- LoRA/DreamBooth integration
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class CharacterAsset:
    """Represents a consistent character for newscast."""

    character_id: str
    name: str
    description: str  # Detailed appearance description
    base_prompt: str  # Core prompt for generation
    style_tags: List[str]  # [professional, friendly, tech-focused, etc.]
    seed: int  # Fixed seed for consistency

    # Optional advanced features
    lora_path: Optional[str] = None  # Path to LoRA weights
    textual_inversion_token: Optional[str] = None  # Custom token
    reference_images: Optional[List[str]] = None  # Path to ref images
    embedding_vector: Optional[List[float]] = None  # Cached embedding

    # Metadata
    created_at: str = ""
    last_used: str = ""
    usage_count: int = 0


class CharacterAssetManager:
    """Manages character assets for consistent generation."""

    def __init__(self, assets_dir: Optional[Path] = None):
        """Initialize character asset manager.

        Args:
            assets_dir: Directory to store character assets
                       (default: ~/.mind/newscast_studio/character_assets)
        """
        if assets_dir is None:
            assets_dir = Path.home() / ".mind" / "newscast_studio" / "character_assets"

        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        self.characters: Dict[str, CharacterAsset] = {}
        self._load_characters()

    def _generate_character_id(self, name: str) -> str:
        """Generate unique character ID from name.

        Args:
            name: Character name

        Returns:
            Unique character ID
        """
        # Use hash for uniqueness
        hash_input = f"{name}_{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def _generate_seed(self, character_id: str) -> int:
        """Generate consistent seed for character.

        Args:
            character_id: Character ID

        Returns:
            Fixed seed for generation
        """
        # Use character ID to generate deterministic seed
        return int(hashlib.md5(character_id.encode()).hexdigest()[:8], 16)

    def _generate_base_prompt(self, description: str, style_tags: List[str]) -> str:
        """Generate base prompt from description and tags.

        Args:
            description: Character description
            style_tags: Style tags

        Returns:
            Base prompt for generation
        """
        tags_str = ", ".join(style_tags)
        return (
            f"{description}, {tags_str}, consistent character, high quality, detailed"
        )

    def create_character(
        self,
        name: str,
        description: str,
        style_tags: List[str],
        base_prompt: Optional[str] = None,
        reference_images: Optional[List[str]] = None,
    ) -> CharacterAsset:
        """Create a new character asset.

        Args:
            name: Character name
            description: Detailed appearance description
            style_tags: Style tags (professional, casual, etc.)
            base_prompt: Optional base prompt (auto-generated if not provided)
            reference_images: Optional paths to reference images

        Returns:
            Created character asset
        """
        character_id = self._generate_character_id(name)
        seed = self._generate_seed(character_id)

        # Auto-generate base prompt if not provided
        if base_prompt is None:
            base_prompt = self._generate_base_prompt(description, style_tags)

        character = CharacterAsset(
            character_id=character_id,
            name=name,
            description=description,
            base_prompt=base_prompt,
            style_tags=style_tags,
            seed=seed,
            reference_images=reference_images,
            created_at=datetime.now().isoformat(),
            last_used=datetime.now().isoformat(),
            usage_count=0,
        )

        self.characters[character_id] = character
        self._save_character(character)

        return character

    def get_character(self, character_id: str) -> Optional[CharacterAsset]:
        """Get character by ID.

        Args:
            character_id: Character ID

        Returns:
            Character asset or None
        """
        return self.characters.get(character_id)

    def get_character_by_name(self, name: str) -> Optional[CharacterAsset]:
        """Get character by name.

        Args:
            name: Character name

        Returns:
            Character asset or None
        """
        for character in self.characters.values():
            if character.name.lower() == name.lower():
                return character
        return None

    def list_characters(self) -> List[CharacterAsset]:
        """List all characters.

        Returns:
            List of all character assets
        """
        return list(self.characters.values())

    def generate_prompt_for_scene(
        self,
        character: CharacterAsset,
        scene_description: str,
        additional_details: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate prompt for a specific scene with this character.

        Args:
            character: Character asset
            scene_description: Scene description (e.g., "standing at desk")
            additional_details: Optional additional details

        Returns:
            Generation parameters including prompt and seed
        """
        # Build scene-specific prompt while maintaining character consistency
        prompt_parts = [
            character.base_prompt,
            scene_description,
        ]

        if additional_details:
            prompt_parts.append(additional_details)

        full_prompt = ", ".join(prompt_parts)

        # Update usage stats
        character.last_used = datetime.now().isoformat()
        character.usage_count += 1
        self._save_character(character)

        return {
            "prompt": full_prompt,
            "negative_prompt": "inconsistent, multiple people, distorted, blurry, low quality",
            "seed": character.seed,
            "character_id": character.character_id,
            "character_name": character.name,
        }

    def update_character(
        self,
        character_id: str,
        updates: Dict[str, Any],
    ) -> Optional[CharacterAsset]:
        """Update character asset.

        Args:
            character_id: Character ID
            updates: Dictionary of fields to update

        Returns:
            Updated character or None
        """
        character = self.characters.get(character_id)
        if not character:
            return None

        # Update allowed fields
        for key, value in updates.items():
            if hasattr(character, key):
                setattr(character, key, value)

        self._save_character(character)
        return character

    def delete_character(self, character_id: str) -> bool:
        """Delete character asset.

        Args:
            character_id: Character ID

        Returns:
            True if deleted, False if not found
        """
        if character_id not in self.characters:
            return False

        # Remove from memory
        del self.characters[character_id]

        # Remove from disk
        character_file = self.assets_dir / f"{character_id}.json"
        if character_file.exists():
            character_file.unlink()

        return True

    def export_character(self, character_id: str, export_path: Path) -> bool:
        """Export character asset to file.

        Args:
            character_id: Character ID
            export_path: Path to export to

        Returns:
            True if exported successfully
        """
        character = self.characters.get(character_id)
        if not character:
            return False

        with open(export_path, "w") as f:
            json.dump(asdict(character), f, indent=2)

        return True

    def import_character(self, import_path: Path) -> Optional[CharacterAsset]:
        """Import character asset from file.

        Args:
            import_path: Path to import from

        Returns:
            Imported character or None
        """
        try:
            with open(import_path) as f:
                data = json.load(f)

            character = CharacterAsset(**data)
            self.characters[character.character_id] = character
            self._save_character(character)

            return character
        except Exception as e:
            print(f"Error importing character: {e}")
            return None

    def _save_character(self, character: CharacterAsset):
        """Save character to disk.

        Args:
            character: Character asset to save
        """
        character_file = self.assets_dir / f"{character.character_id}.json"

        with open(character_file, "w") as f:
            json.dump(asdict(character), f, indent=2)

    def _load_characters(self):
        """Load all characters from disk."""
        if not self.assets_dir.exists():
            return

        for character_file in self.assets_dir.glob("*.json"):
            try:
                with open(character_file) as f:
                    data = json.load(f)

                character = CharacterAsset(**data)
                self.characters[character.character_id] = character
            except Exception as e:
                print(f"Error loading character {character_file}: {e}")


def create_default_newscast_characters() -> Dict[str, CharacterAsset]:
    """Create default character assets for NewscastStudio.

    Returns:
        Dictionary of character ID to CharacterAsset
    """
    manager = CharacterAssetManager()

    # Tech News Host
    tech_host = manager.create_character(
        name="Alex Tech",
        description="professional news anchor, 30s, confident expression, modern attire",
        style_tags=["professional", "tech-focused", "friendly", "newsroom setting"],
        reference_images=None,
    )

    # AI Expert Analyst
    ai_expert = manager.create_character(
        name="Dr. Sarah Chen",
        description="AI researcher, 40s, professional, glasses, science background",
        style_tags=["expert", "academic", "authoritative", "lab setting"],
    )

    # Field Reporter
    field_reporter = manager.create_character(
        name="Mike Rivers",
        description="energetic reporter, 25s, casual professional, outdoor settings",
        style_tags=["energetic", "casual", "on-location", "friendly"],
    )

    return {
        tech_host.character_id: tech_host,
        ai_expert.character_id: ai_expert,
        field_reporter.character_id: field_reporter,
    }
