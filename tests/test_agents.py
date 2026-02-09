from mind.agents.goal_interpreter_agent import GoalInterpreterAgent
from mind.agents.system_designer_agent import SystemDesignerAgent
from mind.agents.boundary_setter_agent import BoundarySetterAgent
from mind.agents.evaluator_agent import EvaluatorAgent


class TestGoalInterpreterAgent:
    """Test suite for GoalInterpreterAgent."""

    def test_goal_interpreter_initialization(self):
        """Test agent initialization."""
        agent = GoalInterpreterAgent()
        assert agent.name == "goal_interpreter_agent"
        assert agent.description is not None
        assert isinstance(agent.history, list)

    def test_goal_interpreter_basic_run(self):
        """Test basic goal interpretation."""
        agent = GoalInterpreterAgent()
        result = agent.run("Build a subsystem for Mind.")
        assert isinstance(result, dict)
        assert "raw_text" in result
        assert "intent" in result
        assert "constraints" in result
        assert result["raw_text"] == "Build a subsystem for Mind."

    def test_goal_interpreter_with_constraints(self):
        """Test goal interpretation with constraint keywords."""
        agent = GoalInterpreterAgent()
        result = agent.run("Design a privacy-preserving system with local execution.")
        assert isinstance(result, dict)
        assert len(result["constraints"]) > 0
        assert any("privacy" in c.lower() for c in result["constraints"])

    def test_goal_interpreter_history(self):
        """Test that agent logs entries to history."""
        agent = GoalInterpreterAgent()
        initial_history_len = len(agent.history)
        agent.run("Test goal")
        assert len(agent.history) > initial_history_len


class TestSystemDesignerAgent:
    """Test suite for SystemDesignerAgent."""

    def test_system_designer_initialization(self):
        """Test agent initialization."""
        agent = SystemDesignerAgent()
        assert agent.name == "system_designer_agent"

    def test_system_designer_returns_architecture(self):
        """Test that agent returns architecture dict."""
        agent = SystemDesignerAgent()
        goal = {"intent": "build_system", "constraints": []}
        result = agent.run(goal)
        assert isinstance(result, dict)
        assert "components" in result
        assert "data_flow" in result
        assert len(result["components"]) > 0


class TestBoundarySetterAgent:
    """Test suite for BoundarySetterAgent."""

    def test_boundary_setter_applies_constraints(self):
        """Test that agent applies boundary constraints."""
        agent = BoundarySetterAgent()
        architecture = {"components": ["a", "b"]}
        constraints = ["Respect privacy", "Local execution"]
        result = agent.run(architecture, constraints)
        assert "boundaries" in result
        assert result["boundaries"] == constraints


class TestEvaluatorAgent:
    """Test suite for EvaluatorAgent."""

    def test_evaluator_basic_scoring(self):
        """Test that evaluator provides scoring."""
        agent = EvaluatorAgent()
        system_output = {
            "components": ["a", "b", "c", "d", "e"],
            "complexity": "medium",
        }
        result = agent.run(system_output)
        assert isinstance(result, dict)
        assert "score" in result
        assert "issues" in result
        assert "suggestions" in result
        assert result["score"] > 0

    def test_evaluator_handles_high_complexity(self):
        """Test evaluator with high complexity."""
        agent = EvaluatorAgent()
        system_output = {
            "components": ["a", "b"],
            "complexity": "high",
        }
        result = agent.run(system_output)
        assert len(result["issues"]) > 0
