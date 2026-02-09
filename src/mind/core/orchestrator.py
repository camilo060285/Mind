from .identity import MindIdentity
from ..cognition.thinking_protocol import ThinkingProtocol
from ..agents.echo_agent import EchoAgent


class Orchestrator:
    """Coordinates agents, cognition, and blueprint execution."""

    def __init__(self):
        self.identity = MindIdentity()
        self.thinking = ThinkingProtocol()
        self.agents = {}
        self.register_agent("echo", EchoAgent("echo"))

    def register_agent(self, name, agent):
        self.agents[name] = agent

    def execute_step(self, step: dict):
        agent_name = step.get("agent")
        action = step.get("action")
        context = step.get("context", {})

        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not registered.")

        agent = self.agents[agent_name]
        return agent.act({"action": action, "context": context})

    def run(self, blueprint: dict):
        steps = blueprint.get("steps", [])
        results = []

        for step in steps:
            thought = self.thinking.think(step)
            result = self.execute_step(thought)
            results.append(result)

        return {
            "identity": self.identity.describe(),
            "results": results,
        }
