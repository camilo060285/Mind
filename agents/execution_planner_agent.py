from agents.base_agent import BaseAgent

class ExecutionPlannerAgent(BaseAgent):
    """Breaks the system into phases and tasks."""

    def __init__(self):
        super().__init__(
            name="execution_planner_agent",
            description="Creates execution plans and timelines."
        )

    def run(self, architecture: dict) -> dict:
        architecture["execution_plan"] = {
            "phases": [],
            "tasks": [],
        }
        self.log("Created execution plan.")
        return architecture
