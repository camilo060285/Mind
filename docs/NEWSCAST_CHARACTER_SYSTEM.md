# NewscastStudio Character Asset System

Complete guide for creating consistent AI-generated characters for newscast production.

## 🎯 What This Solves

When generating AI images for a newscast, you want **the same host/personas to appear consistently across episodes**. This system ensures:
- Same character appearance every time
- Consistent brand identity
- Easy persona management
- Professional newscast production

## 🚀 Quick Start

### 1. Initialize with Default Characters

```bash
mind newscast init
```

This creates three ready-to-use characters:
- **Alex Tech** - Tech News Host
- **Dr. Sarah Chen** - AI Expert
- **Mike Rivers** - Field Reporter

### 2. Create Your Own Character

```bash
mind newscast character create "Sarah Nova" "professional news anchor, 30s, business attire, confident smile"
```

### 3. Generate Scene Prompts

```bash
mind newscast character scene "Sarah Nova" "sitting at news desk, welcoming viewers"
```

This outputs a prompt with a **fixed seed** - use this with Stable Diffusion to get consistent results!

---

## 📖 Complete Command Reference

### Character Management

#### Create a Character
```bash
# Basic
mind newscast character create "Name" "description"

# With custom tags
mind newscast character create "Alex Reporter" "energetic journalist" --tags "casual,friendly,outdoor"

# With custom prompt
mind newscast character create "Dr. Smith" "expert scientist" --prompt "scientist in lab, detailed"
```

#### List All Characters
```bash
# Quick view
mind newscast character list

# Detailed view
mind newscast character list --detailed
```

#### Show Character Details
```bash
mind newscast character show "Sarah Nova"
```

#### Generate Scene Prompt
```bash
# Basic scene
mind newscast character scene "Sarah Nova" "standing at desk"

# With additional details
mind newscast character scene "Sarah Nova" "presenting graphics" --details "futuristic background"
```

#### Delete a Character
```bash
# With confirmation
mind newscast character delete "Old Character"

# Skip confirmation
mind newscast character delete "Test Character" --yes
```

#### Export/Import Characters
```bash
# Export for backup or sharing
mind newscast character export "Sarah Nova" ~/sarah.json

# Import from file
mind newscast character import ~/sarah.json
```

---

## 🎨 How It Works

### The Consistency Secret: Fixed Seeds

Every character gets a **unique, fixed seed** generated from their ID. When you generate images:

```python
Character: Sarah Nova
Seed: 2847563921  # Always the same!

Episode 1: "sitting at desk" → Seed: 2847563921
Episode 2: "standing" → Seed: 2847563921
Episode 3: "presenting" → Seed: 2847563921
```

**Same seed = Same character appearance!** ✨

### Character Asset Structure

Each character stores:
- **Name**: Human-readable identifier
- **Description**: Detailed appearance
- **Base Prompt**: Core generation prompt
- **Style Tags**: Stylistic attributes
- **Fixed Seed**: Ensures consistency
- **Usage Stats**: Track usage across episodes

---

## 🎬 Real-World Workflow

### Creating a Newscast Series

```bash
# 1. Create your host
mind newscast character create "Morgan Hayes" \
  "professional tech news anchor, 35 years old, modern business casual attire, confident and approachable"

# 2. Create supporting characters
mind newscast character create "Dr. Lisa Park" \
  "AI researcher, 40s, professional, glasses, tech lab background"

mind newscast character create "Jake Wilson" \
  "field reporter, 28, casual professional, energetic"

# 3. Generate Episode 1 scenes
mind newscast character scene "Morgan Hayes" "opening monologue at desk"
# → Use this prompt + seed with Stable Diffusion

mind newscast character scene "Dr. Lisa Park" "explaining AI concepts with diagrams"
# → Use this prompt + seed

# 4. Generate Episode 2 scenes (same characters!)
mind newscast character scene "Morgan Hayes" "standing next to tech display"
# → Same seed as Episode 1 = same character!

mind newscast character scene "Jake Wilson" "reporting from tech conference"
```

---

## 💡 Python API Usage

### Basic Usage

```python
from mind.agents.newscast_studio.character_manager import CharacterAssetManager

# Initialize
manager = CharacterAssetManager()

# Create character
host = manager.create_character(
    name="Sarah Nova",
    description="professional news anchor, 30s, business attire",
    style_tags=["professional", "friendly", "tech-savvy"]
)

print(f"Character: {host.name}")
print(f"Seed: {host.seed}")  # Use this seed for all episodes!

# Generate scene
scene = manager.generate_prompt_for_scene(
    host,
    "sitting at news desk",
    "warm lighting, professional newsroom"
)

print(f"Prompt: {scene['prompt']}")
print(f"Seed: {scene['seed']}")
print(f"Negative: {scene['negative_prompt']}")
```

### Advanced: Multiple Characters

