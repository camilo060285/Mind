"""Tests for the evolution system."""

import tempfile
from pathlib import Path

import pytest

from mind.evolution import (
    AdaptationEngine,
    ExperienceLogger,
    ExperimentFramework,
    HypothesisGenerator,
    MetricsCollector,
    SystemMetrics,
)


class TestSystemMetrics:
    """Tests for system metrics."""

    def test_create_metrics(self):
        """Test creating system metrics."""
        metrics = SystemMetrics(
            execution_time=1.5,
            goal="Deploy system",
            result_success=True,
            quality_score=0.9,
        )
        assert metrics.execution_time == 1.5
        assert metrics.goal == "Deploy system"
        assert metrics.result_success is True
        assert metrics.quality_score == 0.9


class TestMetricsCollector:
    """Tests for metrics collector."""

    def test_record_metric(self):
        """Test recording a metric."""
        collector = MetricsCollector()
        collector.record_metric("latency", 0.5, category="performance")
        collector.record_metric("memory", 256, category="resource")

        assert "latency" in collector.metrics
        assert "memory" in collector.metrics
        assert len(collector.metrics["latency"]) == 1

    def test_increment_counter(self):
        """Test counter increment."""
        collector = MetricsCollector()
        collector.increment_counter("requests", 5)
        collector.increment_counter("requests", 3)

        assert collector.get_counter("requests") == 8

    def test_finalize(self):
        """Test finalizing collection."""
        collector = MetricsCollector()
        collector.record_metric("metric1", 100)
        collector.increment_counter("counter1", 5)

        summary = collector.finalize()
        assert summary["total_time"] > 0
        assert summary["counters"]["counter1"] == 5


class TestExperienceLogger:
    """Tests for experience logger."""

    @pytest.fixture
    def temp_logger(self):
        """Create temporary experience logger."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ExperienceLogger(Path(tmpdir))
            yield logger

    def test_log_experience(self, temp_logger):
        """Test logging an experience."""
        metrics = SystemMetrics(
            execution_time=1.0,
            goal="Test goal",
            result_success=True,
            quality_score=0.85,
        )
        exp_id = temp_logger.log_experience(metrics, "Test observation")

        assert exp_id is not None
        exp = temp_logger.get_experience(exp_id)
        assert exp is not None
        assert exp.observations == "Test observation"

    def test_get_recent_experiences(self, temp_logger):
        """Test getting recent experiences."""
        metrics1 = SystemMetrics(execution_time=1.0, result_success=True)
        metrics2 = SystemMetrics(execution_time=2.0, result_success=True)

        temp_logger.log_experience(metrics1, "Exp1")
        temp_logger.log_experience(metrics2, "Exp2")

        recent = temp_logger.get_recent_experiences(limit=2)
        assert len(recent) == 2

    def test_get_experiences_by_goal(self, temp_logger):
        """Test filtering by goal."""
        metrics1 = SystemMetrics(goal="Deploy system")
        metrics2 = SystemMetrics(goal="Test system")

        temp_logger.log_experience(metrics1, "Deploy obs")
        temp_logger.log_experience(metrics2, "Test obs")

        deploy_exps = temp_logger.get_experiences_by_goal("Deploy")
        assert len(deploy_exps) >= 1

    def test_validate_improvement(self, temp_logger):
        """Test improvement validation."""
        metrics = SystemMetrics(goal="Test", result_success=True)
        exp_id = temp_logger.log_experience(metrics, "Test")

        assert temp_logger.validate_improvement(exp_id, True) is True
        exp = temp_logger.get_experience(exp_id)
        assert exp.validated is True

    def test_statistics(self, temp_logger):
        """Test statistics generation."""
        metrics1 = SystemMetrics(result_success=True, execution_time=1.0)
        metrics2 = SystemMetrics(result_success=False, execution_time=2.0)

        temp_logger.log_experience(metrics1, "Obs1")
        temp_logger.log_experience(metrics2, "Obs2")

        stats = temp_logger.get_statistics()
        assert stats["total_experiences"] == 2
        assert stats["successful_rate"] == 0.5


class TestHypothesisGenerator:
    """Tests for hypothesis generator."""

    @pytest.fixture
    def generator(self):
        """Create hypothesis generator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ExperienceLogger(Path(tmpdir))
            gen = HypothesisGenerator(logger)
            yield gen

    def test_generate_hypothesis(self, generator):
        """Test generating a custom hypothesis."""
        hyp = generator.generate_hypothesis(
            title="Test Hypothesis",
            description="Test description",
            expected_improvement=0.2,
            priority=3,
            required_changes=["Change 1"],
            affected_components=["component1"],
            estimated_effort="medium",
        )

        assert hyp.title == "Test Hypothesis"
        assert hyp.priority == 3
        assert hyp.validated is False

    def test_get_hypothesis(self, generator):
        """Test retrieving hypothesis."""
        hyp = generator.generate_hypothesis(
            title="Test",
            description="Test",
            expected_improvement=0.1,
            priority=1,
            required_changes=[],
            affected_components=[],
            estimated_effort="low",
        )

        retrieved = generator.get_hypothesis(hyp.id)
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_validate_hypothesis(self, generator):
        """Test hypothesis validation."""
        hyp = generator.generate_hypothesis(
            title="Test",
            description="Test",
            expected_improvement=0.1,
            priority=1,
            required_changes=[],
            affected_components=[],
            estimated_effort="low",
        )

        result = generator.validate_hypothesis(hyp.id, True)
        assert result.validated is True
        assert result.validation_result is True

    def test_filter_by_effort(self, generator):
        """Test filtering by effort."""
        generator.generate_hypothesis(
            title="Easy",
            description="Test",
            expected_improvement=0.1,
            priority=1,
            required_changes=[],
            affected_components=[],
            estimated_effort="low",
        )
        generator.generate_hypothesis(
            title="Hard",
            description="Test",
            expected_improvement=0.1,
            priority=1,
            required_changes=[],
            affected_components=[],
            estimated_effort="high",
        )

        easy = generator.filter_by_effort("low")
        assert len(easy) >= 1


