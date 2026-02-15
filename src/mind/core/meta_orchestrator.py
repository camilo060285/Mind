from .blueprint_loader import BlueprintLoader
from ..agents.goal_interpreter_agent import GoalInterpreterAgent
from ..agents.system_designer_agent import SystemDesignerAgent
from ..agents.boundary_setter_agent import BoundarySetterAgent
from ..agents.tool_selector_agent import ToolSelectorAgent
from ..agents.agent_architect_agent import AgentArchitectAgent
from ..agents.execution_planner_agent import ExecutionPlannerAgent
from ..agents.evaluator_agent import EvaluatorAgent
from ..agents.evolution_engine_agent import EvolutionEngineAgent
from ..agents.delegator_agent import DelegatorAgent


class MetaOrchestrator:
    def __init__(self):
        self.loader = BlueprintLoader()
        self.agents = {
            "goal_interpreter_agent": GoalInterpreterAgent(),
            "system_designer_agent": SystemDesignerAgent(),
            "boundary_setter_agent": BoundarySetterAgent(),
            "tool_selector_agent": ToolSelectorAgent(),
            "agent_architect_agent": AgentArchitectAgent(),
            "execution_planner_agent": ExecutionPlannerAgent(),
            "evaluator_agent": EvaluatorAgent(),
            "evolution_engine_agent": EvolutionEngineAgent(),
            "delegator_agent": DelegatorAgent(),
        }

    def run_blueprint(self, path: str) -> dict:
        blueprint = self.loader.load(path)
        goal_text = blueprint["goal"]["raw_text"]
        constraints = blueprint.get("constraints", [])
        context = None

        for step in blueprint["pipeline"]:
            agent_name = step["agent"]
            if agent_name not in self.agents:
                raise ValueError(f"Unknown agent in pipeline: {agent_name}")
            agent = self.agents[agent_name]

            if agent_name == "goal_interpreter_agent":
                context = agent.run(goal_text)
            elif agent_name == "boundary_setter_agent":
                context = agent.run(context, constraints)
            else:
                context = agent.run(context)

        return {
            "final_output": context,
            "goal": goal_text,
            "constraints": constraints,
        }
