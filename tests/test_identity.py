from mind.core.identity import MindIdentity


class TestMindIdentity:
    """Test suite for MindIdentity."""

    def test_identity_initialization(self):
        """Test identity object initialization."""
        identity = MindIdentity()
        assert identity is not None

    def test_identity_name(self):
        """Test identity name."""
        identity = MindIdentity()
        assert identity.name == "Mind"

    def test_identity_version(self):
        """Test identity version."""
        identity = MindIdentity()
        assert identity.version == "0.1.0"
        assert isinstance(identity.version, str)

    def test_identity_author(self):
        """Test identity author."""
        identity = MindIdentity()
        assert identity.author == "Cristian"

    def test_identity_description(self):
        """Test identity has meaningful description."""
        identity = MindIdentity()
        assert identity.description is not None
        assert len(identity.description) > 0
        assert "privacy" in identity.description.lower()

    def test_identity_capabilities(self):
        """Test identity lists capabilities."""
        identity = MindIdentity()
        assert identity.capabilities is not None
        assert isinstance(identity.capabilities, list)
        assert len(identity.capabilities) > 0
        # Check for key capabilities
        capability_names = [c.lower() for c in identity.capabilities]
        assert any("blueprint" in c for c in capability_names)
        assert any("agent" in c or "workflow" in c for c in capability_names)

    def test_identity_describe_method(self):
        """Test identity describe method."""
        identity = MindIdentity()
        description = identity.describe()
        assert isinstance(description, dict)
        assert "name" in description
        assert "version" in description
        assert "author" in description
        assert "description" in description
        assert "capabilities" in description
        assert description["name"] == "Mind"
        assert description["version"] == "0.1.0"

    def test_identity_describe_includes_all_fields(self):
        """Test that describe includes all required fields."""
        identity = MindIdentity()
        desc = identity.describe()
        required_fields = {"name", "version", "author", "description", "capabilities"}
        assert required_fields.issubset(set(desc.keys()))
