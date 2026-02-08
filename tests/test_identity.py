from core.identity import MindIdentity


def test_identity():
    identity = MindIdentity()
    assert identity.name == "Mind"
