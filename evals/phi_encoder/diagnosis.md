# Phi Encoder Diagnosis

## Baseline
- Cases: 20
- JSON validity: 0.0%
- Schema compliance: 0.0%
- Canon consistency: 0.0%
- Conflict extraction: 0.0%
- Hallucinated character count: 0

## Primary Root Cause (Current Run)
- The dominant failure is runtime timeout during local `llama-completion` invocation on every case.
- Because generation timed out, downstream checks (JSON/schema/canon/conflict) all scored 0 by cascade.
- This baseline is still valuable: it proves a reliability blocker before cloud integration.

## Interpretation
- This run does **not** yet prove canon weakness or hallucination behavior.
- It primarily proves that encoder runtime/serving configuration must be stabilized first.

## Immediate Fix Order
1. Reduce prompt payload and retrieval context size per case.
2. Lower generation budget for encoder mode (`n_predict`, deterministic decoding).
3. Add strict repair layer after generation (if text is partially malformed JSON).
4. Re-run same 20-case harness and compare deltas.

## Cloud Decision
Cloud integration remains premature until local runtime produces non-timeout outputs and then meets quality thresholds.
