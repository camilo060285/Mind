from core.blueprint_loader import BlueprintLoader


def test_blueprint_loads():
    loader = BlueprintLoader()
    bp = loader.load("blueprints/meta_system.yaml")
    assert "goal" in bp
    assert "pipeline" in bp
