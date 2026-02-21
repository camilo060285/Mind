# Phi Encoder Diagnosis

## Baseline
- Cases: 20
- JSON validity: 100.0%
- Schema compliance: 90.0%
- Canon consistency: 60.0%
- Conflict extraction: 45.0%
- Hallucinated character count: 8
- Invocation timeout rate: 0.0%
- Invocation error rate: 0.0%

## Failure Pattern
- Primary issue: canon drift/hallucination -> add RAG with canon + schema snippets.
- Primary issue: weak abstraction/conflict extraction -> consider curated fine-tuning set.
- Cloud integration is premature; keep local-only until thresholds are met.

## Next Iteration Order
1. Prompt hardening (`encoder/phi_prompt_v2.txt`).
2. RAG injection with canon and schema references.
3. Optional fine-tuning only if instability persists after steps 1-2.
