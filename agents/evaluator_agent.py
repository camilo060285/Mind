from agents.base_agent import BaseAgent

class EvaluatorAgent(BaseAgent):
    """Evaluates system performance and completeness."""

    def __init__(self):
        super().__init__(
            name="evaluator_agent",
            description="Evaluates system quality and suggests improvements."
        )

    def run(self, system_output: dict) -> dict:
        evaluation = {
            "score": None,
            "issues": [],
            "suggestions": [],
        }
        self.log(f"Evaluation: {evaluation}")
        return evaluation
