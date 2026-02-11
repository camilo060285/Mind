"""Example: Using LLM in Mind Agents."""

from mind.cognition import get_default_llm, init_llm

# Initialize with Phi (lightweight, fast)
llm = init_llm(provider="llama_cpp", model="phi")

# Or use Qwen (more capable reasoning)
# llm = init_llm(provider="llama_cpp", model="qwen")

# Or get the default configured instance
# llm = get_default_llm()


# Example 1: Simple text generation
def example_generate():
    prompt = "Explain what a multi-agent system is in one sentence."
    output = llm.generate(prompt, n_predict=100)
    print(f"Generated: {output}")


# Example 2: Parse natural language task
def example_parse_task():
    task_desc = (
        "I want to create an animated visualization of stock prices going up over time"
    )
    task = llm.parse_task(task_desc)
    print(f"Parsed task: {task}")


# Example 3: Create execution plan
def example_create_plan():
    goal = "Optimize database queries for faster response times"
    agents = [
        {"name": "DatabaseAnalyzer", "role": "analyze DB performance"},
        {"name": "IndexOptimizer", "role": "create and manage indexes"},
        {"name": "QueryPlanner", "role": "optimize query execution"},
    ]

    plan = llm.create_plan(goal, agents)
    print("Execution plan:")
    for step in plan:
        print(f"  {step}")


# Example 4: Reasoning about a problem
def example_reasoning():
    problem = "How can we reduce latency in a distributed system?"
    reasoning = llm.reasoning(problem)
    print(f"Reasoning:\n{reasoning}")


# Example 5: Using in an agent
def example_agent_usage():
    """Show how to integrate LLM into a custom agent."""
    from mind.agents.base_agent import BaseAgent

    class SmartAgent(BaseAgent):
        def __init__(self):
            super().__init__()
            self.llm = get_default_llm()

        def run(self, task_description: str):
            # Use LLM to understand the task
            task = self.llm.parse_task(task_description)

            # Use LLM to reason about execution
            reasoning = self.llm.reasoning(f"How should I execute: {task_description}")

            # Create a plan
            plan = self.llm.create_plan(
                task_description, [{"name": "Executor", "role": "execute tasks"}]
            )

            return {
                "task": task,
                "reasoning": reasoning,
                "plan": plan,
            }

    agent = SmartAgent()
    result = agent.run("Create a dashboard showing data analytics")
    print(result)


if __name__ == "__main__":
    print("Mind LLM Integration Examples\n")
    print("=" * 50)

    print("\n1. Generate text:")
    example_generate()

    print("\n2. Parse task:")
    example_parse_task()

    print("\n3. Create plan:")
    example_create_plan()

    print("\n4. Reasoning:")
    example_reasoning()

    print("\n5. Agent integration:")
    example_agent_usage()
