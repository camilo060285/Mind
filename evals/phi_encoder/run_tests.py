#!/usr/bin/env python3
"""Phi encoder evaluation harness (behavior/property based).

Evaluates:
- JSON validity
- schema-required field presence
- null-fill policy for unknowns (required keys present)
- canon consistency
- hallucinated character/fact frequency
- conflict extraction coverage
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class CaseResult:
    case_id: str
    json_valid: bool
    schema_valid: bool
    null_policy_ok: bool
    canon_consistent: bool
    hallucinated_characters: int
    forbidden_fact_hits: int
    has_conflict: bool
    notes: list[str]
    output_preview: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "json_valid": self.json_valid,
            "schema_valid": self.schema_valid,
            "null_policy_ok": self.null_policy_ok,
            "canon_consistent": self.canon_consistent,
            "hallucinated_characters": self.hallucinated_characters,
            "forbidden_fact_hits": self.forbidden_fact_hits,
            "has_conflict": self.has_conflict,
            "notes": self.notes,
            "output_preview": self.output_preview,
        }


def _extract_json_blob(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        return None

    candidate = match.group(0)
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        return None

    return None


def _prompt_for_case(case: dict[str, Any], schema: dict[str, Any]) -> str:
    canon_characters = case.get("canon_characters", [])
    canon_facts = case.get("canon_facts", [])
    allow_invention = bool(case.get("allow_invention", False))
    required_top = schema.get("required", [])

    nested_required = {
        "intent": ["goal", "outcome", "audience"],
        "structure": ["form", "sections"],
        "style": ["tone", "voice", "length_hint"],
        "source": ["raw_input", "encoder"],
        "canon": ["characters", "rules"],
        "extraction": ["beats", "entities", "goals", "conflicts"],
    }

    schema_summary = (
        f"required_top_level={json.dumps(required_top)}\n"
        f"required_nested={json.dumps(nested_required)}"
    )

    return (
        "You are Phi, acting as Mind's encoder. "
        "Return exactly one JSON object and nothing else.\n\n"
        "Rules:\n"
        "1) No markdown, no prose wrappers, no code fences.\n"
        "2) Use all required fields from schema.\n"
        "3) Missing unknown values must be null (never omit required keys).\n"
        "4) Never invent characters or facts unless allow_invention=true.\n"
        "5) Extract beats, entities, goals, and conflicts.\n"
        "6) Include at least one conflict when conflict is implied.\n\n"
        f"allow_invention={str(allow_invention).lower()}\n"
        f"canon_characters={json.dumps(canon_characters)}\n"
        f"canon_facts={json.dumps(canon_facts)}\n\n"
        f"Schema summary:\n{schema_summary}\n\n"
        f"Input:\n{case.get('input', '')}\n"
    )


def _run_phi(prompt: str, args: argparse.Namespace) -> tuple[str, list[str]]:
    notes: list[str] = []

    if args.dry_run:
        return "{}", ["dry_run_enabled"]

    if args.command_template:
        command = args.command_template.format(prompt=prompt)
        proc = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
        if proc.returncode != 0:
            return "", [f"command_failed: {proc.stderr.strip()}"]
        return proc.stdout.strip(), notes

    llama_bin = args.llama_bin
    model_file = args.model_file
    if not llama_bin or not model_file:
        return "", ["missing_llama_or_model_path"]

    command = [
        llama_bin,
        "-m",
        model_file,
        "-p",
        prompt,
        "-n",
        str(args.n_predict),
        "--temp",
        str(args.temperature),
    ]

    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
    except Exception as exc:  # pylint: disable=broad-except
        return "", [f"invocation_error: {exc}"]

    if proc.returncode != 0:
        return "", [f"llama_failed: {proc.stderr.strip()}"]

    output = proc.stdout.strip()
    return output, notes


def _validate_required_fields(
    payload: dict[str, Any], schema: dict[str, Any]
) -> tuple[bool, list[str]]:
    notes: list[str] = []
    required_top = schema.get("required", [])
    for key in required_top:
        if key not in payload:
            notes.append(f"missing_top:{key}")

    nested_required = {
        "intent": ["goal", "outcome", "audience"],
        "structure": ["form", "sections"],
        "style": ["tone", "voice", "length_hint"],
        "source": ["raw_input", "encoder"],
        "canon": ["characters", "rules"],
        "extraction": ["beats", "entities", "goals", "conflicts"],
    }

    for section, required in nested_required.items():
        if section not in payload:
            continue
        value = payload.get(section)
        if value is None:
            continue
        if not isinstance(value, dict):
            notes.append(f"invalid_type:{section}:expected_object")
            continue
        for key in required:
            if key not in value:
                notes.append(f"missing_nested:{section}.{key}")

    return len(notes) == 0, notes


def _check_null_policy(
    payload: dict[str, Any], schema: dict[str, Any]
) -> tuple[bool, list[str]]:
    notes: list[str] = []
    required_top = schema.get("required", [])
    for key in required_top:
        if key not in payload:
            notes.append(f"required_key_missing:{key}")

    return len(notes) == 0, notes


def _collect_entity_names(payload: dict[str, Any]) -> set[str]:
    names: set[str] = set()

    for item in payload.get("entities", []):
        if isinstance(item, dict):
            raw_name = item.get("name")
            if isinstance(raw_name, str) and raw_name.strip():
                names.add(raw_name.strip().lower())

    extraction = payload.get("extraction")
    if isinstance(extraction, dict):
        for item in extraction.get("entities", []):
            if isinstance(item, str) and item.strip():
                names.add(item.strip().lower())

    canon = payload.get("canon")
    if isinstance(canon, dict):
        for item in canon.get("characters", []):
            if isinstance(item, str) and item.strip():
                names.add(item.strip().lower())

    return names


def _check_canon(
    payload: dict[str, Any], case: dict[str, Any]
) -> tuple[bool, int, int, list[str]]:
    notes: list[str] = []

    canon_characters = {
        value.strip().lower()
        for value in case.get("canon_characters", [])
        if isinstance(value, str) and value.strip()
    }
    allow_invention = bool(case.get("allow_invention", False))

    output_text = json.dumps(payload, ensure_ascii=False).lower()
    forbidden_hits = 0
    for fact in case.get("forbidden_facts", []):
        if (
            isinstance(fact, str)
            and fact.strip()
            and fact.strip().lower() in output_text
        ):
            forbidden_hits += 1
            notes.append(f"forbidden_fact:{fact}")

    hallucinated = 0
    if canon_characters and not allow_invention:
        found = _collect_entity_names(payload)
        unknown = sorted(name for name in found if name not in canon_characters)
        hallucinated = len(unknown)
        if unknown:
            notes.append(f"hallucinated_characters:{unknown}")

    canon_ok = forbidden_hits == 0 and hallucinated == 0
    return canon_ok, hallucinated, forbidden_hits, notes


def _check_conflict(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    notes: list[str] = []
    extraction = payload.get("extraction")
    if not isinstance(extraction, dict):
        return False, ["missing_extraction"]

    conflicts = extraction.get("conflicts")
    if not isinstance(conflicts, list):
        return False, ["conflicts_not_array"]

    non_empty = [item for item in conflicts if isinstance(item, str) and item.strip()]
    if not non_empty:
        notes.append("no_conflict_extracted")
        return False, notes

    return True, notes


def _to_rate(values: list[bool]) -> float:
    if not values:
        return 0.0
    return round(sum(1 for value in values if value) / len(values), 4)


def _build_diagnosis(summary: dict[str, Any]) -> str:
    total = int(summary["total_cases"])
    if total == 0:
        return "# Phi Encoder Diagnosis\n\nNo cases were executed.\n"

    json_rate = float(summary["json_valid_rate"])
    schema_rate = float(summary["schema_valid_rate"])
    canon_rate = float(summary["canon_consistency_rate"])
    conflict_rate = float(summary["conflict_extraction_rate"])
    hallucinated = int(summary["total_hallucinated_characters"])

    lines = [
        "# Phi Encoder Diagnosis",
        "",
        "## Baseline",
        f"- Cases: {total}",
        f"- JSON validity: {json_rate:.1%}",
        f"- Schema compliance: {schema_rate:.1%}",
        f"- Canon consistency: {canon_rate:.1%}",
        f"- Conflict extraction: {conflict_rate:.1%}",
        f"- Hallucinated character count: {hallucinated}",
        "",
        "## Failure Pattern",
    ]

    if json_rate < 0.9 or schema_rate < 0.8:
        lines.append(
            "- Primary issue: JSON/schema reliability -> tighten prompt + add strict repair layer."
        )
    if canon_rate < 0.8 or hallucinated > 0:
        lines.append(
            "- Primary issue: canon drift/hallucination -> add RAG with canon + schema snippets."
        )
    if conflict_rate < 0.8:
        lines.append(
            "- Primary issue: weak abstraction/conflict extraction -> consider curated fine-tuning set."
        )
    if (
        json_rate >= 0.9
        and schema_rate >= 0.8
        and canon_rate >= 0.8
        and conflict_rate >= 0.8
        and hallucinated == 0
    ):
        lines.append(
            "- Baseline is strong enough to consider cloud shadow mode at 5-10% traffic."
        )
    else:
        lines.append(
            "- Cloud integration is premature; keep local-only until thresholds are met."
        )

    lines.extend(
        [
            "",
            "## Next Iteration Order",
            "1. Prompt hardening (`encoder/phi_prompt_v2.txt`).",
            "2. RAG injection with canon and schema references.",
            "3. Optional fine-tuning only if instability persists after steps 1-2.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run phi encoder behavior tests")
    parser.add_argument(
        "--inputs",
        default="evals/phi_encoder/test_inputs/cases.json",
        help="Path to test input cases JSON",
    )
    parser.add_argument(
        "--schema",
        default="evals/phi_encoder/schema.json",
        help="Path to encoder output schema JSON",
    )
    parser.add_argument(
        "--out",
        default="evals/phi_encoder/results_initial.json",
        help="Output results path",
    )
    parser.add_argument(
        "--diagnosis",
        default="evals/phi_encoder/diagnosis.md",
        help="Output diagnosis markdown path",
    )
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--n-predict", type=int, default=320)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--command-template",
        default="",
        help="Optional custom command template with {prompt}",
    )

    default_llama_bin = os.getenv("MIND_LLAMA_BIN", "")
    default_models_dir = os.getenv("MIND_MODELS_DIR", "")
    default_model_file = (
        str(Path(default_models_dir) / "llm_a" / "model.gguf")
        if default_models_dir
        else ""
    )

    parser.add_argument("--llama-bin", default=default_llama_bin)
    parser.add_argument("--model-file", default=default_model_file)

    args = parser.parse_args()

    inputs_path = Path(args.inputs)
    schema_path = Path(args.schema)
    out_path = Path(args.out)
    diagnosis_path = Path(args.diagnosis)

    inputs_data = json.loads(inputs_path.read_text())
    schema_data = json.loads(schema_path.read_text())

    cases = inputs_data.get("cases", [])
    if args.max_cases and args.max_cases > 0:
        cases = cases[: args.max_cases]

    results: list[CaseResult] = []

    for case in cases:
        case_id = str(case.get("id", "unknown"))
        notes: list[str] = []

        prompt = _prompt_for_case(case, schema_data)
        raw_output, invoke_notes = _run_phi(prompt, args)
        notes.extend(invoke_notes)

        payload = _extract_json_blob(raw_output)
        json_valid = payload is not None

        schema_valid = False
        null_ok = False
        canon_ok = False
        hallucinated = 0
        forbidden_hits = 0
        has_conflict = False

        if json_valid and payload is not None:
            schema_valid, schema_notes = _validate_required_fields(payload, schema_data)
            notes.extend(schema_notes)

            null_ok, null_notes = _check_null_policy(payload, schema_data)
            notes.extend(null_notes)

            canon_ok, hallucinated, forbidden_hits, canon_notes = _check_canon(
                payload, case
            )
            notes.extend(canon_notes)

            has_conflict, conflict_notes = _check_conflict(payload)
            notes.extend(conflict_notes)
        else:
            notes.append("invalid_json")

        results.append(
            CaseResult(
                case_id=case_id,
                json_valid=json_valid,
                schema_valid=schema_valid,
                null_policy_ok=null_ok,
                canon_consistent=canon_ok,
                hallucinated_characters=hallucinated,
                forbidden_fact_hits=forbidden_hits,
                has_conflict=has_conflict,
                notes=notes,
                output_preview=raw_output[:500],
            )
        )

    summary = {
        "total_cases": len(results),
        "json_valid_rate": _to_rate([item.json_valid for item in results]),
        "schema_valid_rate": _to_rate([item.schema_valid for item in results]),
        "null_policy_rate": _to_rate([item.null_policy_ok for item in results]),
        "canon_consistency_rate": _to_rate([item.canon_consistent for item in results]),
        "conflict_extraction_rate": _to_rate([item.has_conflict for item in results]),
        "total_hallucinated_characters": sum(
            item.hallucinated_characters for item in results
        ),
        "total_forbidden_fact_hits": sum(item.forbidden_fact_hits for item in results),
    }

    output_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "phi-local",
        "inputs_file": str(inputs_path),
        "schema_file": str(schema_path),
        "summary": summary,
        "cases": [item.to_dict() for item in results],
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output_payload, indent=2))

    diagnosis_text = _build_diagnosis(summary)
    diagnosis_path.write_text(diagnosis_text)

    print(f"Wrote results: {out_path}")
    print(f"Wrote diagnosis: {diagnosis_path}")


if __name__ == "__main__":
    main()
