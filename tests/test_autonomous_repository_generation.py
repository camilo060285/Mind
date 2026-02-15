"""Tests for autonomous repository generation."""

import pytest
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from mind.system_generator import (
    SystemGenerator,
    SystemRegistry,
    RepositoryInitializer,
    SystemGenerationOutput,
)
from mind.system_generator.system_spec import SystemSpec


class TestRepositoryInitializer:
    """Test repository initialization."""

    def test_init_creates_parent_dir(self):
        """Test that initializer creates parent directory."""
        with TemporaryDirectory() as tmpdir:
            RepositoryInitializer(Path(tmpdir))
            assert (Path(tmpdir)).exists()

    def test_create_system_repository(self):
        """Test creating a system repository."""
        with TemporaryDirectory() as tmpdir:
            initializer = RepositoryInitializer(Path(tmpdir))

            spec = SystemSpec(
                name="Test System",
                goal="Test goal",
                description="Test description",
                features=["feature1"],
                tools=["tool1"],
                config={"system_id": "test123"},
            )

            repo_info = initializer.create_system_repository(
                "test_system", "test123", spec, "subsystem"
            )

            assert repo_info["status"] == "ready"
            assert repo_info["system_id"] == "test123"
            assert repo_info["system_name"] == "test_system"
            assert repo_info["system_type"] == "subsystem"
            assert "main" in repo_info["branches"]
            assert "dev" in repo_info["branches"]

    def test_repo_has_git_history(self):
        """Test that created repo has Git history."""
        with TemporaryDirectory() as tmpdir:
            initializer = RepositoryInitializer(Path(tmpdir))

            spec = SystemSpec(
                name="Test System",
                goal="Test goal",
                description="Test description",
            )

            repo_info = initializer.create_system_repository(
                "test_system", "test123", spec, "subsystem"
            )

            repo_path = Path(repo_info["repo_path"])

            # Check Git directory exists
            assert (repo_path / ".git").exists()

            # Check we can get commit history
            result = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=repo_path,
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0
            assert "test123" in result.stdout or "Initial commit" in result.stdout

    def test_gitignore_created(self):
        """Test that .gitignore is created."""
        with TemporaryDirectory() as tmpdir:
            initializer = RepositoryInitializer(Path(tmpdir))

            spec = SystemSpec(
                name="Test System",
                goal="Test goal",
                description="Test description",
            )

            repo_info = initializer.create_system_repository(
                "test_system", "test123", spec, "subsystem"
            )

            repo_path = Path(repo_info["repo_path"])
            gitignore = repo_path / ".gitignore"

            assert gitignore.exists()
            content = gitignore.read_text()
            assert "__pycache__" in content
            assert ".venv" in content or "venv/" in content

    def test_readme_created(self):
        """Test that README is created."""
        with TemporaryDirectory() as tmpdir:
            initializer = RepositoryInitializer(Path(tmpdir))

            spec = SystemSpec(
                name="Test System",
                goal="Test goal",
                description="Test description",
                features=["feature1", "feature2"],
            )

            repo_info = initializer.create_system_repository(
                "test_system", "test123", spec, "subsystem"
            )

            repo_path = Path(repo_info["repo_path"])
            readme = repo_path / "README.md"

            assert readme.exists()
            content = readme.read_text()
            assert "Test System" in content
            assert "Test goal" in content
            assert "autonomously" in content.lower()

    def test_metadata_created(self):
        """Test that system metadata is created."""
        with TemporaryDirectory() as tmpdir:
            initializer = RepositoryInitializer(Path(tmpdir))

            spec = SystemSpec(
                name="Test System",
                goal="Test goal",
                description="Test description",
                tools=["tool1", "tool2"],
            )

            repo_info = initializer.create_system_repository(
                "test_system", "test123", spec, "subsystem"
            )

            repo_path = Path(repo_info["repo_path"])
            metadata_file = repo_path / "system.metadata.json"

            assert metadata_file.exists()

            with open(metadata_file) as f:
                metadata = json.load(f)

            assert metadata["system"]["id"] == "test123"
            assert metadata["system"]["name"] == "test_system"
            assert metadata["system"]["type"] == "subsystem"
            assert metadata["generation"]["mind_name"] == "Mind"
            assert metadata["repository"]["type"] == "git"
            assert "main" in metadata["repository"]["branches"]

    def test_directory_structure_created(self):
        """Test that proper directory structure is created."""
        with TemporaryDirectory() as tmpdir:
            initializer = RepositoryInitializer(Path(tmpdir))

            spec = SystemSpec(
                name="Test System",
                goal="Test goal",
                description="Test description",
            )

            repo_info = initializer.create_system_repository(
                "test_system", "test123", spec, "subsystem"
            )

            repo_path = Path(repo_info["repo_path"])

            # Check required directories
            required_dirs = [
                "agents",
                "models",
                "blueprints",
                "core",
                "tests",
                "data",
                "config",
                "scripts",
                "docs",
            ]

            for d in required_dirs:
                assert (repo_path / d).is_dir(), f"Missing directory: {d}"


