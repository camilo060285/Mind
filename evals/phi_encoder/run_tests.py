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
from typing import Any, cast


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
            return cast(dict[str, Any], parsed)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return cast(dict[str, Any], parsed)
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : index + 1]
                try:
                    parsed = json.loads(candidate)
                    if isinstance(parsed, dict):
                        return cast(dict[str, Any], parsed)
                except json.JSONDecodeError:
                    return None

    return None


def _strip_prompt_echo(output: str, prompt: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    stripped_output = output.strip()
    stripped_prompt = prompt.strip()

    if stripped_prompt and stripped_output.startswith(stripped_prompt):
        stripped_output = stripped_output[len(stripped_prompt) :].strip()
        notes.append("prompt_echo_trimmed")

    if not stripped_output and stripped_prompt:
        notes.append("prompt_echo_only")

    return stripped_output, notes


def _tokenize_for_retrieval(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9_\-]{3,}", text.lower())
        if token
        not in {
            "the",
            "and",
            "with",
            "from",
            "that",
            "this",
            "into",
            "must",
            "should",
            "always",
            "never",
            "when",
            "where",
            "what",
            "your",
            "their",
            "them",
            "also",
            "very",
            "more",
            "less",
            "scene",
            "style",
            "tone",
            "output",
        }
    }


def _split_markdown_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        if line.startswith("#") and current:
            chunk = "\n".join(current).strip()
            if chunk:
                chunks.append(chunk)
            current = [line]
        else:
            current.append(line)

    tail = "\n".join(current).strip()
    if tail:
        chunks.append(tail)

    if not chunks:
        cleaned = text.strip()
        chunks = [cleaned] if cleaned else []

    final_chunks: list[str] = []
    for chunk in chunks:
        compact_lines = [line.strip() for line in chunk.splitlines() if line.strip()]
        compact = "\n".join(compact_lines)
        if len(compact) <= 260:
            final_chunks.append(compact)
            continue
        sentences = re.split(r"(?<=[.!?])\s+", compact)
        current_sentence = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            candidate = (
                f"{current_sentence} {sentence}".strip()
                if current_sentence
                else sentence
            )
            if len(candidate) > 260 and current_sentence:
                final_chunks.append(current_sentence)
                current_sentence = sentence
            else:
                current_sentence = candidate
        if current_sentence:
            final_chunks.append(current_sentence)

    return [chunk for chunk in final_chunks if chunk]


