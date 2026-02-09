"""A/B testing framework for validating improvement hypotheses."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class ExperimentStatus(Enum):
    """Status of an experiment."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ABORTED = "aborted"


@dataclass
class ExperimentVariant:
    """A variant in an A/B test."""

    name: str
    description: str
    configuration: Dict[str, Any]
    results: List[float] = field(default_factory=list)  # Performance scores


@dataclass
class Experiment:
    """An A/B testing experiment."""

    id: str
    hypothesis_id: str
    title: str
    description: str
    status: ExperimentStatus = ExperimentStatus.PENDING
    variant_a: Optional[ExperimentVariant] = None
    variant_b: Optional[ExperimentVariant] = None
    sample_size: int = 10
    samples_run: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    confidence_level: float = 0.95
    winner: Optional[str] = None


class ExperimentFramework:
    """Framework for running A/B testing experiments."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize experiment framework.

        Args:
            storage_dir: Directory to store experiments. Defaults to ~/.mind_experiments
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".mind_experiments"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.experiments_file = self.storage_dir / "experiments.jsonl"

        self.experiments: Dict[str, Experiment] = {}
        self._load_experiments()

    def _load_experiments(self) -> None:
        """Load experiments from disk."""
        if self.experiments_file.exists():
            try:
                with open(self.experiments_file, "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            variant_a = ExperimentVariant(
                                name=data["variant_a"]["name"],
                                description=data["variant_a"]["description"],
                                configuration=data["variant_a"]["configuration"],
                                results=data["variant_a"].get("results", []),
                            )
                            variant_b = ExperimentVariant(
                                name=data["variant_b"]["name"],
                                description=data["variant_b"]["description"],
                                configuration=data["variant_b"]["configuration"],
                                results=data["variant_b"].get("results", []),
                            )
                            exp = Experiment(
                                id=data["id"],
                                hypothesis_id=data["hypothesis_id"],
                                title=data["title"],
                                description=data["description"],
                                status=ExperimentStatus(data.get("status", "pending")),
                                variant_a=variant_a,
                                variant_b=variant_b,
                                sample_size=data.get("sample_size", 10),
                                samples_run=data.get("samples_run", 0),
                                created_at=data.get("created_at", ""),
                                completed_at=data.get("completed_at"),
                                confidence_level=data.get("confidence_level", 0.95),
                                winner=data.get("winner"),
                            )
                            self.experiments[exp.id] = exp
            except (json.JSONDecodeError, ValueError, KeyError):
                pass

    def _save_experiments(self) -> None:
        """Save experiments to disk."""
        with open(self.experiments_file, "w") as f:
            for exp in self.experiments.values():
                if exp.variant_a is None or exp.variant_b is None:
                    continue
                data = {
                    "id": exp.id,
                    "hypothesis_id": exp.hypothesis_id,
                    "title": exp.title,
                    "description": exp.description,
                    "status": exp.status.value,
                    "variant_a": {
                        "name": exp.variant_a.name,
                        "description": exp.variant_a.description,
                        "configuration": exp.variant_a.configuration,
                        "results": exp.variant_a.results,
                    },
                    "variant_b": {
                        "name": exp.variant_b.name,
                        "description": exp.variant_b.description,
                        "configuration": exp.variant_b.configuration,
                        "results": exp.variant_b.results,
                    },
                    "sample_size": exp.sample_size,
                    "samples_run": exp.samples_run,
                    "created_at": exp.created_at,
                    "completed_at": exp.completed_at,
                    "confidence_level": exp.confidence_level,
                    "winner": exp.winner,
                }
                f.write(json.dumps(data) + "\n")

    def create_experiment(
        self,
        hypothesis_id: str,
        title: str,
        description: str,
        variant_a_name: str,
        variant_a_config: Dict[str, Any],
        variant_b_name: str,
        variant_b_config: Dict[str, Any],
        sample_size: int = 10,
    ) -> Experiment:
        """Create a new A/B testing experiment.

        Args:
            hypothesis_id: ID of hypothesis being tested
            title: Experiment title
            description: Experiment description
            variant_a_name: Name of control variant
            variant_a_config: Configuration for variant A
            variant_b_name: Name of treatment variant
            variant_b_config: Configuration for variant B
            sample_size: Number of samples per variant

        Returns:
            Created experiment
        """
        import uuid

        exp_id = f"exp_{uuid.uuid4().hex[:6]}"

        variant_a = ExperimentVariant(
            name=variant_a_name,
            description="Control variant",
            configuration=variant_a_config,
        )
        variant_b = ExperimentVariant(
            name=variant_b_name,
            description="Treatment variant",
            configuration=variant_b_config,
        )

        exp = Experiment(
            id=exp_id,
            hypothesis_id=hypothesis_id,
            title=title,
            description=description,
            variant_a=variant_a,
            variant_b=variant_b,
            sample_size=sample_size,
        )

        self.experiments[exp_id] = exp
        self._save_experiments()
        return exp

    def get_experiment(self, exp_id: str) -> Optional[Experiment]:
        """Get experiment by ID.

        Args:
            exp_id: Experiment ID

        Returns:
            Experiment or None
        """
        return self.experiments.get(exp_id)

    def record_result(
        self, exp_id: str, variant: str, score: float
    ) -> Optional[Experiment]:
        """Record a result for an experiment variant.

        Args:
            exp_id: Experiment ID
            variant: Variant name ("A" or "B")
            score: Performance score

        Returns:
            Updated experiment or None
        """
        if exp_id not in self.experiments:
            return None

        exp = self.experiments[exp_id]
        if exp.status == ExperimentStatus.PENDING:
            exp.status = ExperimentStatus.RUNNING

        if exp.variant_a is not None and variant.upper() == "A":
            exp.variant_a.results.append(score)
        elif exp.variant_b is not None and variant.upper() == "B":
            exp.variant_b.results.append(score)

        if exp.variant_a is not None and exp.variant_b is not None:
            exp.samples_run = len(exp.variant_a.results) + len(exp.variant_b.results)

            # Check if experiment is complete
            if exp.samples_run >= exp.sample_size * 2:
                self._complete_experiment(exp)

        self._save_experiments()
        return exp

    def _complete_experiment(self, exp: Experiment) -> None:
        """Complete an experiment and determine winner.

        Args:
            exp: Experiment to complete
        """
        exp.status = ExperimentStatus.COMPLETED
        exp.completed_at = datetime.now().isoformat()

        if exp.variant_a is None or exp.variant_b is None:
            return

        if len(exp.variant_a.results) > 0 and len(exp.variant_b.results) > 0:
            avg_a = sum(exp.variant_a.results) / len(exp.variant_a.results)
            avg_b = sum(exp.variant_b.results) / len(exp.variant_b.results)

            # Determine winner (higher score is better)
            exp.winner = exp.variant_b.name if avg_b > avg_a else exp.variant_a.name

    def get_active_experiments(self) -> List[Experiment]:
        """Get currently active experiments.

        Returns:
            List of active experiments
        """
        return [
            e
            for e in self.experiments.values()
            if e.status in (ExperimentStatus.PENDING, ExperimentStatus.RUNNING)
        ]

    def get_completed_experiments(self) -> List[Experiment]:
        """Get completed experiments.

        Returns:
            List of completed experiments
        """
        return [
            e
            for e in self.experiments.values()
            if e.status == ExperimentStatus.COMPLETED
        ]

    def abort_experiment(self, exp_id: str) -> Optional[Experiment]:
        """Abort an experiment.

        Args:
            exp_id: Experiment ID

        Returns:
            Updated experiment or None
        """
        if exp_id not in self.experiments:
            return None

        exp = self.experiments[exp_id]
        exp.status = ExperimentStatus.ABORTED
        exp.completed_at = datetime.now().isoformat()

        self._save_experiments()
        return exp

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about all experiments.

        Returns:
            Statistics dictionary
        """
        exps = list(self.experiments.values())
        completed = sum(1 for e in exps if e.status == ExperimentStatus.COMPLETED)
        active = sum(1 for e in exps if e.status == ExperimentStatus.RUNNING)

        return {
            "total_experiments": len(exps),
            "completed": completed,
            "active": active,
            "pending": sum(1 for e in exps if e.status == ExperimentStatus.PENDING),
            "aborted": sum(1 for e in exps if e.status == ExperimentStatus.ABORTED),
        }

    def export_results(self, filepath: str) -> None:
        """Export experiment results to file.

        Args:
            filepath: Path to export to
        """
        export_file = Path(filepath)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        results = []
        for exp in self.experiments.values():
            if exp.status == ExperimentStatus.COMPLETED:
                if exp.variant_a is None or exp.variant_b is None:
                    continue

                avg_a = (
                    sum(exp.variant_a.results) / len(exp.variant_a.results)
                    if exp.variant_a.results
                    else 0
                )
                avg_b = (
                    sum(exp.variant_b.results) / len(exp.variant_b.results)
                    if exp.variant_b.results
                    else 0
                )

                results.append(
                    {
                        "id": exp.id,
                        "title": exp.title,
                        "hypothesis_id": exp.hypothesis_id,
                        "variant_a": exp.variant_a.name,
                        "avg_a": avg_a,
                        "variant_b": exp.variant_b.name,
                        "avg_b": avg_b,
                        "winner": exp.winner,
                        "completed_at": exp.completed_at,
                    }
                )

        with open(export_file, "w") as f:
            json.dump(results, f, indent=2)
