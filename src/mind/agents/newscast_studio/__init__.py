"""NewscastStudio with character asset management.

Provides consistent character generation across newscast episodes using:
- Character Asset Manager for persona persistence
- Fixed seeds for reproducibility
- LoRA/DreamBooth integration
- Scene-specific prompt generation
"""

from mind.agents.newscast_studio.character_manager import (
    CharacterAssetManager,
    CharacterAsset,
    create_default_newscast_characters,
)

__all__ = [
    "CharacterAssetManager",
    "CharacterAsset",
    "create_default_newscast_characters",
]
