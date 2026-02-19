"""Provider-agnostic benchmark matrix for choosing Mind/Studio LLMs.

Usage examples:
  python scripts/benchmark_llm_matrix.py \
    --models llama_cpp:phi llama_cpp:qwen \
    --cases benchmarks/animation_studio_cases.json \
    --rubric benchmarks/scoring_rubric.json \
    --out benchmarks/results_latest.json

  python scripts/benchmark_llm_matrix.py \
    --models custom:my_model \
    --custom-command-template "my_cli --model {model} --prompt {prompt}" \
    --cases benchmarks/animation_studio_cases.json
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from mind.cognition import get_llm_provider
from mind.latent.contracts import build_latent_payload, validate_latent_payload


@dataclass
class ModelSpec:
    provider: str
    model: str


class BenchmarkError(RuntimeError):
    """Raised when benchmark input or execution fails."""


def parse_model_spec(raw: str) -> ModelSpec:
    if ":" not in raw:
        raise BenchmarkError(
            f"Invalid model spec '{raw}'. Expected '<provider>:<model>'"
        )
    provider, model = raw.split(":", 1)
    return ModelSpec(provider=provider.strip(), model=model.strip())


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise BenchmarkError(f"File not found: {path}")
    return json.loads(path.read_text())


def keyword_coverage(output: str, keywords: list[str]) -> float:
    if not keywords:
        return 1.0
    lowered = output.lower()
    hits = sum(1 for key in keywords if key.lower() in lowered)
    return hits / len(keywords)


def latency_to_score(seconds: float) -> float:
    if seconds <= 2:
        return 10.0
    if seconds <= 5:
        return 8.0
    if seconds <= 10:
        return 6.0
    if seconds <= 20:
        return 4.0
    return 2.0


def run_custom_command(template: str, model: str, prompt: str) -> str:
    command = template.format(model=model, prompt=shlex.quote(prompt))
    proc = subprocess.run(command, shell=True, capture_output=True, text=True)
    if proc.returncode != 0:
        raise BenchmarkError(f"Custom command failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def shape_prompt(case: dict[str, Any]) -> str:
    """Apply lightweight prompt shaping for stricter benchmark outputs."""
    prompt = str(case.get("prompt", "")).strip()

    if case.get("expects_json", False):
        prompt += (
            "\n\nOutput requirements: return valid JSON only. "
            "No markdown. No explanations."
        )

    return prompt


def try_parse_json(text: str) -> dict[str, Any] | None:
    """Try strict and salvaged JSON parsing from model output."""
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return cast(dict[str, Any], parsed)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None

    candidate = match.group(0).strip()
    try:
        parsed = json.loads(candidate)
        if isinstance(parsed, dict):
            return cast(dict[str, Any], parsed)
    except json.JSONDecodeError:
        pass

    return None


def build_encoder_fallback(case: dict[str, Any], output: str) -> dict[str, Any]:
    """Build deterministic fallback latent payload when JSON cannot be recovered."""
    domain = str(case.get("domain", "general"))
    raw_input = f"{case.get('prompt', '')}\nMODEL_OUTPUT:\n{output[:500]}"
    return build_latent_payload(raw_input=raw_input, domain=domain)


def generate_output(
    spec: ModelSpec,
    prompt: str,
    custom_command_template: str | None,
    n_predict: int,
    provider_timeout: int,
) -> str:
    if spec.provider == "custom":
        if not custom_command_template:
            raise BenchmarkError("custom provider requires --custom-command-template")
        return run_custom_command(custom_command_template, spec.model, prompt)

    provider: Any = get_llm_provider(provider=spec.provider, model=spec.model)
    return provider.generate(prompt, n_predict=n_predict, timeout=provider_timeout)


def evaluate_case(
    spec: ModelSpec,
    case: dict[str, Any],
    custom_command_template: str | None,
    n_predict: int,
    provider_timeout: int,
) -> dict[str, Any]:
    start = time.perf_counter()
    prompt = shape_prompt(case)
    output = generate_output(
        spec,
        prompt,
        custom_command_template,
        n_predict,
        provider_timeout,
    )
    latency = time.perf_counter() - start

    required_keywords = case.get("required_keywords", [])
    coverage = keyword_coverage(output, required_keywords)

    schema_adherence = 0.0
    json_valid = False
    if case.get("expects_json", False):
        parsed = try_parse_json(output)
        if parsed is not None:
            json_valid, errors = validate_latent_payload(parsed)
            schema_adherence = 1.0 if json_valid else 0.0
            schema_notes = [] if json_valid else errors
        else:
            schema_notes = ["Output is not valid JSON"]

        if not json_valid:
            repair_prompt = (
                "Repair the following output into valid JSON for the latent schema. "
                "Return JSON only with keys: schema_version, domain, intent, entities, "
                "constraints, structure, style, confidence, source.\n\n"
                f"Original output:\n{output}"
            )
            try:
                repaired = generate_output(
                    spec,
                    repair_prompt,
                    custom_command_template,
                    n_predict,
                    provider_timeout,
                )
                parsed = try_parse_json(repaired)
                if parsed is None:
                    raise ValueError("Repair output is not parseable JSON")

                json_valid, errors = validate_latent_payload(parsed)
                if json_valid:
                    output = repaired
                    schema_adherence = 1.0
                    schema_notes = ["repaired_json_success"]
                else:
                    schema_notes = ["repair_failed"] + errors
            except Exception as exc:  # pylint: disable=broad-except
                schema_notes.append(f"repair_error: {exc}")

        if not json_valid:
            fallback_payload = build_encoder_fallback(case, output)
            fallback_valid, fallback_errors = validate_latent_payload(fallback_payload)
            if fallback_valid:
                json_valid = True
                schema_adherence = 1.0
                output = json.dumps(fallback_payload)
                schema_notes.append("fallback_payload_built")
            else:
                schema_notes.append(f"fallback_failed: {fallback_errors}")
    else:
        schema_adherence = 1.0
        schema_notes = []

    metrics: dict[str, float | None] = {
        "schema_adherence": schema_adherence,
        "instruction_following": coverage,
        "character_consistency": None,
        "script_quality": None,
        "latency": latency_to_score(latency) / 10,
        "cost": None,
    }

    return {
        "case_id": case["id"],
        "task_type": case.get("task_type"),
        "latency_seconds": round(latency, 3),
        "keyword_coverage": round(coverage, 3),
        "expects_json": bool(case.get("expects_json", False)),
        "json_valid": json_valid,
        "schema_notes": schema_notes,
        "metrics": metrics,
        "output_preview": output[:500],
    }


def weighted_score(metrics: dict[str, Any], weights: dict[str, float]) -> float:
    total = 0.0
    active_weight = 0.0
    for key, weight in weights.items():
        value = metrics.get(key)
        if value is None:
            continue
        total += float(value) * weight
        active_weight += weight

    if active_weight == 0:
        return 0.0
    return total


def normalized_weighted_score(
    metrics: dict[str, Any],
    weights: dict[str, float],
) -> float:
    raw_total = 0.0
    active_weight = 0.0
    for key, weight in weights.items():
        value = metrics.get(key)
        if value is None:
            continue
        raw_total += float(value) * weight
        active_weight += weight

    if active_weight == 0:
        return 0.0
    return raw_total / active_weight


def aggregate_model_score(
    case_results: list[dict[str, Any]],
    weights: dict[str, float],
) -> dict[str, Any]:
    scored_cases: list[dict[str, Any]] = []
    for result in case_results:
        auto_score = weighted_score(result["metrics"], weights)
        normalized_score = normalized_weighted_score(result["metrics"], weights)
        scored_cases.append(
            {
                **result,
                "auto_weighted_score": round(auto_score, 4),
                "auto_weighted_score_normalized": round(normalized_score, 4),
            }
        )

    avg_score = 0.0
    avg_normalized_score = 0.0
    if scored_cases:
        total = sum(cast(float, item["auto_weighted_score"]) for item in scored_cases)
        total_normalized = sum(
            cast(float, item["auto_weighted_score_normalized"]) for item in scored_cases
        )
        avg_score = total / len(scored_cases)
        avg_normalized_score = total_normalized / len(scored_cases)
    return {
        "cases": scored_cases,
        "auto_average_score": round(avg_score, 4),
        "auto_average_score_normalized": round(avg_normalized_score, 4),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run LLM benchmark matrix for Mind.")
    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        help="Model specs in '<provider>:<model>' format",
    )
    parser.add_argument(
        "--cases",
        default="benchmarks/animation_studio_cases.json",
        help="Path to benchmark cases JSON",
    )
    parser.add_argument(
        "--rubric",
        default="benchmarks/scoring_rubric.json",
        help="Path to scoring rubric JSON",
    )
    parser.add_argument(
        "--out",
        default="benchmarks/results_latest.json",
        help="Output path for benchmark results",
    )
    parser.add_argument(
        "--custom-command-template",
        default=None,
        help=(
            "Shell command template for custom provider. "
            "Use {model} and {prompt} placeholders."
        ),
    )
    parser.add_argument(
        "--n-predict",
        type=int,
        default=240,
        help="Tokens to request per case (lower values are faster on local models).",
    )
    parser.add_argument(
        "--provider-timeout",
        type=int,
        default=300,
        help="Per-case timeout in seconds for provider.generate calls.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    cases_data = load_json(Path(args.cases))
    rubric_data = load_json(Path(args.rubric))
    weights: dict[str, float] = rubric_data.get("weights", {})

    cases = cases_data.get("cases", [])
    if not cases:
        raise BenchmarkError("No benchmark cases found.")

    matrix: dict[str, Any] = {
        "cases_file": args.cases,
        "rubric_file": args.rubric,
        "results": {},
    }

    for raw_model in args.models:
        spec = parse_model_spec(raw_model)
        case_results: list[dict[str, Any]] = []

        for case in cases:
            try:
                result = evaluate_case(
                    spec,
                    case,
                    args.custom_command_template,
                    args.n_predict,
                    args.provider_timeout,
                )
            except Exception as exc:  # pylint: disable=broad-except
                result = {
                    "case_id": case.get("id", "unknown"),
                    "task_type": case.get("task_type"),
                    "latency_seconds": 0,
                    "keyword_coverage": 0,
                    "expects_json": bool(case.get("expects_json", False)),
                    "json_valid": False,
                    "schema_notes": [f"execution_error: {exc}"],
                    "metrics": {
                        "schema_adherence": 0.0,
                        "instruction_following": 0.0,
                        "character_consistency": None,
                        "script_quality": None,
                        "latency": 0.0,
                        "cost": None,
                    },
                    "output_preview": "",
                    "auto_weighted_score": 0.0,
                    "auto_weighted_score_normalized": 0.0,
                }
            case_results.append(result)

        matrix["results"][raw_model] = aggregate_model_score(case_results, weights)

    ranking = sorted(
        (
            {
                "model": model_name,
                "auto_average_score": details.get("auto_average_score", 0),
                "auto_average_score_normalized": details.get(
                    "auto_average_score_normalized", 0
                ),
            }
            for model_name, details in matrix["results"].items()
        ),
        key=lambda item: item["auto_average_score_normalized"],
        reverse=True,
    )

    matrix["ranking"] = ranking

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(matrix, indent=2))

    print(f"Saved benchmark results to {out_path}")
    print("Ranking:")
    for item in ranking:
        print(
            "- "
            f"{item['model']}: raw={item['auto_average_score']} "
            f"normalized={item['auto_average_score_normalized']}"
        )


if __name__ == "__main__":
    main()