```python
# Create a cast
host = manager.create_character(
    name="Morgan Hayes",
    description="tech news anchor, confident, professional",
    style_tags=["professional", "newsroom"]
)

analyst = manager.create_character(
    name="Dr. Chen",
    description="AI expert, glasses, lab coat",
    style_tags=["expert", "scientific"]
)

# Generate coordinated scenes
host_scene = manager.generate_prompt_for_scene(
    host, "asking question to expert"
)

analyst_scene = manager.generate_prompt_for_scene(
    analyst, "answering question, explaining diagram"
)

# Both scenes maintain character consistency!
```

---

## 🔍 Understanding Character Assets

### Storage Location
```
~/.mind/
└── newscast_studio/
    └── character_assets/
        ├── a1b2c3d4e5f6.json  # Character 1
        ├── f6e5d4c3b2a1.json  # Character 2
        └── ...
```

### Character File Format
```json
{
  "character_id": "a1b2c3d4e5f6",
  "name": "Sarah Nova",
  "description": "professional news anchor, 30s...",
  "base_prompt": "professional news anchor, 30s, professional, friendly, ...",
  "style_tags": ["professional", "friendly", "tech-savvy"],
  "seed": 2847563921,
  "created_at": "2026-02-15T10:30:00",
  "last_used": "2026-02-15T14:20:00",
  "usage_count": 15
}
```

---

## 🎓 Integration with AI Image Generation

### With Stable Diffusion

```bash
# 1. Get character prompt
mind newscast character scene "Sarah Nova" "at desk" > prompt.txt

# 2. Extract seed and prompt from output

# 3. Use with stable-diffusion-webui or API:
python scripts/txt2img.py \
  --prompt "$(cat prompt.txt)" \
  --seed 2847563921 \
  --steps 50 \
  --cfg_scale 7.5
```

### With Python + Diffusers

```python
from diffusers import StableDiffusionPipeline
from mind.agents.newscast_studio.character_manager import CharacterAssetManager

# Get character scene
manager = CharacterAssetManager()
host = manager.get_character_by_name("Sarah Nova")
scene = manager.generate_prompt_for_scene(host, "at news desk")

# Generate with Stable Diffusion
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
pipe = pipe.to("cuda")

image = pipe(
    prompt=scene['prompt'],
    negative_prompt=scene['negative_prompt'],
    generator=torch.Generator().manual_seed(scene['seed']),
    num_inference_steps=50
).images[0]

image.save(f"episode_1_{host.name}.png")
```

---

## 🌟 Best Practices

### 1. Detailed Descriptions
```bash
# ❌ Too vague
mind newscast character create "Host" "news person"

# ✅ Detailed
mind newscast character create "Morgan Hayes" \
  "professional tech news anchor, 35 years old, shoulder-length brown hair, 
   modern business casual attire, confident smile, newsroom background"
```

### 2. Consistent Style Tags
Use the same tags across similar characters:
- Professional newscast: `professional, newsroom, business attire`
- Casual segments: `casual, friendly, approachable`
- Expert interviews: `expert, authoritative, professional`

### 3. Test Your Character
Generate a few test images first to ensure consistency:
```bash
# Test different angles
mind newscast character scene "Host" "front view at desk"
mind newscast character scene "Host" "side profile presenting"
mind newscast character scene "Host" "standing full body"
```

### 4. Backup Your Characters
```bash
# Export all characters
for char in $(mind newscast character list | grep "│" | awk '{print $2}'); do
    mind newscast character export "$char" "backup_${char}.json"
done
```

---

## 🐛 Troubleshooting

### Character Looks Different Each Time
- **Check seed usage**: Make sure you're using the exact seed from the scene generation
- **Try different checkpoint**: Some SD models handle seeds differently
- **Use --cfg_scale 7-9**: Higher guidance scale improves consistency

### Character Not Found
```bash
# List all characters to see exact names
mind newscast character list

# Names are case-sensitive!
mind newscast character show "Sarah Nova"  # ✅
mind newscast character show "sarah nova"  # ❌
```

### Import Failed
- Check JSON format is valid
- Ensure all required fields are present
- Try exporting an existing character to see correct format

---

## 📚 Examples

See `examples/newscast_with_consistent_characters.py` for complete working examples.

Run the demo:
```bash
cd ~/mind
source mind-env/bin/activate
python examples/newscast_with_consistent_characters.py
```

---

## 🤝 Contributing

Want to add features like:
- LoRA weight integration
- Reference image support
- DreamBooth training hooks
- Multi-character scene composition

Contributions welcome!

---

## 📖 Related Documentation

- [NewscastStudio Overview](../docs/NEWSCAST_OVERVIEW.md)
- [AI Image Generation Guide](../docs/IMAGE_GENERATION.md)
- [Character Consistency Techniques](../docs/CHARACTER_CONSISTENCY.md)

---

**Made with Mind 🧠**
