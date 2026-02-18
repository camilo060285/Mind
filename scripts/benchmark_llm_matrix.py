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
import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from mind.cognition import get_llm_provider
from mind.latent.contracts import validate_latent_payload


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


def generate_output(
    spec: ModelSpec,
    prompt: str,
    custom_command_template: str | None,
) -> str:
    if spec.provider == "custom":
        if not custom_command_template:
            raise BenchmarkError("custom provider requires --custom-command-template")
        return run_custom_command(custom_command_template, spec.model, prompt)

    provider: Any = get_llm_provider(provider=spec.provider, model=spec.model)
    return provider.generate(prompt, n_predict=700)


def evaluate_case(
    spec: ModelSpec,
    case: dict[str, Any],
    custom_command_template: str | None,
) -> dict[str, Any]:
    start = time.perf_counter()
    output = generate_output(spec, case["prompt"], custom_command_template)
    latency = time.perf_counter() - start

    required_keywords = case.get("required_keywords", [])
    coverage = keyword_coverage(output, required_keywords)

    schema_adherence = 0.0
    json_valid = False
    if case.get("expects_json", False):
        try:
            parsed = json.loads(output)
            json_valid, errors = validate_latent_payload(parsed)
            schema_adherence = 1.0 if json_valid else 0.0
            schema_notes = [] if json_valid else errors
        except json.JSONDecodeError:
            schema_notes = ["Output is not valid JSON"]
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
    for key, weight in weights.items():
        value = metrics.get(key)
        if value is None:
            continue
        total += float(value) * weight
    return total


def aggregate_model_score(
    case_results: list[dict[str, Any]],
    weights: dict[str, float],
) -> dict[str, Any]:
    scored_cases: list[dict[str, Any]] = []
    for result in case_results:
        auto_score = weighted_score(result["metrics"], weights)
        scored_cases.append({**result, "auto_weighted_score": round(auto_score, 4)})

    avg_score = 0.0
    if scored_cases:
        total = sum(cast(float, item["auto_weighted_score"]) for item in scored_cases)
        avg_score = total / len(scored_cases)
    return {
        "cases": scored_cases,
        "auto_average_score": round(avg_score, 4),
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
            result = evaluate_case(spec, case, args.custom_command_template)
            case_results.append(result)

        matrix["results"][raw_model] = aggregate_model_score(case_results, weights)

    ranking = sorted(
        (
            {
                "model": model_name,
                "auto_average_score": details.get("auto_average_score", 0),
            }
            for model_name, details in matrix["results"].items()
        ),
        key=lambda item: item["auto_average_score"],
        reverse=True,
    )

    matrix["ranking"] = ranking

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(matrix, indent=2))

    print(f"Saved benchmark results to {out_path}")
    print("Ranking:")
    for item in ranking:
        print(f"- {item['model']}: {item['auto_average_score']}")


if __name__ == "__main__":
    main()
