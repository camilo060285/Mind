# LLM Selection Matrix for Mind + 2D Animation Studio

This guide helps choose the best LLM stack for story/script generation, prompt-pack creation, and consistent studio outputs.

## Why This Exists

Do not choose by intuition. Choose by benchmark evidence across your real workflow.

## Decision Strategy (Recommended)

Use a hybrid stack:
1. **Local encoder model** for latent structuring and cost control.
2. **Cloud (or stronger local) decoder model** for script richness and nuance.
3. **Image model + LoRA pipeline** for visual identity consistency.

## Baseline Candidates

- `llama_cpp:phi` (fast, cheap local baseline)
- `llama_cpp:qwen` (stronger local reasoning)
- `custom:<name>` (external API or hosted model using command template)

## Benchmark Assets

- Cases: `benchmarks/animation_studio_cases.json`
- Rubric: `benchmarks/scoring_rubric.json`
- Runner: `scripts/benchmark_llm_matrix.py`
- Results output (default): `benchmarks/results_latest.json`

## Run the Matrix

```bash
python scripts/benchmark_llm_matrix.py \
  --models llama_cpp:phi llama_cpp:qwen \
  --cases benchmarks/animation_studio_cases.json \
  --rubric benchmarks/scoring_rubric.json \
  --out benchmarks/results_latest.json
```

Direct provider A/B examples:

```bash
# OpenAI vs Anthropic (requires both API keys configured in env)
python scripts/benchmark_llm_matrix.py \
  --models openai:gpt-4o-mini anthropic:claude-3-5-sonnet-latest \
  --cases benchmarks/animation_studio_cases.json \
  --rubric benchmarks/scoring_rubric.json \
  --out benchmarks/results_cloud_ab.json

# Ollama local baseline
python scripts/benchmark_llm_matrix.py \
  --models ollama:qwen2.5:7b-instruct ollama:llama3.1:8b-instruct \
  --cases benchmarks/animation_studio_cases.json \
  --rubric benchmarks/scoring_rubric.json \
  --out benchmarks/results_ollama_ab.json
```

If you want to compare an API model before writing a dedicated provider:

```bash
python scripts/benchmark_llm_matrix.py \
  --models custom:gpt_like \
  --custom-command-template "your_cli --model {model} --prompt {prompt}" \
  --cases benchmarks/animation_studio_cases.json
```

## Scoring Logic

Weighted criteria from `benchmarks/scoring_rubric.json`:
- schema adherence
- instruction following
- character consistency
- script quality
- latency
- cost

The runner computes automatic metrics for:
- schema adherence (JSON/latent validation)
- instruction following (keyword coverage)
- latency

Human-in-the-loop scores should be added for:
- character consistency
- script quality
- cost realism for API usage

## Final Selection Rule

Pick winner only after:
1. At least 3 benchmark runs on different days/topics.
2. No major failures in encoder JSON validity.
3. Character voice remains stable across script + prompt-pack tasks.
4. Cost/latency fit your weekly production budget.

## Autonomy Readiness Rule

Before enabling semi-autonomous production loops, require:
- average benchmark score above your threshold (example: 0.75),
- zero critical schema failures in last 10 runs,
- stable character consistency review from human checks.
