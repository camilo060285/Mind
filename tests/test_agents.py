from agents.goal_interpreter_agent import GoalInterpreterAgent


def test_goal_interpreter_basic():
    agent = GoalInterpreterAgent()
    result = agent.run("Build a subsystem for Mind.")
    assert isinstance(result, dict)
    assert "raw_text" in result
