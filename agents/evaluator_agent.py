from agents.base_agent import BaseAgent

class EvaluatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="evaluator_agent",
            description="Evaluates system quality and suggests improvements."
        )

    def run(self, system_output: dict) -> dict:
        components = system_output.get("components", [])
        complexity = system_output.get("complexity", "unknown")

        score = 0
        issues = []
        suggestions = []

        if len(components) >= 5:
            score += 3
        else:
            score += 1
            suggestions.append("Add more explicit components for clarity.")

        if complexity == "medium":
            score += 2
        elif complexity == "high":
            issues.append("System may be too complex to maintain.")
        else:
            suggestions.append("Clarify complexity level.")

        evaluation = {
            "score": score,
            "issues": issues,
            "suggestions": suggestions,
        }

        self.log(f"Evaluation: {evaluation}")
        return evaluation