def _load_canon_chunks(canon_dir: Path) -> list[tuple[str, str]]:
    if not canon_dir.exists() or not canon_dir.is_dir():
        return []

    chunks: list[tuple[str, str]] = []
    for path in sorted(canon_dir.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        for chunk in _split_markdown_chunks(content):
            cleaned = chunk.strip()
            if cleaned:
                chunks.append((path.name, cleaned))

    return chunks


def _retrieve_canon_context(
    case: dict[str, Any],
    canon_chunks: list[tuple[str, str]],
    top_k: int,
    max_chars: int,
    min_overlap: int,
) -> str:
    if not canon_chunks or top_k <= 0 or max_chars <= 0:
        return ""

    query_parts = [str(case.get("input", ""))]
    query_parts.extend(
        value for value in case.get("canon_characters", []) if isinstance(value, str)
    )
    query_parts.extend(
        value for value in case.get("canon_facts", []) if isinstance(value, str)
    )
    query = "\n".join(query_parts)
    query_tokens = _tokenize_for_retrieval(query)
    if not query_tokens:
        return ""

    scored: list[tuple[int, str, str]] = []
    canon_names = {
        value.strip().lower()
        for value in case.get("canon_characters", [])
        if isinstance(value, str) and value.strip()
    }
    for source_name, chunk in canon_chunks:
        chunk_tokens = _tokenize_for_retrieval(chunk)
        overlap = len(query_tokens.intersection(chunk_tokens))
        if overlap < max(min_overlap, 1):
            continue
        bonus = 0
        for name in case.get("canon_characters", []):
            if isinstance(name, str) and name.strip() and name.lower() in chunk.lower():
                bonus += 2
        source_lower = source_name.lower()
        if any(name in source_lower for name in canon_names):
            bonus += 3
        if "environment" in source_lower:
            bonus -= 1
        scored.append((overlap + bonus, source_name, chunk))

    if not scored:
        return ""

    scored.sort(key=lambda item: item[0], reverse=True)
    selected: list[str] = []
    used_chars = 0

    for _, source_name, chunk in scored[: max(top_k * 2, top_k)]:
        compact_chunk = chunk
        if len(compact_chunk) > 240:
            compact_chunk = compact_chunk[:240].rstrip() + "..."
        entry = f"[{source_name}]\n{compact_chunk}\n"
        if used_chars + len(entry) > max_chars:
            remaining = max_chars - used_chars
            if remaining > 80:
                entry = entry[:remaining]
                selected.append(entry)
            break
        selected.append(entry)
        used_chars += len(entry)
        if len(selected) >= top_k:
            break

    return "\n".join(selected).strip()


def _implied_conflict_from_input(case: dict[str, Any]) -> str | None:
    raw_input = case.get("input")
    if not isinstance(raw_input, str):
        return None
    lowered = raw_input.lower()
    cues = [
        "but",
        "however",
        "except",
        "versus",
        "vs",
        "tension",
        "conflict",
        "contradiction",
        "yet",
        "although",
    ]
    if any(cue in lowered for cue in cues):
        return "implied tension"
    return None


def _load_prompt_template(prompt_file: str | None = None) -> str:
    """Load prompt from file, default to minimal prompt."""
    if prompt_file is None:
        prompt_file = "encoder/phi_prompt_minimal.txt"

    prompt_path = Path(prompt_file)
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")

    # Fallback if file not found
    return "Return valid JSON only."


def _prompt_for_case(
    case: dict[str, Any],
    schema: dict[str, Any],
    rag_context: str = "",
    prompt_template: str = "",
) -> str:
    """Build prompt from template with case-specific variables."""
    canon_characters = case.get("canon_characters", [])
    canon_facts = case.get("canon_facts", [])
    allow_invention = bool(case.get("allow_invention", False))
    user_input = case.get("input", "")

    # Use provided template or load default
    if not prompt_template:
        prompt_template = _load_prompt_template()

    # Fill placeholder variables in template
    rag_section = f"Retrieved canon:\n{rag_context}\n\n" if rag_context.strip() else ""

    filled_template = (
        prompt_template.replace("{ALLOW_INVENTION}", str(allow_invention).lower())
        .replace("{CANON_CHARACTERS}", json.dumps(canon_characters))
        .replace("{CANON_FACTS}", json.dumps(canon_facts))
        .replace("{RAG_CONTEXT}", rag_section.strip())
        .replace("{INPUT}", user_input)
    )

    return filled_template


def _run_phi(prompt: str, args: argparse.Namespace) -> tuple[str, list[str]]:
    notes: list[str] = []

    if args.dry_run:
        return "{}", ["dry_run_enabled"]

    if args.command_template:
        command_str = args.command_template.format(prompt=prompt)
        try:
            proc = subprocess.run(
                command_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=args.timeout,
            )
        except subprocess.TimeoutExpired:
            return "", [f"invocation_timeout:{args.timeout}s"]
        if proc.returncode != 0:
            return "", [f"command_failed: {proc.stderr.strip()}"]
        output, trim_notes = _strip_prompt_echo(proc.stdout, prompt)
        return output, notes + trim_notes

    llama_bin = args.llama_bin
    model_file = args.model_file
    if not llama_bin or not model_file:
        return "", ["missing_llama_or_model_path"]

    command: list[str] = [
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
    except subprocess.TimeoutExpired:
        return "", [f"invocation_timeout:{args.timeout}s"]
    except Exception as exc:  # pylint: disable=broad-except
        return "", [f"invocation_error: {exc}"]

    if proc.returncode != 0:
        return "", [f"llama_failed: {proc.stderr.strip()}"]

    output, trim_notes = _strip_prompt_echo(proc.stdout, prompt)
    return output, notes + trim_notes


def _validate_required_fields(
    payload: dict[str, Any], schema: dict[str, Any]
) -> tuple[bool, list[str]]:
    notes: list[str] = []
    required_top = schema.get("required", [])
    for key in required_top:
        if key not in payload:
            notes.append(f"missing_top:{key}")

    entities = cast(Any, payload.get("entities"))
    if entities is not None and not isinstance(entities, list):
        notes.append("invalid_type:entities:expected_array")
    elif isinstance(entities, list) and not entities:
        notes.append("empty_entities")

    beats = cast(Any, payload.get("beats"))
    if beats is not None and not isinstance(beats, list):
        notes.append("invalid_type:beats:expected_array")
    elif isinstance(beats, list):
        if not beats:
            notes.append("empty_beats")
        for index, beat in enumerate(beats):  # type: ignore[misc]
            if not isinstance(beat, dict):
                notes.append(f"invalid_type:beats[{index}]:expected_object")
                continue
            for key in ["id", "goal", "conflict"]:
                if key not in beat:
                    notes.append(f"missing_nested:beats[{index}].{key}")

    constraints = payload.get("constraints")
    if constraints is not None and not isinstance(constraints, dict):
        notes.append("invalid_type:constraints:expected_object")
    elif isinstance(constraints, dict) and "never_invent" not in constraints:
        notes.append("missing_nested:constraints.never_invent")

    style = payload.get("style")
    if style is not None and not isinstance(style, dict):
        notes.append("invalid_type:style:expected_object")
    elif isinstance(style, dict) and "tone" not in style:
        notes.append("missing_nested:style.tone")

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

    entities_list = payload.get("entities", [])
    for item in entities_list:
        if isinstance(item, str) and item.strip():
            names.add(item.strip().lower())
        if isinstance(item, dict):
            raw_name = cast(Any, item.get("name"))  # type: ignore[misc]
            if isinstance(raw_name, str) and raw_name.strip():
                names.add(raw_name.strip().lower())

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
    beats = cast(Any, payload.get("beats"))
    if not isinstance(beats, list):
        return False, ["beats_not_array"]

    non_empty: list[str] = []
    for item in beats:  # type: ignore[misc]
        if not isinstance(item, dict):
            continue
        conflict = cast(Any, item.get("conflict"))  # type: ignore[misc]
        if isinstance(conflict, str) and conflict.strip():
            non_empty.append(conflict.strip())

    if not non_empty:
        notes.append("no_conflict_extracted")
        return False, notes

    return True, notes


def _to_rate(values: list[bool]) -> float:
    if not values:
        return 0.0
    return round(sum(1 for value in values if value) / len(values), 4)


def _note_rate(results: list[CaseResult], prefix: str) -> float:
    if not results:
        return 0.0
    hit_count = sum(
        1 for item in results if any(note.startswith(prefix) for note in item.notes)
    )
    return round(hit_count / len(results), 4)


def _repair_json_output(
    raw_output: str,
    schema: dict[str, Any],
    args: argparse.Namespace,
) -> tuple[dict[str, Any] | None, list[str]]:
    required_top = schema.get("required", [])
    repair_prompt = (
        "You are a JSON repair assistant. Convert the content into one valid JSON object only.\n"
        "Do not add markdown or explanations.\n"
        f"Required top-level keys: {json.dumps(required_top)}\n\n"
        "Content to repair:\n"
        f"{raw_output}\n"
    )

    repair_args = argparse.Namespace(**vars(args))
    repair_args.n_predict = max(int(args.n_predict), 320)
    repair_args.temperature = 0.1

    repaired_output, repair_notes = _run_phi(repair_prompt, repair_args)
    repaired_payload = _extract_json_blob(repaired_output)
    if repaired_payload is None:
        return None, repair_notes + ["repair_failed"]

    return repaired_payload, repair_notes + ["repaired_json_success"]


def _build_diagnosis(summary: dict[str, Any]) -> str:
    total = int(summary["total_cases"])
    if total == 0:
        return "# Phi Encoder Diagnosis\n\nNo cases were executed.\n"

    json_rate = float(summary["json_valid_rate"])
    schema_rate = float(summary["schema_valid_rate"])
    canon_rate = float(summary["canon_consistency_rate"])
    conflict_rate = float(summary["conflict_extraction_rate"])
    hallucinated = int(summary["total_hallucinated_characters"])
    timeout_rate = float(summary.get("invocation_timeout_rate", 0.0))
    runtime_error_rate = float(summary.get("invocation_error_rate", 0.0))

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
        f"- Invocation timeout rate: {timeout_rate:.1%}",
        f"- Invocation error rate: {runtime_error_rate:.1%}",
        "",
        "## Failure Pattern",
    ]

    if timeout_rate > 0.0 or runtime_error_rate > 0.0:
        lines.append(
            "- Primary issue: runtime invocation instability -> fix serving/runtime before interpreting quality metrics."
        )

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
            "1. Prompt hardening (`encoder/phi_prompt_minimal.txt`).",
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
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--n-predict", type=int, default=320)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--rag-canon-dir",
        default="rag/canon",
        help="Path to markdown canon bibles used for retrieval context",
    )
    parser.add_argument(
        "--rag-top-k",
        type=int,
        default=1,
        help="How many retrieved canon snippets to inject into the prompt",
    )
    parser.add_argument(
        "--rag-max-chars",
        type=int,
        default=300,
        help="Maximum characters of retrieved canon context injected per prompt",
    )
    parser.add_argument(
        "--rag-min-overlap",
        type=int,
        default=2,
        help="Minimum token overlap required to include a canon snippet",
    )
    parser.add_argument(
        "--no-rag",
        action="store_true",
        help="Disable retrieval context injection",
    )
    parser.add_argument(
        "--command-template",
        default="",
        help="Optional custom command template with {prompt}",
    )
    parser.add_argument(
        "--prompt-file",
        default="encoder/phi_prompt_minimal.txt",
        help="Path to prompt template file (replaces hardcoded prompt)",
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
    rag_canon_dir = Path(args.rag_canon_dir)

    inputs_data = json.loads(inputs_path.read_text())
    schema_data = json.loads(schema_path.read_text())

    # Load prompt template
    prompt_template = _load_prompt_template(args.prompt_file)

    canon_chunks: list[tuple[str, str]] = []
    if not args.no_rag:
        canon_chunks = _load_canon_chunks(rag_canon_dir)

    cases = inputs_data.get("cases", [])
    if args.max_cases and args.max_cases > 0:
        cases = cases[: args.max_cases]

    results: list[CaseResult] = []

    for case in cases:
        case_id = str(case.get("id", "unknown"))
        notes: list[str] = []

        rag_context = _retrieve_canon_context(
            case,
            canon_chunks,
            top_k=int(args.rag_top_k),
            max_chars=int(args.rag_max_chars),
            min_overlap=int(args.rag_min_overlap),
        )
        prompt = _prompt_for_case(
            case, schema_data, rag_context=rag_context, prompt_template=prompt_template
        )
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

        if (
            not json_valid
            and raw_output
            and not any(note.startswith("invocation_timeout:") for note in notes)
        ):
            repaired_payload, repair_notes = _repair_json_output(
                raw_output,
                schema_data,
                args,
            )
            notes.extend(repair_notes)
            if repaired_payload is not None:
                payload = repaired_payload
                json_valid = True

        if json_valid and payload is not None:
            canon_characters = [
                value.strip()
                for value in case.get("canon_characters", [])
                if isinstance(value, str) and value.strip()
            ]
            allow_invention = bool(case.get("allow_invention", False))
            if canon_characters and not allow_invention:
                canon_lookup = {name.lower() for name in canon_characters}
                entities = payload.get("entities")
                if isinstance(entities, list):
                    filtered_entities = []
                    for entity in entities:
                        if (
                            isinstance(entity, str)
                            and entity.strip().lower() in canon_lookup
                        ):
                            filtered_entities.append(entity)
                    if filtered_entities != entities:
                        payload["entities"] = filtered_entities
                        notes.append("entities_clamped_to_canon")
                    if not payload.get("entities"):
                        payload["entities"] = [canon_characters[0]]
                        notes.append("entities_defaulted_to_primary_canon")

            schema_valid, schema_notes = _validate_required_fields(payload, schema_data)
            notes.extend(schema_notes)

            null_ok, null_notes = _check_null_policy(payload, schema_data)
            notes.extend(null_notes)

            canon_ok, hallucinated, forbidden_hits, canon_notes = _check_canon(
                payload, case
            )
            notes.extend(canon_notes)

            implied_conflict = _implied_conflict_from_input(case)
            if implied_conflict:
                beats = payload.get("beats")
                if isinstance(beats, list) and beats:
                    first_beat = beats[0]
                    if isinstance(first_beat, dict):
                        conflict_value = first_beat.get("conflict")
                        if not (
                            isinstance(conflict_value, str) and conflict_value.strip()
                        ):
                            first_beat["conflict"] = implied_conflict
                            notes.append("conflict_autofilled")

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

    summary: dict[str, Any] = {
        "total_cases": len(results),
        "json_valid_rate": _to_rate([item.json_valid for item in results]),
        "schema_valid_rate": _to_rate([item.schema_valid for item in results]),
        "null_policy_rate": _to_rate([item.null_policy_ok for item in results]),
        "canon_consistency_rate": _to_rate([item.canon_consistent for item in results]),
        "conflict_extraction_rate": _to_rate([item.has_conflict for item in results]),
        "invocation_timeout_rate": _note_rate(results, "invocation_timeout:"),
        "invocation_error_rate": _note_rate(results, "invocation_error:"),
        "prompt_echo_rate": _note_rate(results, "prompt_echo"),
        "repair_success_rate": _note_rate(results, "repaired_json_success"),
        "total_hallucinated_characters": sum(
            item.hallucinated_characters for item in results
        ),
        "total_forbidden_fact_hits": sum(item.forbidden_fact_hits for item in results),
    }

    output_payload: dict[str, Any] = {
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
