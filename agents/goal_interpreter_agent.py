from agents.base_agent import BaseAgent

class GoalInterpreterAgent(BaseAgent):
    """
    Interprets Cristian's goals, constraints, and emotional context.
    Converts human intention into structured system requirements.
    """

    def __init__(self):
        super().__init__(
            name="goal_interpreter_agent",
            description="Understands Cristian's intentions and converts them into structured goals."
        )

    def run(self, raw_input: str) -> dict:
        structured_goal = {
            "raw_text": raw_input,
            "intent": None,
            "constraints": [],
            "priority": "normal",
            "emotional_tone": None,
        }
        self.log(f"Interpreted goal: {structured_goal}")
        return structured_goal
