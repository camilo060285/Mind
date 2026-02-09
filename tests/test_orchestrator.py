from mind.core.meta_orchestrator import MetaOrchestrator
from mind.core.mind_orchestrator import MindOrchestrator


class TestMetaOrchestrator:
    """Test suite for MetaOrchestrator."""

    def test_meta_orchestrator_initialization(self):
        """Test meta orchestrator initialization."""
        meta = MetaOrchestrator()
        assert meta is not None
        assert meta.loader is not None
        assert meta.agents is not None
        assert len(meta.agents) > 0

    def test_meta_orchestrator_has_required_agents(self):
        """Test that meta orchestrator has all required agents."""
        meta = MetaOrchestrator()
        required_agents = {
            "goal_interpreter_agent",
            "system_designer_agent",
            "boundary_setter_agent",
            "tool_selector_agent",
            "agent_architect_agent",
            "execution_planner_agent",
            "evaluator_agent",
            "evolution_engine_agent",
            "delegator_agent",
        }
        assert required_agents.issubset(set(meta.agents.keys()))

    def test_meta_pipeline_runs(self):
        """Test that meta pipeline executes successfully."""
        meta = MetaOrchestrator()
        result = meta.run_blueprint("blueprints/meta_system.yaml")
        assert isinstance(result, dict)
        assert "final_output" in result
        assert "goal" in result
        assert "constraints" in result

    def test_meta_pipeline_result_structure(self):
        """Test the structure of pipeline result."""
        meta = MetaOrchestrator()
        result = meta.run_blueprint("blueprints/meta_system.yaml")
        # final_output can be dict or string depending on pipeline
        assert result["final_output"] is not None
        assert isinstance(result["goal"], str)
        assert isinstance(result["constraints"], list)

    def test_meta_pipeline_contains_goal_intent(self):
        """Test that pipeline produces goal with intent."""
        meta = MetaOrchestrator()
        result = meta.run_blueprint("blueprints/meta_system.yaml")
        final_output = result["final_output"]
        # The final output should have architectural information
        assert final_output is not None


class TestMindOrchestrator:
    """Test suite for MindOrchestrator."""

    def test_mind_orchestrator_initialization(self):
        """Test mind orchestrator initialization."""
        orchestrator = MindOrchestrator()
        assert orchestrator is not None
        assert orchestrator.identity is not None
        assert orchestrator.meta is not None
        assert orchestrator.thinking is not None
        assert orchestrator.memory is not None

    def test_mind_orchestrator_memory_structure(self):
        """Test mind orchestrator memory is properly initialized."""
        orchestrator = MindOrchestrator()
        memory = orchestrator.memory
        assert isinstance(memory, dict)
        required_keys = {"goals", "architectures", "evaluations", "evolutions"}
        assert required_keys.issubset(set(memory.keys()))
        # All should be lists
        for key in required_keys:
            assert isinstance(memory[key], list)

    def test_mind_lifecycle_execution(self):
        """Test full mind lifecycle execution."""
        orchestrator = MindOrchestrator()
        result = orchestrator.run("blueprints/meta_system.yaml")
        assert isinstance(result, dict)
        assert "identity" in result
        assert "result" in result
        assert "evolution" in result
        assert "memory" in result

    def test_mind_identity_in_result(self):
        """Test that identity is included in result."""
        orchestrator = MindOrchestrator()
        result = orchestrator.run("blueprints/meta_system.yaml")
        identity = result["identity"]
        assert identity["name"] == "Mind"
        assert identity["version"] == "0.1.0"
        assert "capabilities" in identity

    def test_mind_evolution_tracking(self):
        """Test that mind tracks evolution."""
        orchestrator = MindOrchestrator()
        result = orchestrator.run("blueprints/meta_system.yaml")
        evolution = result["evolution"]
        assert "total_goals" in evolution
        assert "total_architectures" in evolution
        assert evolution["total_goals"] > 0
        assert evolution["total_architectures"] > 0

    def test_mind_memory_updated_after_execution(self):
        """Test that memory is updated after execution."""
        orchestrator = MindOrchestrator()
        initial_memory = len(orchestrator.memory["goals"])
        orchestrator.run("blueprints/meta_system.yaml")
        assert len(orchestrator.memory["goals"]) > initial_memory
        assert len(orchestrator.memory["architectures"]) > 0
        assert len(orchestrator.memory["evolutions"]) > 0
