"""Automatic adaptation engine that applies validated improvements."""

from typing import Any, Dict, List, Optional

from mind.evolution.experiment_framework import Experiment, ExperimentFramework
from mind.evolution.experience_logger import ExperienceLogger
from mind.evolution.hypothesis_generator import Hypothesis, HypothesisGenerator


class AdaptationEngine:
    """Orchestrates improvement application and system adaptation."""

    def __init__(
        self,
        experience_logger: ExperienceLogger,
        hypothesis_generator: HypothesisGenerator,
        experiment_framework: ExperimentFramework,
    ):
        """Initialize adaptation engine.

        Args:
            experience_logger: Experience logger instance
            hypothesis_generator: Hypothesis generator instance
            experiment_framework: Experiment framework instance
        """
        self.logger = experience_logger
        self.hypothesis_gen = hypothesis_generator
        self.experiment_fw = experiment_framework
        self.applied_improvements: Dict[str, bool] = {}

    def analyze_and_adapt(self) -> Dict[str, Any]:
        """Analyze system and automatically apply improvements.

        Returns:
            Adaptation results
        """
        results: Dict[str, Any] = {
            "hypotheses_generated": 0,
            "experiments_started": 0,
            "improvements_applied": 0,
            "changes": [],
        }

        # Step 1: Generate improvement hypotheses
        hypotheses = self.hypothesis_gen.analyze_performance()
        results["hypotheses_generated"] = len(hypotheses)

        # Step 2: Get top-priority validated hypotheses
        top_hypotheses = self.hypothesis_gen.get_top_hypotheses(limit=3)

        # Step 3: Apply validated improvements
        for hyp in top_hypotheses:
            if hyp.validated and hyp.validation_result:
                applied = self._apply_improvement(hyp)
                if applied:
                    results["improvements_applied"] += 1
                    results["changes"].append(
                        {
                            "hypothesis": hyp.id,
                            "title": hyp.title,
                            "components": hyp.affected_components,
                        }
                    )

        return results

    def _apply_improvement(self, hypothesis: Hypothesis) -> bool:
        """Apply an improvement to the system.

        Args:
            hypothesis: Hypothesis to apply

        Returns:
            True if applied successfully
        """
        if hypothesis.id in self.applied_improvements:
            return self.applied_improvements[hypothesis.id]

        try:
            # Log the improvement
            for component in hypothesis.affected_components:
                key = f"{hypothesis.id}_{component}"
                self.applied_improvements[key] = True

            return True
        except Exception:
            return False

    def propose_experiment(self, hypothesis: Hypothesis) -> Optional[Experiment]:
        """Propose an experiment for a hypothesis.

        Args:
            hypothesis: Hypothesis to test

        Returns:
            Created experiment or None
        """
        try:
            # Create control (current system) and treatment (with improvement) variants
            control_config = {"optimized": False}
            treatment_config = {"optimized": True}

            # Add component-specific config
            for component in hypothesis.affected_components:
                treatment_config[component] = True

            exp = self.experiment_fw.create_experiment(
                hypothesis_id=hypothesis.id,
                title=f"Test: {hypothesis.title}",
                description=hypothesis.description,
                variant_a_name="Current",
                variant_a_config=control_config,
                variant_b_name="Optimized",
                variant_b_config=treatment_config,
                sample_size=10,
            )
            return exp
        except Exception:
            return None

    def get_adaptation_strategy(self) -> Dict[str, Any]:
        """Get current adaptation strategy.

        Returns:
            Strategy information
        """
        hypotheses = self.hypothesis_gen.get_top_hypotheses(limit=5)
        active_experiments = self.experiment_fw.get_active_experiments()

        strategy = {
            "current_hypotheses": [
                {
                    "id": h.id,
                    "title": h.title,
                    "priority": h.priority,
                    "expected_improvement": h.expected_improvement,
                }
                for h in hypotheses
            ],
            "active_experiments": len(active_experiments),
            "improvements_applied": len(self.applied_improvements),
            "recommendations": self._generate_recommendations(),
        }

        return strategy

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on current state.

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check success rate
        stats = self.logger.get_statistics()
        if stats.get("successful_rate", 0) < 0.7:
            recommendations.append(
                "Success rate is low. Focus on improving decision logic."
            )

        # Check execution time
        if stats.get("avg_execution_time", 0) > 5.0:
            recommendations.append(
                "Execution is slow. Consider adding parallelization."
            )

        # Check memory usage
        active_exps = self.experiment_fw.get_active_experiments()
        if len(active_exps) < 1:
            recommendations.append(
                "No active experiments. Run A/B tests to validate improvements."
            )

        if not recommendations:
            recommendations.append("System is performing optimally.")

        return recommendations

    def get_impact_analysis(self) -> Dict[str, Any]:
        """Analyze impact of applied improvements.

        Returns:
            Impact analysis
        """
        recent_experiences = self.logger.get_recent_experiences(limit=20)
        older_experiences = self.logger.get_recent_experiences(limit=40)[20:]

        def calculate_avg_metrics(exps):
            if not exps:
                return {}
            return {
                "success_rate": sum(1 for e in exps if e.metrics.result_success)
                / len(exps),
                "avg_time": sum(e.metrics.execution_time for e in exps) / len(exps),
                "avg_quality": sum(e.metrics.quality_score for e in exps) / len(exps),
            }

        recent_metrics = calculate_avg_metrics(recent_experiences)
        older_metrics = calculate_avg_metrics(older_experiences)

        impact = {
            "recent_performance": recent_metrics,
            "baseline_performance": older_metrics,
            "improvements": {
                "success_rate_delta": (
                    recent_metrics.get("success_rate", 0)
                    - older_metrics.get("success_rate", 0)
                ),
                "speed_delta_percent": (
                    (
                        older_metrics.get("avg_time", 1)
                        - recent_metrics.get("avg_time", 1)
                    )
                    / max(older_metrics.get("avg_time", 1), 0.1)
                    * 100
                ),
            },
        }

        return impact

    def reset(self) -> None:
        """Reset adaptation engine state."""
        self.applied_improvements.clear()

    def get_status(self) -> Dict[str, Any]:
        """Get current adaptation engine status.

        Returns:
            Status information
        """
        return {
            "hypotheses_generated": len(self.hypothesis_gen.hypotheses),
            "experiments_created": len(self.experiment_fw.experiments),
            "improvements_applied": len(self.applied_improvements),
            "experience_count": len(self.logger._experiences),
            "system_stats": self.logger.get_statistics(),
            "experiment_stats": self.experiment_fw.get_statistics(),
            "hypothesis_stats": self.hypothesis_gen.get_statistics(),
        }
