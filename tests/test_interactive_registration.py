import pytest

from mind.cli.interactive import InteractiveMindShell


def test_distributed_commands_registered():
    shell = InteractiveMindShell()
    cmds = {c.name for c in shell.registry.list_commands()}

    expected = {
        "net_register",
        "net_list",
        "rpc_call",
        "lb_assign",
        "lb_stats",
        "state_set",
        "state_get",
    }

    # Ensure all expected distributed commands are present
    assert expected.issubset(cmds)


if __name__ == "__main__":
    pytest.main([__file__])
