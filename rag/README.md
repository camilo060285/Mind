# RAG Prep (Phi Encoder)

This folder prepares retrieval assets to reduce canon drift and hallucination.

## Structure
- `canon/`: character bibles, universe rules, continuity notes
- `schema_refs/`: encoder schema docs and examples

## Intended Use
1. Retrieve top-k canon and schema snippets before encoder generation.
2. Inject snippets into encoder prompt context.
3. Re-run eval harness and compare deltas.
