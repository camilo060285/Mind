# Phi Encoder Diagnosis

## Baseline
- Cases: 10
- JSON validity: 0.0%
- Schema compliance: 0.0%
- Canon consistency: 0.0%
- Conflict extraction: 0.0%
- Hallucinated character count: 0
- Invocation timeout rate: 100.0%
- Invocation error rate: 0.0%

## Failure Pattern
- Primary issue: runtime invocation instability -> fix serving/runtime before interpreting quality metrics.
- Primary issue: JSON/schema reliability -> tighten prompt + add strict repair layer.
- Primary issue: canon drift/hallucination -> add RAG with canon + schema snippets.
- Primary issue: weak abstraction/conflict extraction -> consider curated fine-tuning set.
- Cloud integration is premature; keep local-only until thresholds are met.

## Next Iteration Order
1. Prompt hardening (`encoder/phi_prompt_v2.txt`).
2. RAG injection with canon and schema references.
3. Optional fine-tuning only if instability persists after steps 1-2.
