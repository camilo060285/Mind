# Phi Semi-Autonomous Setup Guide

This guide explains how phi (via llama.cpp) is now wired as the default LLM for autonomous operation across both Mind and 2d_animation_studio.

## What Changed

- ✅ Phi model selected as primary LLM (lightweight, on-device, no cloud costs)
- ✅ Environment variables configured in `.env` files
- ✅ Startup validation added to catch configuration issues early
- ✅ Benchmark score: **0.6636 normalized** (exceeds ≥0.65 autonomy threshold)

## Quick Start

### 1. Verify Setup

Before running any autonomous workflows, validate the phi installation:

```bash
# In Mind repo
cd ~/mind
python scripts/validate_llm_setup.py
```

Expected output:
```
✓ Configuration: provider=llama_cpp, model=phi
✓ llama.cpp binary found: /home/cris_agent_admin/llama.cpp/build/bin/llama-completion
✓ Models directory found: /home/cris_agent_admin/local_llms/models
✓ Phi model found: /home/cris_agent_admin/local_llms/models/llm_a/model.gguf (1706.4 MB)
✓ All systems ready for autonomous operation!
```

If validation fails, follow the instructions in the error message.

### 2. Use with Mind CLI

```bash
# Load Mind CLI (automatically loads .env)
cd ~/mind
python -m mind.cli info
python -m mind.cli list
```

### 3. Use with 2D Animation Studio

```bash
# Load Studio CLI (automatically loads .env)
cd ~/2d_animation_studio
python cli/studio.py --help
```

Both CLIs automatically:
- Load `.env` configuration at startup
- Initialize phi as the default LLM provider
- Connect to llama.cpp with found models

## Configuration Files

### ~/.env (Mind)
```env
MIND_LLM_PROVIDER=llama_cpp
MIND_LLM_MODEL=phi
MIND_LLAMA_BIN=/home/cris_agent_admin/llama.cpp/build/bin/llama-completion
MIND_MODELS_DIR=/home/cris_agent_admin/local_llms/models
```

### ~/.env (2d_animation_studio)
Same as Mind (inherits the same environment variables).

## Performance Notes

### Phi Benchmark Results

| Case | Score | Status |
|------|-------|--------|
| encoder_ryxen_identity | 0.5636 | Uses fallback (schema valid) |
| script_episode_opening | 0.7091 | Strong (70% keyword match) |
| shot_prompt_pack | 0.4909 | Acceptable |
| production_plan | 0.8909 | Excellent (100% keyword match) |
| **Overall** | **0.6636** | **✓ Autonomy Ready** |

The system is ready for semi-autonomous operation:
- Generates scripts/prompts without cloud dependencies
- Graceful fallback ensures no hard failures
- Quality gates can enforce normalized_score >= 0.65

### Temperature/Token Tuning

Phi can be tuned for better JSON output by modifying `LlamaCppProvider`:

```python
# Default: temperature=0.7 (more creative)
# For JSON: temperature=0.3-0.5 (more deterministic)
provider = LlamaCppProvider(model="phi", temperature=0.4)
```

Current defaults are in [src/mind/cognition/providers/llama_cpp_provider.py](../src/mind/cognition/providers/llama_cpp_provider.py#L30).

## Troubleshooting

### "llama-completion not found"
Build llama.cpp:
```bash
cd ~/llama.cpp && mkdir -p build && cd build
cmake .. && make
```

### "Phi model not found"
Download from HuggingFace:
```bash
mkdir -p ~/local_llms/models/llm_a
# Download model.gguf to ~/local_llms/models/llm_a/
```

### Slow inference on CPU
- Consider using cloud providers (OpenAI, Anthropic) if latency is critical
- Or use GPU-accelerated llama.cpp with CUDA support

## Next Steps

1. **Implement semi-autonomous approval queue** (draft → rank → approve)
2. **End-to-end test** with Ryxen character generation
3. **Monitor production quality** with benchmark score tracking
4. **Consider cloud fallback** if local latency becomes bottleneck

## Reference Files

- [Benchmark Results](../benchmarks/results_phi_few_shot_v3.json)
- [Benchmark Runner](../scripts/benchmark_llm_matrix.py)
- [LLM Provider Config](../src/mind/cognition/llm_config.py)
- [Phi Provider](../src/mind/cognition/providers/llama_cpp_provider.py)
