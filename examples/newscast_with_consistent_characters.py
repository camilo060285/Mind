"""Example: Using consistent characters in NewscastStudio.

Demonstrates how to create and use character assets for consistent
persona generation across multiple episodes.
"""

from pathlib import Path

from mind.agents.newscast_studio.character_manager import CharacterAssetManager

print("=" * 70)
print("NEWSCAST CHARACTER ASSET MANAGEMENT DEMO")
print("=" * 70)
print()

# Initialize character manager
char_manager = CharacterAssetManager()

# Create your host character
print("📝 Creating Host Character...")
host = char_manager.create_character(
    name="Sarah Nova",
    description="professional news anchor, woman in her 30s, business attire, "
    "confident smile, modern newsroom background",
    style_tags=["professional", "friendly", "tech-savvy", "4k quality"],
)

print(f"✅ Created character: {host.name}")
print(f"   ID: {host.character_id}")
print(f"   Fixed Seed: {host.seed}")
print(f"   Base Prompt: {host.base_prompt[:80]}...")
print()

# Create additional characters
print("📝 Creating Supporting Characters...")

analyst = char_manager.create_character(
    name="Dr. Marcus Reed",
    description="AI expert, man in his 40s, professional attire, "
    "thoughtful expression, technology lab background",
    style_tags=["expert", "authoritative", "scientific", "professional"],
)

field_reporter = char_manager.create_character(
    name="Jamie Martinez",
    description="field reporter, person in 20s, casual professional, "
    "energetic demeanor, outdoor settings",
    style_tags=["energetic", "casual", "on-location", "dynamic"],
)

print(f"✅ Created {analyst.name} (Expert)")
print(f"✅ Created {field_reporter.name} (Field Reporter)")
print()

# Generate prompts for different episodes - SAME CHARACTER!
print("=" * 70)
print("GENERATING SCENES WITH CONSISTENT CHARACTERS")
print("=" * 70)
print()

# Episode 1: Opening
print("🎬 Episode 1 - Opening Scene")
scene1 = char_manager.generate_prompt_for_scene(
    host,
    "sitting at news desk, welcoming gesture",
    "warm lighting, professional newsroom",
)
print(f"   Character: {scene1['character_name']}")
print(f"   Prompt: {scene1['prompt'][:100]}...")
print(f"   Seed: {scene1['seed']} (will always be the same!)")
print()

# Episode 2: Explaining tech
print("🎬 Episode 2 - Tech Explanation")
scene2 = char_manager.generate_prompt_for_scene(
    host,
    "standing next to holographic AI diagram, pointing",
    "futuristic tech graphics, engaged expression",
)
print(f"   Character: {scene2['character_name']}")
print(f"   Prompt: {scene2['prompt'][:100]}...")
print(f"   Seed: {scene2['seed']} (same seed = same character!)")
print()

# Episode 3: Interviewing
print("🎬 Episode 3 - Interview with Expert")

# Host scene
host_scene = char_manager.generate_prompt_for_scene(
    host, "sitting in interview chair, listening intently", "split screen setup"
)
print(f"   Host ({host_scene['character_name']}):")
print(f"      Seed: {host_scene['seed']}")
print()

# Expert scene
expert_scene = char_manager.generate_prompt_for_scene(
    analyst, "explaining AI concepts, hand gestures", "technology graphics"
)
print(f"   Expert ({expert_scene['character_name']}):")
print(f"      Seed: {expert_scene['seed']}")
print()

# Episode 4: Field report
print("🎬 Episode 4 - Field Report")
field_scene = char_manager.generate_prompt_for_scene(
    field_reporter,
    "reporting from tech conference, holding microphone",
    "crowd in background, excited atmosphere",
)
print(f"   Reporter ({field_scene['character_name']}):")
print(f"      Prompt: {field_scene['prompt'][:100]}...")
print(f"      Seed: {field_scene['seed']}")
print()

# Show character usage stats
print("=" * 70)
print("CHARACTER USAGE STATISTICS")
print("=" * 70)
print()

for character in char_manager.list_characters():
    print(f"📊 {character.name}")
    print(f"   ID: {character.character_id}")
    print(f"   Used {character.usage_count} times")
    print(f"   Last used: {character.last_used}")
    print(f"   Seed: {character.seed}")
    print()

# Demonstrate export/import
print("=" * 70)
print("EXPORT/IMPORT DEMONSTRATION")
print("=" * 70)
print()

# Export a character
export_path = Path.home() / ".mind" / "temp_character_export.json"
print(f"📤 Exporting {host.name} to {export_path}")
char_manager.export_character(host.character_id, export_path)
print("   ✅ Exported successfully")
print()

# Could import later with:
# imported = char_manager.import_character(export_path)

print("=" * 70)
print("✅ DEMO COMPLETE")
print("=" * 70)
print()
print("Key Benefits:")
print("  • Same seed = same character appearance across all episodes")
print("  • Consistent brand identity for your newscast")
print("  • Easy to manage multiple personas")
print("  • Can export/import characters for sharing or backup")
print()
print("Character assets saved to:")
print(f"  {char_manager.assets_dir}")
