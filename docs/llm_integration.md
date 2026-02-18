# LLM Integration for Mind Agents

## Overview

The Mind framework now supports **LLM integration** for intelligent agent orchestration and reasoning. This enables agents to:

- **Understand natural language** task descriptions
- **Plan execution** paths dynamically  
- **Reason** about problems and solutions
- **Generate** text and structured tasks

## Supported Models

### Current Setup (Your Devices)

| Model | Size | Use Case | Speed |
|-------|------|----------|-------|
| **Phi** (llm_a) | 1.7GB | Fast reasoning, lightweight | ⚡ Fast |
| **Qwen** (llm_b) | 4.4GB | Complex tasks, better quality | ⚡ Medium |

Both run locally on your Raspberry Pi using **llama.cpp** with zero cloud costs.

## Supported Providers

- `llama_cpp` (local GGUF models)
- `ollama` (local/remote Ollama endpoint)
- `openai` (OpenAI-compatible chat completions)
- `anthropic` (Anthropic Messages API)

## Installation & Setup

### Prerequisites

✅ Already have on your system:
- llama.cpp compiled at `~/llama.cpp/`
- Models at `~/local_llms/models/{llm_a,llm_b}/`
- Python 3.13+

### No additional installation needed!

The LLM module uses your existing llama.cpp setup. Just ensure:

```bash
# Verify llama.cpp is built
ls ~/llama.cpp/build/bin/llama-completion

# Verify models exist
ls ~/local_llms/models/llm_a/model.gguf
ls ~/local_llms/models/llm_b/model.gguf
```

## Usage

### Basic Usage

```python
from mind.cognition import init_llm, get_default_llm

# Initialize with Phi (fast)
llm = init_llm(model="phi")

# Or Qwen (better reasoning)
llm = init_llm(model="qwen")

# Or use default
llm = get_default_llm()
```

### Generate Text

```python
prompt = "What is a multi-agent system?"
output = llm.generate(prompt, n_predict=200)
print(output)
```

### Parse Natural Language Tasks

```python
task_description = "Create a dashboard showing real-time stock prices"
task = llm.parse_task(task_description)
print(task)
# Output: {"task_type": "visualization", "goal": "...", "subtasks": [...]}
```

### Create Execution Plans

```python
agents = [
    {"name": "DatabaseAgent", "role": "fetch data"},
    {"name": "VisualizationAgent", "role": "create visuals"},
]

plan = llm.create_plan("Show stock price trends", agents)
for step in plan:
    print(step)
```

### Reasoning About Problems

```python
reasoning = llm.reasoning("How can we optimize database queries?")
print(reasoning)
```

## Configuration

Control behavior via environment variables:

```bash
# Choose model
export MIND_LLM_MODEL=phi          # or "qwen"
export MIND_LLM_PROVIDER=llama_cpp

# Custom paths (optional)
export MIND_LLAMA_BIN=/custom/path/llama-completion
export MIND_MODELS_DIR=/custom/path/models

# Then run your app
python your_app.py
```

### Cloud/API provider configuration

```bash
# OpenAI-compatible
export MIND_LLM_PROVIDER=openai
export MIND_LLM_MODEL=gpt-4o-mini
export MIND_OPENAI_API_KEY=<your_key>
# optional
export MIND_OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic
export MIND_LLM_PROVIDER=anthropic
export MIND_LLM_MODEL=claude-3-5-sonnet-latest
export MIND_ANTHROPIC_API_KEY=<your_key>
# optional
export MIND_ANTHROPIC_BASE_URL=https://api.anthropic.com

# Ollama
export MIND_LLM_PROVIDER=ollama
export MIND_LLM_MODEL=qwen2.5:7b-instruct
# optional
export MIND_OLLAMA_BASE_URL=http://localhost:11434
```

## Integration with Agents

### Making Agents LLM-Aware

```python
from mind.agents.base_agent import BaseAgent
from mind.cognition import get_default_llm

class SmartExecutor(BaseAgent):
    def __init__(self):
        super().__init__()
        self.llm = get_default_llm()
    
    def run(self, task_description: str):
        # Let LLM understand the task
        parsed_task = self.llm.parse_task(task_description)
        
        # Reason about execution
        reasoning = self.llm.reasoning(task_description)
        
        # Create execution plan
        plan = self.llm.create_plan(
            parsed_task["goal"],
            self.available_agents
        )
        
        # Execute
        result = self.execute(plan)
        
        return result
```

## Performance Tips

### For Phi (1.7GB)
- Fastest inference
- Good for task parsing and planning
- CPU-efficient on Raspberry Pi
```python
llm = init_llm(model="phi", n_threads=2)
```

### For Qwen (4.4GB)
- Better reasoning and understanding
- Use when quality matters more than speed
- Still runs on Pi, just a bit slower
```python
llm = init_llm(model="qwen", n_threads=4)
```

### Tuning Inference

```python
llm = init_llm(
    model="phi",
    n_threads=2,           # Number of CPU threads
    ctx_size=512,          # Context window (larger = more memory)
    temperature=0.7,       # Randomness (0.0-1.0)
    top_p=0.9,             # Diversity
)
```

## Architecture

```
mind/
├── cognition/
│   ├── __init__.py
│   ├── llm_interface.py      # Abstract provider interface
│   ├── llm_config.py         # Configuration & factory
│   └── providers/
│       ├── __init__.py
│       └── llama_cpp_provider.py  # llama.cpp implementation
├── agents/
│   └── base_agent.py         # Agents can use LLM now
└── ...
```

## Future Providers

The architecture supports adding more providers without modifying existing code:

```python
# Future: Add Ollama provider
from mind.cognition.providers.ollama_provider import OllamaProvider

# Future: Add Anthropic Claude
from mind.cognition.providers.anthropic_provider import AnthropicProvider

# Just instantiate and use
llm = OllamaProvider(model="mistral")
llm.generate("Hello")
```

## Troubleshooting

### "llama-completion not found"
```bash
cd ~/llama.cpp
mkdir build
cd build
cmake ..
make
```

### "Model not found"
```bash
ls ~/local_llms/models/llm_a/model.gguf
ls ~/local_llms/models/llm_b/model.gguf
```

### Slow inference
- Reduce `n_threads` if CPU is bottlenecked
- Reduce `ctx_size` to use less memory
- Use Phi instead of Qwen for speed
- Check if other processes are consuming CPU

## Cost Analysis

| Setup | Cost | Notes |
|-------|------|-------|
| **Local (current)** | $0/month | Runs on Raspberry Pi |
| **Ollama Cloud** | $0-5/month | Optional cloud inference |
| **API-based** | $50+/month | Anthropic, OpenAI, etc. |

**Your current setup is the most cost-effective!**

## Examples

See [examples/llm_usage_example.py](../examples/llm_usage_example.py) for complete working examples.

## Contributing

To add a new LLM provider:

1. Create `src/mind/cognition/providers/your_provider.py`
2. Implement `LLMProvider` interface
3. Update `src/mind/cognition/llm_config.py` factory
4. Add tests and docs

## Model Selection Benchmark

Use the benchmark matrix before choosing a final production model:

- Guide: [LLM Selection Matrix](./LLM_SELECTION_MATRIX.md)
- Cases: `benchmarks/animation_studio_cases.json`
- Rubric: `benchmarks/scoring_rubric.json`
- Runner: `scripts/benchmark_llm_matrix.py`
