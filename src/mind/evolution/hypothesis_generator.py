"""Hypothesis generation for system improvements based on metrics and experiences."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from mind.evolution.experience_logger import ExperienceLogger


@dataclass
class Hypothesis:
    """A proposed improvement hypothesis."""

    id: str
    title: str
    description: str
    expected_improvement: float  # 0-1 estimated improvement
    priority: int  # 1-5, higher is more important
    required_changes: List[str]
    affected_components: List[str]
    estimated_effort: str  # "low", "medium", "high"
    validated: bool = False
    validation_result: Optional[bool] = None


class HypothesisGenerator:
    """Generates improvement hypotheses from experiences and metrics."""

    def __init__(self, experience_logger: ExperienceLogger):
        """Initialize hypothesis generator.

        Args:
            experience_logger: ExperienceLogger instance for analyzing experiences
        """
        self.logger = experience_logger
        self.hypotheses: Dict[str, Hypothesis] = {}

    def analyze_performance(self) -> List[Hypothesis]:
        """Analyze recent experiences and generate hypotheses.

        Returns:
            List of generated hypotheses
        """
        hypotheses: List[Hypothesis] = []

        # Get recent experiences
        recent = self.logger.get_recent_experiences(limit=20)
        if not recent:
            return hypotheses

        # Analyze success rate
        success_rate = sum(1 for e in recent if e.metrics.result_success) / len(recent)

        if success_rate < 0.7:
            hyp = Hypothesis(
                id="hyp_001",
                title="Improve Decision Making",
                description="Success rate is below 70%. Implement better decision strategy.",
                expected_improvement=0.15,
                priority=5,
                required_changes=[
                    "Enhance reasoning engine",
                    "Add more context to decisions",
                ],
                affected_components=["reasoning_engine", "goal_interpreter_agent"],
                estimated_effort="high",
            )
            hypotheses.append(hyp)
            self.hypotheses[hyp.id] = hyp

        # Analyze execution time
        avg_time = sum(e.metrics.execution_time for e in recent) / len(recent)
        if avg_time > 5.0:
            hyp = Hypothesis(
                id="hyp_002",
                title="Optimize Execution Speed",
                description=f"Average execution time is {avg_time:.1f}s. Add caching and parallelization.",
                expected_improvement=0.25,
                priority=4,
                required_changes=[
                    "Implement caching layer",
                    "Enable parallel agent execution",
                ],
                affected_components=["orchestrator", "agent_executor"],
                estimated_effort="high",
            )
            hypotheses.append(hyp)
            self.hypotheses[hyp.id] = hyp

        # Analyze error frequency
        avg_errors = sum(e.metrics.error_count for e in recent) / len(recent)
        if avg_errors > 0:
            hyp = Hypothesis(
                id="hyp_003",
                title="Reduce Error Rate",
                description=f"Average {avg_errors:.1f} errors per execution. Add validation and error recovery.",
                expected_improvement=0.2,
                priority=4,
                required_changes=[
                    "Add input validation",
                    "Implement error recovery strategies",
                ],
                affected_components=["agents", "orchestrator"],
                estimated_effort="medium",
            )
            hypotheses.append(hyp)
            self.hypotheses[hyp.id] = hyp

        # Analyze memory usage patterns
        memory_stored = sum(e.metrics.memory_stored for e in recent) / len(recent)
        memory_accessed = sum(e.metrics.memory_accessed for e in recent) / len(recent)

        if memory_accessed < memory_stored * 0.3:
            hyp = Hypothesis(
                id="hyp_004",
                title="Improve Memory Utilization",
                description="Only 30% of stored memories are being accessed. Review memory organization.",
                expected_improvement=0.1,
                priority=2,
                required_changes=[
                    "Review tagging strategy",
                    "Improve search relevance",
                ],
                affected_components=["memory_store", "memory_manager"],
                estimated_effort="low",
            )
            hypotheses.append(hyp)
            self.hypotheses[hyp.id] = hyp

        return hypotheses

    def generate_hypothesis(
        self,
        title: str,
        description: str,
        expected_improvement: float,
        priority: int,
        required_changes: List[str],
        affected_components: List[str],
        estimated_effort: str,
    ) -> Hypothesis:
        """Generate a custom hypothesis.

        Args:
            title: Hypothesis title
            description: Detailed description
            expected_improvement: Expected improvement (0-1)
            priority: Priority (1-5)
            required_changes: List of changes needed
            affected_components: List of affected components
            estimated_effort: Effort level (low/medium/high)

        Returns:
            Generated hypothesis
        """
        import uuid

        hyp_id = f"hyp_{uuid.uuid4().hex[:6]}"
        hyp = Hypothesis(
            id=hyp_id,
            title=title,
            description=description,
            expected_improvement=expected_improvement,
            priority=priority,
            required_changes=required_changes,
            affected_components=affected_components,
            estimated_effort=estimated_effort,
        )
        self.hypotheses[hyp_id] = hyp
        return hyp

    def get_hypothesis(self, hyp_id: str) -> Optional[Hypothesis]:
        """Get hypothesis by ID.

        Args:
            hyp_id: Hypothesis ID

        Returns:
            Hypothesis or None
        """
        return self.hypotheses.get(hyp_id)

    def get_top_hypotheses(self, limit: int = 5) -> List[Hypothesis]:
        """Get top prioritized hypotheses.

        Args:
            limit: Maximum to return

        Returns:
            Sorted hypotheses by priority
        """
        hyps = list(self.hypotheses.values())
        hyps.sort(key=lambda h: (-h.priority, -h.expected_improvement))
        return hyps[:limit]

    def validate_hypothesis(self, hyp_id: str, result: bool) -> Optional[Hypothesis]:
        """Validate a hypothesis based on experiment result.

        Args:
            hyp_id: Hypothesis ID
            result: Whether hypothesis was validated

        Returns:
            Updated hypothesis or None
        """
        if hyp_id not in self.hypotheses:
            return None

        hyp = self.hypotheses[hyp_id]
        hyp.validated = True
        hyp.validation_result = result
        return hyp

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated hypotheses.

        Returns:
            Statistics dictionary
        """
        hyps = list(self.hypotheses.values())
        validated = sum(1 for h in hyps if h.validated)
        successful = sum(1 for h in hyps if h.validated and h.validation_result)

        return {
            "total_hypotheses": len(hyps),
            "validated": validated,
            "successful_validations": successful,
            "avg_priority": sum(h.priority for h in hyps) / len(hyps) if hyps else 0,
            "avg_expected_improvement": (
                sum(h.expected_improvement for h in hyps) / len(hyps) if hyps else 0
            ),
        }

    def filter_by_component(self, component: str) -> List[Hypothesis]:
        """Get hypotheses affecting a specific component.

        Args:
            component: Component name

        Returns:
            List of hypotheses
        """
        return [
            h for h in self.hypotheses.values() if component in h.affected_components
        ]

    def filter_by_effort(self, effort: str) -> List[Hypothesis]:
        """Get hypotheses by required effort.

        Args:
            effort: Effort level (low/medium/high)

        Returns:
            List of hypotheses
        """
        return [h for h in self.hypotheses.values() if h.estimated_effort == effort]
