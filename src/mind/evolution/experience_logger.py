"""Experience logging for tracking system performance and improvements."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SystemMetrics:
    """Metrics collected during a single execution."""

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    execution_time: float = 0.0  # seconds
    goal: str = ""
    result_success: bool = False
    agents_used: int = 0
    decisions_made: int = 0
    memory_accessed: int = 0
    memory_stored: int = 0
    error_count: int = 0
    quality_score: float = 0.0  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Experience:
    """A recorded system experience with metrics and outcomes."""

    id: str
    metrics: SystemMetrics
    observations: str
    improvements: List[str] = field(default_factory=list)
    validated: bool = False
    improvement_score: float = 0.0  # 0-1 estimated improvement


class ExperienceLogger:
    """Logs system experiences and performance metrics for learning."""

    def __init__(self, storage_dir: Optional[Path] = None):
        """Initialize experience logger.

        Args:
            storage_dir: Directory to store experiences. Defaults to ~/.mind_experiences
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".mind_experiences"

        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.storage_dir / "experiences.jsonl"

        self._experiences: Dict[str, Experience] = {}
        self._load_experiences()

    def _load_experiences(self) -> None:
        """Load experiences from disk."""
        if self.log_file.exists():
            try:
                with open(self.log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            metrics = SystemMetrics(
                                timestamp=data["metrics"]["timestamp"],
                                execution_time=data["metrics"]["execution_time"],
                                goal=data["metrics"]["goal"],
                                result_success=data["metrics"]["result_success"],
                                agents_used=data["metrics"]["agents_used"],
                                decisions_made=data["metrics"]["decisions_made"],
                                memory_accessed=data["metrics"]["memory_accessed"],
                                memory_stored=data["metrics"]["memory_stored"],
                                error_count=data["metrics"]["error_count"],
                                quality_score=data["metrics"]["quality_score"],
                                metadata=data["metrics"].get("metadata", {}),
                            )
                            exp = Experience(
                                id=data["id"],
                                metrics=metrics,
                                observations=data["observations"],
                                improvements=data.get("improvements", []),
                                validated=data.get("validated", False),
                                improvement_score=data.get("improvement_score", 0.0),
                            )
                            self._experiences[exp.id] = exp
            except (json.JSONDecodeError, ValueError, KeyError):
                pass

    def _save_experiences(self) -> None:
        """Save experiences to disk."""
        with open(self.log_file, "w") as f:
            for exp in self._experiences.values():
                data = {
                    "id": exp.id,
                    "metrics": {
                        "timestamp": exp.metrics.timestamp,
                        "execution_time": exp.metrics.execution_time,
                        "goal": exp.metrics.goal,
                        "result_success": exp.metrics.result_success,
                        "agents_used": exp.metrics.agents_used,
                        "decisions_made": exp.metrics.decisions_made,
                        "memory_accessed": exp.metrics.memory_accessed,
                        "memory_stored": exp.metrics.memory_stored,
                        "error_count": exp.metrics.error_count,
                        "quality_score": exp.metrics.quality_score,
                        "metadata": exp.metrics.metadata,
                    },
                    "observations": exp.observations,
                    "improvements": exp.improvements,
                    "validated": exp.validated,
                    "improvement_score": exp.improvement_score,
                }
                f.write(json.dumps(data) + "\n")

    def log_experience(
        self,
        metrics: SystemMetrics,
        observations: str,
        improvements: Optional[List[str]] = None,
    ) -> str:
        """Log a system experience.

        Args:
            metrics: Performance metrics
            observations: Observations about what happened
            improvements: Suggested improvements

        Returns:
            Experience ID
        """
        import uuid

        exp_id = str(uuid.uuid4())[:8]
        exp = Experience(
            id=exp_id,
            metrics=metrics,
            observations=observations,
            improvements=improvements or [],
        )
        self._experiences[exp_id] = exp
        self._save_experiences()
        return exp_id

    def get_experience(self, exp_id: str) -> Optional[Experience]:
        """Get an experience by ID.

        Args:
            exp_id: Experience ID

        Returns:
            Experience or None
        """
        return self._experiences.get(exp_id)

    def get_recent_experiences(
        self, limit: int = 10, success_only: bool = False
    ) -> List[Experience]:
        """Get recent experiences.

        Args:
            limit: Maximum number to return
            success_only: Only return successful executions

        Returns:
            List of experiences sorted by timestamp (newest first)
        """
        exps = list(self._experiences.values())
        if success_only:
            exps = [e for e in exps if e.metrics.result_success]

        exps.sort(key=lambda e: e.metrics.timestamp, reverse=True)
        return exps[:limit]

    def get_experiences_by_goal(self, goal: str) -> List[Experience]:
        """Get experiences for a specific goal.

        Args:
            goal: Goal description

        Returns:
            List of matching experiences
        """
        goal_lower = goal.lower()
        matches = [
            e
            for e in self._experiences.values()
            if goal_lower in e.metrics.goal.lower()
        ]
        matches.sort(key=lambda e: e.metrics.timestamp, reverse=True)
        return matches

    def validate_improvement(self, exp_id: str, success: bool) -> bool:
        """Validate whether an improvement was successful.

        Args:
            exp_id: Experience ID
            success: Whether the improvement worked

        Returns:
            True if validated, False if not found
        """
        if exp_id not in self._experiences:
            return False

        exp = self._experiences[exp_id]
        exp.validated = True
        if success:
            exp.improvement_score = min(1.0, exp.improvement_score + 0.1)
        else:
            exp.improvement_score = max(0.0, exp.improvement_score - 0.1)

        self._save_experiences()
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged experiences.

        Returns:
            Statistics dictionary
        """
        if not self._experiences:
            return {
                "total_experiences": 0,
                "successful_rate": 0.0,
                "avg_execution_time": 0.0,
                "validated_improvements": 0,
                "total_improvements_suggested": 0,
            }

        exps = list(self._experiences.values())
        successful = sum(1 for e in exps if e.metrics.result_success)
        validated = sum(1 for e in exps if e.validated)
        total_improvements = sum(len(e.improvements) for e in exps)
        avg_time = sum(e.metrics.execution_time for e in exps) / len(exps)

        return {
            "total_experiences": len(exps),
            "successful_rate": successful / len(exps) if exps else 0.0,
            "avg_execution_time": avg_time,
            "validated_improvements": validated,
            "total_improvements_suggested": total_improvements,
            "storage_location": str(self.storage_dir),
        }

    def export(self, filepath: str) -> None:
        """Export all experiences to file.

        Args:
            filepath: Path to export to
        """
        export_file = Path(filepath)
        export_file.parent.mkdir(parents=True, exist_ok=True)

        data = []
        for exp in self._experiences.values():
            data.append(
                {
                    "id": exp.id,
                    "metrics": {
                        "timestamp": exp.metrics.timestamp,
                        "execution_time": exp.metrics.execution_time,
                        "goal": exp.metrics.goal,
                        "result_success": exp.metrics.result_success,
                        "quality_score": exp.metrics.quality_score,
                    },
                    "observations": exp.observations,
                    "improvements": exp.improvements,
                    "improvement_score": exp.improvement_score,
                }
            )

        with open(export_file, "w") as f:
            json.dump(data, f, indent=2)

    def clear_old_experiences(self, days: int = 30) -> int:
        """Clear experiences older than N days.

        Args:
            days: Age threshold in days

        Returns:
            Number of experiences cleared
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        to_delete = []

        for exp_id, exp in self._experiences.items():
            exp_time = datetime.fromisoformat(exp.metrics.timestamp)
            if exp_time < cutoff:
                to_delete.append(exp_id)

        for exp_id in to_delete:
            del self._experiences[exp_id]

        if to_delete:
            self._save_experiences()

        return len(to_delete)