class TestSystemRegistry:
    """Test system registry."""

    def test_init_creates_registry_dir(self):
        """Test that registry initializer creates directory."""
        with TemporaryDirectory() as tmpdir:
            registry = SystemRegistry(Path(tmpdir))
            assert registry.registry_dir.exists()

    def test_register_system(self):
        """Test registering a system."""
        with TemporaryDirectory() as tmpdir:
            registry = SystemRegistry(Path(tmpdir))

            repo_info = {"repo_path": "/path/to/repo", "repo_url": "/path/to/repo"}
            spec_dict = {
                "name": "Test System",
                "goal": "Test goal",
                "features": ["f1"],
            }

            registry.register_system("test123", "test_system", repo_info, spec_dict)

            assert "test123" in registry.systems
            assert registry.systems["test123"]["name"] == "test_system"

    def test_get_system(self):
        """Test getting a system from registry."""
        with TemporaryDirectory() as tmpdir:
            registry = SystemRegistry(Path(tmpdir))

            repo_info = {"repo_path": "/path/to/repo"}
            spec_dict = {"name": "Test System"}

            registry.register_system("test123", "test_system", repo_info, spec_dict)

            system = registry.get_system("test123")
            assert system is not None
            assert system["id"] == "test123"

    def test_list_systems(self):
        """Test listing all systems."""
        with TemporaryDirectory() as tmpdir:
            registry = SystemRegistry(Path(tmpdir))

            for i in range(3):
                repo_info = {"repo_path": f"/path/to/repo{i}"}
                spec_dict = {"name": f"System {i}"}
                registry.register_system(f"id{i}", f"system_{i}", repo_info, spec_dict)

            systems = registry.list_systems()
            assert len(systems) == 3

    def test_get_system_by_name(self):
        """Test finding system by name."""
        with TemporaryDirectory() as tmpdir:
            registry = SystemRegistry(Path(tmpdir))

            repo_info = {"repo_path": "/path/to/repo"}
            spec_dict = {"name": "Test System"}

            registry.register_system("test123", "my_test_system", repo_info, spec_dict)

            system = registry.get_system_by_name("my_test_system")
            assert system is not None
            assert system["id"] == "test123"

    def test_update_system_status(self):
        """Test updating system status."""
        with TemporaryDirectory() as tmpdir:
            registry = SystemRegistry(Path(tmpdir))

            repo_info = {"repo_path": "/path/to/repo"}
            spec_dict = {"name": "Test System"}

            registry.register_system("test123", "test_system", repo_info, spec_dict)

            assert registry.systems["test123"]["status"] == "active"

            registry.update_system_status("test123", "archived")
            assert registry.systems["test123"]["status"] == "archived"

    def test_registry_persistence(self):
        """Test that registry persists to disk."""
        with TemporaryDirectory() as tmpdir:
            # Create and populate registry
            registry1 = SystemRegistry(Path(tmpdir))
            repo_info = {"repo_path": "/path/to/repo"}
            spec_dict = {"name": "Test System"}
            registry1.register_system("test123", "test_system", repo_info, spec_dict)

            # Load registry in new instance
            registry2 = SystemRegistry(Path(tmpdir))
            system = registry2.get_system("test123")

            assert system is not None
            assert system["id"] == "test123"

    def test_registry_summary(self):
        """Test registry summary generation."""
        with TemporaryDirectory() as tmpdir:
            registry = SystemRegistry(Path(tmpdir))

            for i in range(2):
                repo_info = {"repo_path": f"/path/to/repo{i}"}
                spec_dict = {"name": f"System {i}"}
                registry.register_system(f"id{i}", f"system_{i}", repo_info, spec_dict)

            summary = registry.get_registry_summary()

            assert summary["total_systems"] == 2
            assert summary["active"] == 2
            assert summary["archived"] == 0


