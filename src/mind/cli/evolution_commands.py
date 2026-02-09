"""Evolution system CLI commands for the interactive shell."""

from mind.evolution import (
    AdaptationEngine,
    ExperienceLogger,
    ExperimentFramework,
    HypothesisGenerator,
    SystemMetrics,
)


class EvolutionCommandHandler:
    """Handler for evolution-related CLI commands."""

    def __init__(
        self,
        experience_logger: ExperienceLogger | None = None,
        hypothesis_generator: HypothesisGenerator | None = None,
        experiment_framework: ExperimentFramework | None = None,
        adaptation_engine: AdaptationEngine | None = None,
    ):
        """Initialize evolution command handler.

        Args:
            experience_logger: Experience logger instance
            hypothesis_generator: Hypothesis generator instance
            experiment_framework: Experiment framework instance
            adaptation_engine: Adaptation engine instance
        """
        self.logger = experience_logger or ExperienceLogger()
        self.hypothesis_gen = hypothesis_generator or HypothesisGenerator(self.logger)
        self.experiment_fw = experiment_framework or ExperimentFramework()
        self.adaptation_engine = adaptation_engine or AdaptationEngine(
            self.logger, self.hypothesis_gen, self.experiment_fw
        )

    def handle_log_experience(self, args: str) -> str:
        """Log a system experience.

        Usage: log_exp <goal> <observation>

        Args:
            args: Goal and observation

        Returns:
            Confirmation message
        """
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            return "Error: Usage: log_exp <goal> <observation>"

        goal, observation = parts[0], parts[1].strip().strip("\"'")

        metrics = SystemMetrics(
            goal=goal,
            execution_time=0.0,
            result_success=True,
            quality_score=0.8,
        )
        exp_id = self.logger.log_experience(metrics, observation)
        return f"Logged experience: {exp_id}"

    def handle_analyze(self, args: str) -> str:
        """Analyze system and generate improvement hypotheses.

        Usage: analyze

        Args:
            args: Unused

        Returns:
            Analysis results
        """
        hypotheses = self.hypothesis_gen.analyze_performance()

        output = f"Generated {len(hypotheses)} improvement hypotheses:\n"
        for i, hyp in enumerate(hypotheses, 1):
            output += f"\n{i}. {hyp.title} (Priority: {hyp.priority})\n"
            output += f"   Expected improvement: {hyp.expected_improvement*100:.0f}%\n"
            output += f"   Effort: {hyp.estimated_effort}\n"

        return output.rstrip()

    def handle_show_hypothesis(self, args: str) -> str:
        """Show hypothesis details.

        Usage: show_hyp <hyp_id>

        Args:
            args: Hypothesis ID

        Returns:
            Hypothesis details
        """
        hyp_id = args.strip()
        if not hyp_id:
            return "Error: Please provide hypothesis ID"

        hyp = self.hypothesis_gen.get_hypothesis(hyp_id)
        if not hyp:
            return f"Not found: {hyp_id}"

        output = f"Hypothesis: {hyp.title}\n"
        output += f"ID: {hyp.id}\n"
        output += f"Description: {hyp.description}\n"
        output += f"Priority: {hyp.priority}/5\n"
        output += f"Expected improvement: {hyp.expected_improvement*100:.0f}%\n"
        output += f"Effort: {hyp.estimated_effort}\n"
        output += f"Components: {', '.join(hyp.affected_components)}\n"
        output += "Changes needed:\n"
        for change in hyp.required_changes:
            output += f"  - {change}\n"
        output += f"Validated: {hyp.validated}\n"

        return output.rstrip()

    def handle_list_hypotheses(self, args: str) -> str:
        """List top hypotheses.

        Usage: list_hyp [limit]

        Args:
            args: Optional limit (default 5)

        Returns:
            List of hypotheses
        """
        limit = 5
        if args.strip():
            try:
                limit = int(args.strip())
            except ValueError:
                return "Error: Limit must be a number"

        hypotheses = self.hypothesis_gen.get_top_hypotheses(limit=limit)
        if not hypotheses:
            return "No hypotheses found"

        output = f"Top {len(hypotheses)} hypotheses:\n"
        for i, hyp in enumerate(hypotheses, 1):
            output += (
                f"{i}. {hyp.title} - Priority: {hyp.priority}, "
                f"Expected: +{hyp.expected_improvement*100:.0f}%\n"
            )

        return output.rstrip()

    def handle_propose_experiment(self, args: str) -> str:
        """Propose experiment for a hypothesis.

        Usage: propose_exp <hyp_id>

        Args:
            args: Hypothesis ID

        Returns:
            Confirmation message
        """
        hyp_id = args.strip()
        if not hyp_id:
            return "Error: Please provide hypothesis ID"

        hyp = self.hypothesis_gen.get_hypothesis(hyp_id)
        if not hyp:
            return f"Not found: {hyp_id}"

        exp = self.adaptation_engine.propose_experiment(hyp)
        if not exp:
            return f"Failed to create experiment for {hyp_id}"

        return f"Created experiment: {exp.id}\nTitle: {exp.title}"

    def handle_record_result(self, args: str) -> str:
        """Record experiment result.

        Usage: record_result <exp_id> <variant> <score>

        Args:
            args: Experiment ID, variant (A/B), and score

        Returns:
            Confirmation message
        """
        parts = args.split()
        if len(parts) < 3:
            return "Error: Usage: record_result <exp_id> <variant> <score>"

        exp_id, variant, score_str = parts[0], parts[1], parts[2]

        try:
            score = float(score_str)
        except ValueError:
            return "Error: Score must be a number"

        exp = self.experiment_fw.record_result(exp_id, variant, score)
        if not exp:
            return f"Not found: {exp_id}"

        if exp.status.value == "completed":
            return f"Experiment completed. Winner: {exp.winner}"
        return f"Result recorded. Progress: {exp.samples_run}/{exp.sample_size*2}"

    def handle_adaptation_status(self, args: str) -> str:
        """Show adaptation engine status.

        Usage: adapt_status

        Args:
            args: Unused

        Returns:
            Status information
        """
        status = self.adaptation_engine.get_status()

        output = "Adaptation Engine Status:\n"
        output += f"Hypotheses generated: {status['hypotheses_generated']}\n"
        output += f"Experiments created: {status['experiments_created']}\n"
        output += f"Improvements applied: {status['improvements_applied']}\n"
        output += f"Total experiences: {status['experience_count']}\n"

        return output.rstrip()

    def handle_evolution_stats(self, args: str) -> str:
        """Show evolution statistics.

        Usage: evo_stats

        Args:
            args: Unused

        Returns:
            Statistics
        """
        stats = self.logger.get_statistics()

        output = "Evolution Statistics:\n"
        output += f"Total experiences: {stats['total_experiences']}\n"
        output += f"Success rate: {stats['successful_rate']*100:.1f}%\n"
        output += f"Avg execution time: {stats['avg_execution_time']:.2f}s\n"
        output += f"Validated improvements: {stats['validated_improvements']}\n"
        output += (
            f"Total improvements suggested: {stats['total_improvements_suggested']}\n"
        )

        return output.rstrip()

    def handle_impact_analysis(self, args: str) -> str:
        """Show improvement impact analysis.

        Usage: impact

        Args:
            args: Unused

        Returns:
            Impact analysis
        """
        impact = self.adaptation_engine.get_impact_analysis()

        output = "Impact Analysis:\n"
        output += "Recent Performance:\n"
        for key, value in impact["recent_performance"].items():
            if isinstance(value, float):
                output += f"  {key}: {value:.2f}\n"

        output += "\nBaseline Performance:\n"
        for key, value in impact["baseline_performance"].items():
            if isinstance(value, float):
                output += f"  {key}: {value:.2f}\n"

        output += "\nImprovements:\n"
        for key, value in impact["improvements"].items():
            output += f"  {key}: {value:+.2f}\n"

        return output.rstrip()
