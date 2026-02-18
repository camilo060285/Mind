# Universal Reasoning Layer (v1)

This document defines the first implementation pass of a domain-agnostic reasoning pipeline for Mind.

## Pipeline

1. Encoder (local model, e.g., Phi) converts raw input to latent JSON.
2. Validation pass checks latent consistency and schema correctness.
3. Decoder (cloud LLM) expands latent JSON into rich final output.

## Current v1 Assets

- Core schema: `src/mind/latent/schemas/latent_core.schema.json`
- Animation extension: `src/mind/latent/schemas/animation_extension.schema.json`
- Builder/validator helpers: `src/mind/latent/contracts.py`
- Prompt templates: `src/mind/latent/prompts.py`
- Cognition hooks: `src/mind/cognition/thinking_protocol.py`

## Latent Core Contract

Core fields (required):
- `schema_version`
- `domain`
- `intent`
- `entities`
- `constraints`
- `structure`
- `style`
- `confidence`
- `source`

## Integration Plan (Mind)

### Phase 1 (implemented)
- Add latent module with schemas, prompts, and validators.
- Add cognition methods: `encode`, `validate`, `decoder_input`.

### Phase 2 (next)
- Update `MetaOrchestrator.run_blueprint` to optionally pre-encode `goal_text` into latent form.
- Pass latent payload through agent steps instead of raw text where possible.
- Store latent payloads in memory for re-use and evolution scoring.

### Phase 3 (next)
- Add domain router to pick extension schema (`animation`, `research`, `planning`, etc.).
- Add version migration utilities for latent schema evolution.

## Decoder Prompt Contract

Decoder should receive:
- `latent_payload`
- requested output format
- optional domain extension payload

Decoder must preserve constraints and structure while adding detail and stylistic quality.