class TestSystemGenerationOutput:
    """Test output formatting."""

    def test_console_output_format(self):
        """Test console output formatting."""
        repo_info = {
            "repo_path": "/path/to/repo",
            "system_id": "test123",
            "system_name": "test_system",
            "system_type": "subsystem",
        }
        spec = {"name": "Test", "goal": "Test goal", "components": [], "features": []}

        output = SystemGenerationOutput.format_console_output(repo_info, spec, "")

        assert "SYSTEM GENERATION COMPLETE" in output
        assert "test123" in output
        assert "test_system" in output
        assert "subsystem" in output

    def test_json_output_format(self):
        """Test JSON output formatting."""
        repo_info = {"repo_path": "/path/to/repo", "system_id": "test123"}
        spec = {"name": "Test"}
        registry_entry = {"id": "test123"}

        output = SystemGenerationOutput.format_json_output(
            repo_info, spec, registry_entry
        )

        assert output["status"] == "success"
        assert "timestamp" in output
        assert output["repository"] == repo_info
        assert output["specification"] == spec
        assert output["registry_entry"] == registry_entry

    def test_manifest_output_format(self):
        """Test manifest output formatting."""
        repo_info = {"system_id": "test123", "system_name": "test_system"}
        spec = {"goal": "Test goal", "features": [], "tools": []}

        output = SystemGenerationOutput.format_manifest_output(repo_info, spec)

        assert "test123" in output
        assert "test_system" in output
        assert "Test goal" in output

    def test_integration_guide_format(self):
        """Test integration guide formatting."""
        spec = {"name": "Test System"}
        repo_path = "/path/to/repo"

        guide = SystemGenerationOutput.format_integration_guide(spec, repo_path)

        assert "QUICK START" in guide
        assert "DEVELOPMENT WORKFLOW" in guide
        assert repo_path in guide


class TestSystemGeneratorIntegration:
    """Integration tests for system generator."""

    def test_create_system_end_to_end(self):
        """Test complete system creation flow."""
        with TemporaryDirectory() as tmpdir:
            with TemporaryDirectory() as minddir:
                generator = SystemGenerator(Path(tmpdir), Path(minddir))

                system = generator.create(
                    name="Test System",
                    goal="Test goal",
                    features=["feature1", "feature2"],
                    tools=["tool1"],
                    system_type="subsystem",
                )

                # Verify system object
                assert system.system_id is not None
                assert system.spec.name == "Test System"
                assert system.repo_info is not None
                assert system.registry_entry is not None

                # Verify repository exists
                repo_path = Path(system.get_repo_path())
                assert repo_path.exists()

                # Verify registry entry
                registry_system = generator.registry.get_system(system.system_id)
                assert registry_system is not None
                assert registry_system["name"] == "test_system"

    def test_system_appears_in_registry(self):
        """Test that created system appears in registry."""
        with TemporaryDirectory() as tmpdir:
            with TemporaryDirectory() as minddir:
                generator = SystemGenerator(Path(tmpdir), Path(minddir))

                system1 = generator.create(
                    name="System 1",
                    goal="Goal 1",
                    features=["f1"],
                    tools=[],
                )

                system2 = generator.create(
                    name="System 2",
                    goal="Goal 2",
                    features=["f2"],
                    tools=[],
                )

                systems = generator.registry.list_systems()
                assert len(systems) == 2

                ids = [s["id"] for s in systems]
                assert system1.system_id in ids
                assert system2.system_id in ids

    def test_system_has_proper_structure(self):
        """Test that created system has proper structure."""
        with TemporaryDirectory() as tmpdir:
            with TemporaryDirectory() as minddir:
                generator = SystemGenerator(Path(tmpdir), Path(minddir))

                system = generator.create(
                    name="Test System",
                    goal="Test goal",
                    features=["f1"],
                    tools=["t1"],
                )

                repo_path = Path(system.get_repo_path())

                # Check .git
                assert (repo_path / ".git").exists()

                # Check README
                assert (repo_path / "README.md").exists()

                # Check metadata
                assert (repo_path / "system.metadata.json").exists()

                # Check directory structure
                for d in ["agents", "models", "blueprints", "core", "tests"]:
                    assert (repo_path / d).is_dir()

    def test_system_git_branches(self):
        """Test that system has main and dev branches."""
        with TemporaryDirectory() as tmpdir:
            with TemporaryDirectory() as minddir:
                generator = SystemGenerator(Path(tmpdir), Path(minddir))

                system = generator.create(
                    name="Test System",
                    goal="Test goal",
                    features=["f1"],
                    tools=[],
                )

                repo_path = Path(system.get_repo_path())

                # Check branches exist
                result = subprocess.run(
                    ["git", "branch", "-a"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                )

                assert "main" in result.stdout
                assert "dev" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
