# Quick Start: LLM Integration for Mind Agents

## ✅ Setup Complete!

Your local LLM infrastructure is now integrated into the Mind framework:

```
✓ Phi model (1.7GB) - llm_a
✓ Qwen model (4.4GB) - llm_b
✓ llama.cpp compiled and ready
✓ LLM interface abstraction added
✓ Configuration system implemented
```

## One-Minute Start

```python
from mind.cognition import init_llm

# Get Phi (fast, lightweight)
llm = init_llm(model="phi")

# Or Qwen (better reasoning)
# llm = init_llm(model="qwen")

# Generate text
output = llm.generate("Explain quantum computing")
print(output)

# Parse tasks in natural language
task = llm.parse_task("Create an animation of solar system planets")
print(task["task_type"])  # visualization
print(task["subtasks"])   # [list of steps]

# Create execution plan
plan = llm.create_plan("Build a web dashboard", agents=[...])

# Reasoning about problems
reasoning = llm.reasoning("How to optimize database queries?")
```

## Making Agents Intelligent

Before (placeholder):
```python
class AnimationAgent:
    def run(self, task):
        result = {
            "status": "success",
            "output": {},  # Empty!
        }
        return result
```

After (with LLM):
```python
from mind.cognition import get_default_llm

class AnimationAgent:
    def __init__(self):
        self.llm = get_default_llm()
    
    def run(self, task_description: str):
        # Let LLM understand what to do
        parsed = self.llm.parse_task(task_description)
        
        # Reason about how to execute
        reasoning = self.llm.reasoning(parsed["goal"])
        
        # Execute based on reasoning
        if "animation" in parsed["task_type"]:
            result = self.create_animation(parsed)
        else:
            result = self.handle_other(parsed)
        
        return {"status": "success", "output": result}
```

## Files Added

```
src/mind/cognition/
├── llm_interface.py          # Abstract interface
├── llm_config.py             # Configuration & factory
├── providers/
│   ├── __init__.py
│   └── llama_cpp_provider.py # Your local llama.cpp integration
└── __init__.py               # Updated exports

docs/
└── llm_integration.md        # Full documentation

examples/
└── llm_usage_example.py      # Complete working examples

test_llm_setup.py             # Verification test
```

## Environment Variables (Optional)

```bash
# Use Qwen instead of Phi by default
export MIND_LLM_MODEL=qwen

# Custom paths (if you move models)
export MIND_LLAMA_BIN=/custom/path/llama-completion
export MIND_MODELS_DIR=/custom/path/models
```

## Architecture Diagram

```
Your Raspberry Pi:
┌─────────────────────────────────────┐
│  Mind Agents (AnimationAgent, etc)  │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  LLM Integration Layer              │
│  (llm_interface.py)                 │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  LlamaCppProvider                   │
│  (local inference, zero cost)       │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  llama.cpp + local models           │
│  ├─ Phi (1.7GB) - llm_a            │
│  └─ Qwen (4.4GB) - llm_b           │
└─────────────────────────────────────┘
```

## Next Steps

1. **Review** [docs/llm_integration.md](../../docs/llm_integration.md) for detailed docs
2. **Run examples** with `python examples/llm_usage_example.py`
3. **Update agents** to use LLM for:
   - Task understanding
   - Execution planning
   - Reasoning & validation
   - Inter-agent communication

## What This Enables

### Before (Static Agents)
- Fixed logic per agent
- No understanding of natural language
- Rigid task specifications
- No reasoning capability

### After (Intelligent Agents)
- ✅ Natural language understanding
- ✅ Dynamic planning & reasoning
- ✅ Flexible task handling
- ✅ Self-validating outputs
- ✅ Zero cloud costs (local inference)

## Cost Comparison

| Approach | Monthly Cost | Infrastructure |
|----------|-------------|-----------------|
| **Your Current Setup** | $0 | Raspberry Pi (already have) |
| Cloud APIs | $50-500+ | External servers |

## Questions?

- Full docs: [docs/llm_integration.md](../../docs/llm_integration.md)
- Examples: [examples/llm_usage_example.py](../../examples/llm_usage_example.py)
- Test setup: Run `python test_llm_setup.py`

---

**Your Mind system is now intelligent! 🧠**
