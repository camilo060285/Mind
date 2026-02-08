from core.meta_orchestrator import MetaOrchestrator


def test_meta_pipeline_runs():
    meta = MetaOrchestrator()
    result = meta.run_blueprint("blueprints/meta_system.yaml")
    assert "final_output" in result
    assert "goal" in result
