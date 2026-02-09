import pytest
from mind.core.blueprint_loader import BlueprintLoader


class TestBlueprintLoader:
    """Test suite for BlueprintLoader."""

    def test_blueprint_loader_initialization(self):
        """Test loader initialization."""
        loader = BlueprintLoader()
        assert loader is not None

    def test_blueprint_loads_valid_file(self):
        """Test loading valid blueprint file."""
        loader = BlueprintLoader()
        bp = loader.load("blueprints/meta_system.yaml")
        assert isinstance(bp, dict)
        assert "goal" in bp
        assert "pipeline" in bp

    def test_blueprint_goal_structure(self):
        """Test blueprint goal structure."""
        loader = BlueprintLoader()
        bp = loader.load("blueprints/meta_system.yaml")
        assert isinstance(bp["goal"], dict)
        assert "raw_text" in bp["goal"]

    def test_blueprint_pipeline_structure(self):
        """Test blueprint pipeline structure."""
        loader = BlueprintLoader()
        bp = loader.load("blueprints/meta_system.yaml")
        assert isinstance(bp["pipeline"], list)
        assert len(bp["pipeline"]) > 0
        for step in bp["pipeline"]:
            assert "agent" in step

    def test_blueprint_constraints_present(self):
        """Test that constraints are defined in blueprint."""
        loader = BlueprintLoader()
        bp = loader.load("blueprints/meta_system.yaml")
        assert "constraints" in bp
        assert isinstance(bp["constraints"], list)
        assert len(bp["constraints"]) > 0

    def test_blueprint_file_not_found(self):
        """Test error handling for missing blueprint."""
        loader = BlueprintLoader()
        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent/blueprint.yaml")
