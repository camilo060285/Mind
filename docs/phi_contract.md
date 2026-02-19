# Phi Encoder Contract

## Purpose
Phi is the local encoder for Mind. Its responsibility is to transform messy user input into stable, schema-valid latent JSON that downstream agents can trust.

## Required Responsibilities
- Convert ambiguous natural language into structured JSON.
- Preserve canon and continuity from provided context.
- Normalize names, entities, constraints, and rules.
- Extract beats, entities, goals, and conflicts.
- Avoid invention unless `allow_invention=true` is explicitly provided.
- Return schema-valid JSON only (no markdown, no prose wrappers).

## Output Guarantees
- Always produce valid JSON object output.
- Must include all required schema fields.
- Missing unknown values must be explicit `null`, not omitted.
- Include at least one conflict when conflict is implied or explicit.
- Must not add unapproved characters, events, or world facts.

## Failure Semantics
When uncertain, Phi must:
- keep structure valid,
- set uncertain fields to `null`,
- add uncertainty signals in `unresolved`.

## Evaluation Thresholds (Gate for cloud shadow mode)
- JSON validity: >= 90%
- Schema compliance: >= 80%
- Canon consistency: >= 80%
- Hallucinated characters: 0
- Conflict extraction: >= 80%

Only after these thresholds are met should cloud shadow mode (5-10% traffic) be considered.
