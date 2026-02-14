# NewscastStudio Development Roadmap

## Current State Assessment

### ✅ What NewscastStudio CAN Do Right Now

1. **Take a market topic** → `newscast create "Apple stock jumps 15%"`
2. **Generate professional analysis** (using Mind's LLM)
   - News hook identification
   - Key points extraction
   - Market impact analysis
3. **Write broadcast script** (LLM-generated, broadcast-ready)
   - Professional tone
   - Proper timing (60 seconds = ~150 words)
   - Structure: Intro → Body → Outlook → Outro
4. **Create anchor directions** (LLM-generated)
   - Voice delivery instructions (pace, emphasis)
   - Facial expressions guidance
   - Gestures at specific moments
   - Camera angles
5. **Store complete project** as JSON
   - Location: `~/.newscast/broadcasts/broadcast_20260214_120000_apple_stock/broadcast.json`
   - Contains all agent outputs
6. **Collect feedback** → `newscast feedback <id> --engagement 75 --quality 8`
7. **Feed Mind's learning system** automatically

### ❌ What's NOT Done Yet

| Component | Status | Why |
|-----------|--------|-----|
| **Voice narration** | ❌ Not integrated | Needs ElevenLabs API integration |
| **Character/Avatar** | ❌ Not created | Needs character design + Synthesia/D-ID integration |
| **Image generation** | ❌ Not integrated | Needs DALL-E or Stable Diffusion pipeline |
| **Video assembly** | ❌ Not built | Needs FFmpeg coordination + scene sequencing |
| **Publishing** | ❌ Not set up | Needs YouTube/Twitter API integration |
| **Full automation** | ❌ One-click flow | Manual assembly required until all pieces ready |

---

## The Gap: Understanding Your Manual Process

**Right now, the workflow would be:**

```
1. newscast create "Apple stock news"
   └─ OUTPUT: Script + Directions (JSON)

2. [MANUAL] Use Stable Diffusion / DALL-E
   └─ Generate images based on market topic
   └─ Create 4-5 key visual frames

3. [MANUAL] Create/Find Character
   └─ Use character design tools
   └─ Or use Synthesia template (needs integration)

4. [MANUAL] Generate Voice
   └─ Copy script from NewscastStudio
   └─ Generate voice via ElevenLabs (manual upload)

5. [MANUAL] Assemble Video
   └─ Use Synthesia / D-ID / custom video tool
   └─ Combine: Character + Voice + Visuals

6. [MANUAL] Upload & Share
   └─ YouTube / Twitter

7. [AUTO] Collect Feedback
   └─ newscast feedback <id> --engagement X --quality Y
   └─ Mind learns from performance
```

**This is inefficient.** You need to automate the gap.

---

## Realistic 4-Phase Roadmap

### PHASE 1: Understanding & Manual MVP (1-2 weeks)
**Goal:** Create ONE complete broadcast manually to understand the full pipeline

**What you do:**
1. Create newscast topic
2. Get generated script + directions
3. Design/find ONE reusable character
4. Generate images for that character (Stable Diffusion)
5. Generate voice (manual ElevenLabs)
6. Assemble video (FFmpeg or Synthesia)
7. Publish and collect feedback

**Deliverable:** First complete broadcast
**What you learn:** Exact pipeline, timing, quality issues

**Key questions answered:**
- How long does character creation take?
- Do generated images match script quality?
- What voice characteristics work best?
- How much manual editing is needed?

---

### PHASE 2: Automation Layer 1 (2-3 weeks)
**Goal:** Automate the API calls and image generation

**Build:**

#### 2a. **Character System** (`src/newscast/character/`)
```python
class CharacterManager:
    """Manages character templates and customization"""
    
    def create_character(self, name, description, style):
        # Generate character description for AI systems
        pass
    
    def get_character(self, character_id):
        pass
```

**What it does:**
- Stores character templates (Synthesia IDs, D-ID APIs, custom JSON)
- Maps market topics to character personas
- Example: "Financial news" → Professional anchor character

**Deliverable:** 3-5 reusable character templates

---

#### 2b. **Image Generation Pipeline** (`src/newscast/integrations/image_generator.py`)
```python
class ImageGenerator:
    """Generates visuals for broadcasts"""
    
    def generate_from_script(self, script, style):
        # Take script → Generate 4 key visual frames
        # Uses Stable Diffusion or DALL-E
        pass
```

**What it does:**
- Takes script sections
- Generates matching images
- Stores in broadcast folder
- Creates image sequence timeline

**Integration point:** Stable Diffusion (free locally) or DALL-E (cost)

**Deliverable:** Script → 4-5 matching images automatically

---

#### 2c. **Voice Integration** (`src/newscast/integrations/voice_generator.py`)
```python
class VoiceGenerator:
    """Generates voice narration"""
    
    def generate_voice(self, script, voice_id, language):
        # ElevenLabs API integration
        # Returns: MP3 audio file
        pass
```

**What it does:**
- Takes script from NewscastStudio
- Calls ElevenLabs API (cost: $0.03-0.05 per broadcast)
- Generates MP3 with proper timing
- Stores in broadcast folder

**Deliverable:** Script → Professional voice automatically

---

#### 2d. **CLI Updates**
```bash
newscast create "Apple stock" \
  --character "professional_anchor" \
  --voice "male_professional" \
  --image-style "financial_market" \
  --generate-images \
  --generate-voice

# Outputs: Script + Images + Voice (ready for video assembly)
```

---

### PHASE 3: Video Assembly (1 week)
**Goal:** Combine character + voice + images into video

#### 3a. **Video Composer** (`src/newscast/integrations/video_composer.py`)

**Option A: Synthesia Integration** (Recommended for start)
```python
class SynthesiaComposer:
    def create_video(self, character_id, voice_file, images):
        # Sends to Synthesia API
        # Returns: Video file
```
- Cost: $0.30-0.50 per video
- Quality: Professional, lip-synced
- Speed: 5-10 minutes

**Option B: Custom FFmpeg** (Free but manual)
```python
class FFmpegComposer:
    def create_video(self, voice_file, images, directions):
        # ffmpeg: combine images + transitions + voice
        # Output: MP4
```
- Cost: $0
- Quality: Good (pan/zoom/transitions)
- Speed: Instant
- Limitation: No character movement

**Decision:** Start with Synthesia, fallback to FFmpeg for MVP

#### 3b. **Publishing Pipeline** (`src/newscast/integrations/publisher.py`)
```python
class Publisher:
    def publish_to_youtube(self, video_file, metadata):
        pass
    
    def publish_to_twitter(self, video_file, metadata):
        pass
```

---

### PHASE 4: Full Automation + Intelligence (2-3 weeks)
**Goal:** One command creates and publishes complete broadcast

#### 4a. **Orchestrator v2**
```bash
newscast create "Tesla earnings" --auto-publish-youtube

# This does:
# 1. Create script + analysis
# 2. Generate images
# 3. Generate voice
# 4. Compose video
# 5. Publish to YouTube
# 6. Collect metrics
# 7. Feed to Mind's learning system
```

#### 4b. **Scheduling & Automation**
```bash
newscast schedule --hourly "Market headlines"
# Runs every hour, creates broadcast automatically
```

#### 4c. **Analytics Integration**
```bash
newscast analytics <broadcast_id>
# Shows: Views, engagement, retention
# Feeds back to Mind for learning
```

#### 4d. **Advanced Learning**
- Mind suggests topics likely to perform
- Character selection optimized by performance
- Image styles ranked by engagement
- Voice characteristics tested

---

## Detailed Implementation Plan

### IMMEDIATE (This Week)

#### Step 1: Create your first character
**Option A: Use Synthesia (Easier, requires account)**
- Create free Synthesia account
- Pick an avatar (professional, news anchor style)
- Get your character ID
- Store in: `src/newscast/character/templates.json`

**Option B: Create custom character**
- Use Stable Diffusion to generate character image
- Document character description
- Store in your local system

```json
{
  "characters": {
    "professional_anchor": {
      "name": "Alex Markets",
      "description": "Professional financial news anchor",
      "voice_style": "authoritative_calm",
      "synthesia_id": "YOUR_ID_HERE",
      "image_path": "characters/professional_anchor.png",
      "default_attire": "formal_business"
    }
  }
}
```

#### Step 2: Create your first broadcast manually
```bash
# Generate script from NewscastStudio
newscast create "Apple stock reaches all-time high"

# This gives you:
# - Script (copy it)
# - Analysis
# - Directions
# - Saved to ~/.newscast/broadcasts/broadcast_20260214_120000_apple_stock/broadcast.json
```

#### Step 3: Generate images (Manual)
**Using Stable Diffusion locally:**
```python
from diffusers import StableDiffusionPipeline

prompt = "Professional financial market broadcast set, modern trading desk, blue theme"
# Generate image
# Save to broadcast folder
```

**Or DALL-E (costs $0.02 per image):**
- Just send prompt to API

#### Step 4: Generate voice (Manual via ElevenLabs)
- Copy script sections (intro, body, outro)
- Upload to ElevenLabs dashboard
- Select "professional male" voice
- Download MP3
- Save to broadcast folder

#### Step 5: Assemble video
**Simple option: FFmpeg + Synthesia**

If using Synthesia:
1. Send character + voice + images to API
2. Get video back
3. Upload to YouTube

If using FFmpeg:
1. Create video with transitions
2. Overlay voice
3. Add image sequences
4. Export MP4

#### Step 6: Collect feedback
```bash
newscast feedback broadcast_20260214_120000_apple_stock \
  --engagement 80 \
  --quality 8 \
  --comments "Professional look, voice was perfect, images matched well"
```

#### Step 7: Observe Mind learning
```bash
newscast learn
# Should show: First broadcast recorded, waiting for more data
```

---

### THEN Phase 2: Automation (Week 2-3)

Once you understand the manual process, build integrations:

1. **ImageGenerator** (takes script → generates images via Stable Diffusion)
2. **VoiceGenerator** (takes script → generates voice via ElevenLabs API)
3. **VideoComposer** (takes images + voice → creates video via Synthesia or FFmpeg)
4. **Updated orchestrator** (coordinates all three)

---

## Implementation Order (Most Efficient)

### Week 1: MVP Manual
```
Day 1: Character design/selection
Day 2-3: Manual broadcast creation (script + images + voice)
Day 4: Video assembly
Day 5: Publish + feedback collection
Day 6-7: Document learnings, identify pain points
```

### Week 2-3: Automate APIs
```
Day 1-2: ImageGenerator integration (Stable Diffusion local)
Day 3-4: VoiceGenerator integration (ElevenLabs API)
Day 5-6: VideoComposer integration (Synthesia or FFmpeg)
Day 7: CLI updates + testing
```

### Week 4: Polish
```
Day 1-3: Reliability + error handling
Day 4-5: Documentation + examples
Day 6-7: Performance optimization
```

---

## File Structure You'll Build

```
newscast-studio/
├── src/newscast/
│   ├── characters/                    ← NEW
│   │   ├── __init__.py
│   │   └── character_manager.py
│   ├── integrations/                  ← EXPAND
│   │   ├── image_generator.py         ← NEW
│   │   ├── voice_generator.py         ← NEW
│   │   ├── video_composer.py          ← NEW
│   │   ├── publisher.py               ← NEW
│   │   └── (future: elevenlabs.py, synthesia.py, etc)
│   ├── orchestrator.py                ← UPDATE
│   ├── cli/
│   │   └── newscast_cli.py            ← UPDATE (new commands)
│   └── agents/
│       └── (existing - no change needed)
└── docs/
    ├── IMPLEMENTATION_ROADMAP.md      ← THIS FILE
    ├── PHASE_1_MANUAL_PROCESS.md      ← How-to manual creation
    ├── PHASE_2_AUTOMATION.md          ← Integration details
    └── CHARACTER_DESIGN.md            ← Character system design
```

---

## Cost Analysis

### Current Cost (Phase 1 - Manual)
- NewscastStudio generation: $0 (local LLM)
- Image generation: $0.02-0.04 per image × 4 = $0.08-0.16
- Voice generation: $0.03-0.05 per broadcast
- Video creation (Synthesia): $0.30-0.50
- **Total per broadcast: ~$0.40-0.70**

### Future Cost (Phase 2+ - Automated)
- Same as above (just automated)
- Bulk discounts possible ($12-20/month for unlimited voice)
- **Total: ~$0.30-0.50 per broadcast at scale**

### Revenue Targets
- **B2C**: $9.99/month (10 broadcasts) = $10/month revenue, cost ~$4
- **B2B**: $500+/month (custom news for financial firms) = $500+ revenue

---

## Success Metrics for Each Phase

### Phase 1 (Manual MVP)
✅ Successfully create 1 complete broadcast end-to-end  
✅ Video quality acceptable for YouTube  
✅ Script quality rated 7+/10  
✅ Audio clarity excellent  
✅ Total time: < 4 hours per broadcast  

### Phase 2 (Automation Layer 1)
✅ Images auto-generated from script  
✅ Voice auto-generated from script  
✅ Time per broadcast: < 1 hour  
✅ Quality maintained (7+/10)  
✅ 5+ successful broadcasts created and published  

### Phase 3 (Video Assembly)
✅ Full video generated end-to-end  
✅ Time per broadcast: < 5 minutes  
✅ Professional quality maintained  
✅ Publishing to YouTube automated  

### Phase 4 (Full Automation + Intelligence)
✅ Single command: `newscast create --auto-publish`  
✅ Scheduling: Hourly/daily broadcasts work  
✅ Mind learning: Visible improvements in agent performance  
✅ Revenue: First customers using the system  

---

## Critical Implementation Notes

### Character System (Critical for Quality)
- Character choice massively affects output quality
- Professional vs casual character → different audience
- Multiple characters → flexibility but more setup
- **Start with 1-2 characters, expand later**

### Image Generation Strategy
**Recommended: Hybrid approach**
- Use Stable Diffusion locally (free) for rapid iteration
- Use DALL-E for specific high-quality shots
- Cache successful images (reuse across topics)

### Voice Generation Strategy
- ElevenLabs: Best quality, $0.03 per broadcast
- Alternative: Google TTS (free but lower quality)
- **Recommendation:** ElevenLabs from start (worth the cost)

### Video Assembly Strategy
- **For MVP:** Synthesia (professional but $0.30-0.50)
- **For efficiency:** FFmpeg + custom transitions (free)
- **Eventually:** Both (Synthesia for hero videos, FFmpeg for quick turnarounds)

---

## Decision Points You Need to Make

1. **Character approach**: Synthesia template vs custom?
2. **Image generation**: Stable Diffusion (local) vs DALL-E (cloud)?
3. **Video composition**: Synthesia (easy) vs FFmpeg (free)?
4. **Launch strategy**: Perfect MVP vs quick beta?

### My Recommendation
1. **Character**: Use Synthesia's "Finance News Anchor" template (professional, ready-to-go)
2. **Images**: Stable Diffusion locally (free, fast iteration)
3. **Video**: Synthesia (one-click, professional output)
4. **Timeline**: 2 weeks to working system

**This gets you to working "newscast create → publish" in 2 weeks.**

---

## Next Action

Which phase should we start with?

**Option A:** Let me create Phase 1 documentation (detailed manual process step-by-step)
**Option B:** Create character management system for Phase 2
**Option C:** Create image generation integration for Phase 2
**Option D:** All of above - full implementation guide

What's your preference?
