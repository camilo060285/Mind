# 📘 Blueprint System

Blueprints are YAML files that describe declarative workflows for Mind.

They define:

- the goal
- constraints
- the agent pipeline
- execution order
- context propagation rules

Blueprints are the **declarative heart** of Mind.

---

## 🧩 Example Blueprint

```yaml
goal:
  raw_text: "Design a modular agent system for Mind."

constraints:
  - "Must be privacy‑first"
  - "Must be modular"

pipeline:
  - agent: goal_interpreter_agent
  - agent: boundary_setter_agent
  - agent: system_designer_agent
  - agent: agent_architect_agent
  - agent: execution_planner_agent
  - agent: evaluator_agent
  - agent: evolution_engine_agent

🧱 Blueprint Structure
`goal`
The raw user intent.
`constraints`
Optional list of requirements.
`pipeline`
Ordered list of agents to execute.
Each step references an agent by name.

🧪 Validation
Blueprints are loaded by:

core/blueprint_loader.py

Future enhancements include:
• schema validation
• blueprint linting
• type checking
• blueprint evolution


---

# 🧩 `docs/agents.md`

```markdown
# 🧩 Agents

Agents are modular, pluggable components that perform specific tasks.

All agents inherit from:

agents/base_agent.py


Agents are:

- stateless
- composable
- sandboxed
- easy to extend

---

## 🛠 Creating a New Agent

1. Create a file in `agents/`
2. Inherit from `BaseAgent`
3. Implement `run()`

Example:

```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def run(self, context):
        return {"result": "Hello from MyAgent"}

🔌 Registering an Agent
Add it to MetaOrchestrator:

self.agents["my_agent"] = MyAgent()

🧠 Built‑in Agents
Mind includes:
• GoalInterpreterAgent
• BoundarySetterAgent
• SystemDesignerAgent
• ToolSelectorAgent
• AgentArchitectAgent
• ExecutionPlannerAgent
• EvaluatorAgent
• EvolutionEngineAgent
• DelegatorAgent
These form the meta‑design pipeline.


---

# 🎛 `docs/orchestrators.md`

```markdown
# 🎛 Orchestrators

Mind has two orchestrators:

---

## 1. MetaOrchestrator (`core/meta_orchestrator.py`)

Executes blueprint pipelines step‑by‑step.

Responsibilities:

- load blueprint
- execute agents in order
- propagate context
- return final output

This orchestrator powers the meta‑design pipeline.

---

## 2. MindOrchestrator (`core/mind_orchestrator.py`)

Runs the full lifecycle:

think → act → reflect → evolve


Responsibilities:

- execute blueprints
- store memory
- evolve over time
- unify all layers
- provide a stable interface for the CLI

This orchestrator is the **brain** of Mind.
