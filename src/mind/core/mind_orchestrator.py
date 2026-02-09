from .identity import MindIdentity
from .meta_orchestrator import MetaOrchestrator
from ..cognition.thinking_protocol import ThinkingProtocol
from ..utils.logger import get_logger


class MindOrchestrator:
    """
    The unified orchestrator for Mind.
    Handles:
    - lifecycle (think → act → reflect → evolve)
    - blueprint routing
    - meta-agent integration
    - memory
    """

    def __init__(self):
        self.identity = MindIdentity()
        self.meta = MetaOrchestrator()
        self.thinking = ThinkingProtocol()
        self.logger = get_logger("MindOrchestrator")

        # Simple in-memory store (can later be replaced with file/db)
        self.memory = {
            "goals": [],
            "architectures": [],
            "evaluations": [],
            "evolutions": [],
        }

    # -------------------------
    # Lifecycle
    # -------------------------

    def think(self, input_data: dict) -> dict:
        """Mind interprets and transforms input."""
        thought = self.thinking.think(input_data)
        self.logger.info(f"Thought: {thought}")
        return thought

    def act(self, blueprint_path: str) -> dict:
        """Mind executes a blueprint (meta or normal)."""
        result = self.meta.run_blueprint(blueprint_path)
        self.logger.info(f"Action result: {result}")
        return result

    def reflect(self, result: dict):
        """Mind stores results in memory."""
        self.memory["goals"].append(result.get("goal"))
        self.memory["architectures"].append(result.get("final_output"))
        self.logger.info("Reflection stored in memory.")

    def evolve(self):
        """Mind evolves based on memory."""
        evolution = {
            "total_goals": len(self.memory["goals"]),
            "total_architectures": len(self.memory["architectures"]),
        }
        self.memory["evolutions"].append(evolution)
        self.logger.info(f"Evolution step: {evolution}")
        return evolution

    # -------------------------
    # Unified run
    # -------------------------

    def run(self, blueprint_path: str) -> dict:
        """Full lifecycle execution."""
        self.logger.info("=== Mind Lifecycle Start ===")

        result = self.act(blueprint_path)
        self.reflect(result)
        evolution = self.evolve()

        final = {
            "identity": self.identity.describe(),
            "result": result,
            "evolution": evolution,
            "memory": self.memory,
        }

        self.logger.info("=== Mind Lifecycle Complete ===")
        return final
