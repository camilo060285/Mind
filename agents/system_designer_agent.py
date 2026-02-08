from agents.base_agent import BaseAgent


class SystemDesignerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="system_designer_agent",
            description="Creates architectural blueprints for new systems.",
        )

    def run(self, interpreted_goal: dict) -> dict:
        intent = interpreted_goal.get("intent") or "build_subsystem"

        components = [
            "input_handler",
            "reasoning_core",
            "agent_orchestrator",
            "storage_layer",
            "interface_layer",
        ]

        data_flow = [
            "user_input -> input_handler",
            "input_handler -> reasoning_core",
            "reasoning_core -> agent_orchestrator",
            "agent_orchestrator -> storage_layer",
            "agent_orchestrator -> interface_layer",
        ]

        architecture = {
            "name": f"{intent}_architecture",
            "components": components,
            "data_flow": data_flow,
            "tradeoffs": ["modularity vs. complexity"],
            "complexity": "medium",
        }

        self.log(f"Proposed architecture: {architecture}")
        return architecture