class TestExperimentFramework:
    """Tests for experiment framework."""

    @pytest.fixture
    def framework(self):
        """Create experiment framework."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fw = ExperimentFramework(Path(tmpdir))
            yield fw

    def test_create_experiment(self, framework):
        """Test creating experiment."""
        exp = framework.create_experiment(
            hypothesis_id="hyp_001",
            title="Test Experiment",
            description="Test",
            variant_a_name="Control",
            variant_a_config={"optimized": False},
            variant_b_name="Treatment",
            variant_b_config={"optimized": True},
            sample_size=10,
        )

        assert exp.title == "Test Experiment"
        assert exp.variant_a.name == "Control"
        assert exp.variant_b.name == "Treatment"

    def test_get_experiment(self, framework):
        """Test retrieving experiment."""
        exp = framework.create_experiment(
            hypothesis_id="hyp_001",
            title="Test",
            description="Test",
            variant_a_name="A",
            variant_a_config={},
            variant_b_name="B",
            variant_b_config={},
        )

        retrieved = framework.get_experiment(exp.id)
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_record_result(self, framework):
        """Test recording experiment results."""
        exp = framework.create_experiment(
            hypothesis_id="hyp_001",
            title="Test",
            description="Test",
            variant_a_name="A",
            variant_a_config={},
            variant_b_name="B",
            variant_b_config={},
            sample_size=2,
        )

        framework.record_result(exp.id, "A", 0.8)
        framework.record_result(exp.id, "A", 0.85)
        framework.record_result(exp.id, "B", 0.9)
        framework.record_result(exp.id, "B", 0.95)

        exp = framework.get_experiment(exp.id)
        assert exp.samples_run == 4
        assert exp.status.value == "completed"
        assert exp.winner is not None

    def test_abort_experiment(self, framework):
        """Test aborting experiment."""
        exp = framework.create_experiment(
            hypothesis_id="hyp_001",
            title="Test",
            description="Test",
            variant_a_name="A",
            variant_a_config={},
            variant_b_name="B",
            variant_b_config={},
        )

        framework.abort_experiment(exp.id)
        exp = framework.get_experiment(exp.id)
        assert exp.status.value == "aborted"

    def test_statistics(self, framework):
        """Test framework statistics."""
        framework.create_experiment(
            hypothesis_id="hyp_001",
            title="Test",
            description="Test",
            variant_a_name="A",
            variant_a_config={},
            variant_b_name="B",
            variant_b_config={},
        )

        stats = framework.get_statistics()
        assert stats["total_experiments"] >= 1


class TestAdaptationEngine:
    """Tests for adaptation engine."""

    @pytest.fixture
    def engine(self):
        """Create adaptation engine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ExperienceLogger(Path(tmpdir) / "logger")
            generator = HypothesisGenerator(logger)
            framework = ExperimentFramework(Path(tmpdir) / "experiments")
            engine = AdaptationEngine(logger, generator, framework)
            yield engine

    def test_initialization(self, engine):
        """Test engine initialization."""
        assert engine.logger is not None
        assert engine.hypothesis_gen is not None
        assert engine.experiment_fw is not None

    def test_analyze_and_adapt(self, engine):
        """Test analysis and adaptation."""
        # Add some experiences
        metrics = SystemMetrics(
            execution_time=1.0,
            goal="Test",
            result_success=True,
            quality_score=0.8,
        )
        engine.logger.log_experience(metrics, "Test observation")

        results = engine.analyze_and_adapt()
        assert "hypotheses_generated" in results
        assert "improvements_applied" in results

    def test_propose_experiment(self, engine):
        """Test proposing experiment."""
        hyp = engine.hypothesis_gen.generate_hypothesis(
            title="Test",
            description="Test",
            expected_improvement=0.2,
            priority=3,
            required_changes=["Change 1"],
            affected_components=["comp1"],
            estimated_effort="medium",
        )

        exp = engine.propose_experiment(hyp)
        assert exp is not None
        assert exp.hypothesis_id == hyp.id

    def test_get_status(self, engine):
        """Test getting engine status."""
        status = engine.get_status()
        assert "hypotheses_generated" in status
        assert "experiments_created" in status
        assert "improvements_applied" in status

    def test_reset(self, engine):
        """Test resetting engine."""
        engine.applied_improvements["test"] = True
        engine.reset()
        assert len(engine.applied_improvements) == 0
