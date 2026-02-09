from .base_agent import BaseAgent


class EvolutionEngineAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="evolution_engine_agent", description="Improves systems over time."
        )

    def run(self, evaluation: dict) -> dict:
        improvements = []
        next_steps = []

        if evaluation.get("score", 0) < 4:
            improvements.append("Refine component boundaries.")
            next_steps.append("Add more detailed components to architecture.")

        if evaluation.get("issues"):
            next_steps.append("Address listed issues before implementation.")

        if not improvements and not next_steps:
            improvements.append("System is acceptable as a first iteration.")
            next_steps.append("Proceed to implementation phase.")

        evolution_plan = {
            "improvements": improvements,
            "next_steps": next_steps,
        }

        self.log(f"Evolution plan: {evolution_plan}")
        return evolution_plan
