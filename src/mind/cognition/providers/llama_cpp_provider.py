"""LLM Provider using llama.cpp with local models (Phi, Qwen)."""

import subprocess
import json
import re
from pathlib import Path
from typing import Any, Dict, Optional
from ..llm_interface import LLMProvider


class LlamaCppProvider(LLMProvider):
    """
    LLM Provider using llama.cpp for local inference.

    Supports:
    - Phi (lightweight, fast)
    - Qwen (more capable reasoning)
    - Works on Raspberry Pi with ARM CPU
    - Zero cloud costs
    """

    def __init__(
        self,
        model: str = "phi",
        llama_bin: Optional[Path] = None,
        models_dir: Optional[Path] = None,
        n_threads: int = 2,
        ctx_size: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ):
        """Initialize llama.cpp provider.

        Args:
            model: Model name ("phi" or "qwen")
            llama_bin: Path to llama-completion binary
            models_dir: Path to models directory
            n_threads: Number of threads for inference
            ctx_size: Context window size
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
        """
        self.model = model
        self.n_threads = n_threads
        self.ctx_size = ctx_size
        self.temperature = temperature
        self.top_p = top_p

        # Default paths (Raspberry Pi setup)
        if llama_bin is None:
            llama_bin = Path.home() / "llama.cpp" / "build" / "bin" / "llama-completion"
        if models_dir is None:
            models_dir = Path.home() / "local_llms" / "models"

        self.llama_bin = llama_bin
        self.models_dir = models_dir

        # Model mapping
        self.model_map = {
            "phi": models_dir / "llm_a" / "model.gguf",
            "qwen": models_dir / "llm_b" / "model.gguf",
        }

        # Validate setup
        self._validate_setup()

    def _validate_setup(self) -> None:
        """Validate that llama.cpp and models are available."""
        if not self.llama_bin.exists():
            raise RuntimeError(
                f"llama-completion not found at {self.llama_bin}\n"
                "Build llama.cpp: cd ~/llama.cpp && mkdir build && "
                "cd build && cmake .. && make"
            )

        model_path = self.model_map[self.model]
        if not model_path.exists():
            raise RuntimeError(
                f"Model '{self.model}' not found at {model_path}\n"
                f"Available models: {list(self.model_map.keys())}"
            )

    def _run_llama(self, prompt: str, n_predict: int = 200) -> str:
        """Run llama-completion with given prompt.

        Args:
            prompt: Input prompt
            n_predict: Max tokens to generate

        Returns:
            Generated output
        """
        model_path = self.model_map[self.model]

        cmd = [
            str(self.llama_bin),
            "--model",
            str(model_path),
            "--prompt",
            prompt,
            "--n-predict",
            str(n_predict),
            "--ctx-size",
            str(self.ctx_size),
            "--threads",
            str(self.n_threads),
            "--temp",
            str(self.temperature),
            "--top-p",
            str(self.top_p),
            "--no-display-prompt",
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if proc.returncode != 0:
                raise RuntimeError(f"llama-completion failed:\n{proc.stderr}")

            return proc.stdout.strip()
        except subprocess.TimeoutExpired:
            raise RuntimeError("llama-completion timed out")

    def generate(self, prompt: str, n_predict: int = 200, **kwargs) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt
            n_predict: Max tokens to generate
            **kwargs: Unused (for compatibility)

        Returns:
            Generated text
        """
        return self._run_llama(prompt, n_predict=n_predict)

    def parse_task(self, description: str) -> Dict[str, Any]:
        """Parse natural language task into structured format.

        Args:
            description: Natural language task description

        Returns:
            Structured task spec
        """
        prompt = f"""Parse the following task description into JSON format with:
- task_type (string)
- goal (string) 
- subtasks (list of strings)
- parameters (dict)

Task: {description}

JSON:"""

        output = self._run_llama(prompt, n_predict=300)

        # Extract JSON from output
        try:
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Fallback to basic parsing
        return {
            "task_type": "generic",
            "goal": description,
            "subtasks": [],
            "parameters": {},
        }

    def create_plan(self, goal: str, available_agents: list) -> list:
        """Create execution plan for a goal.

        Args:
            goal: High-level objective
            available_agents: List of available agents

        Returns:
            List of execution steps
        """
        agents_str = "\n".join(
            [f"- {a.get('name')}: {a.get('role')}" for a in available_agents]
        )

        prompt = f"""Create an execution plan to achieve this goal:
Goal: {goal}

Available agents:
{agents_str}

Create a step-by-step plan. Format each step as:
1. [Agent Name]: [Action] -> [Expected Output]
2. ...

Plan:"""

        output = self._run_llama(prompt, n_predict=500)

        # Parse steps
        steps = []
        for line in output.split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                steps.append(line)

        return steps if steps else [f"Execute with any available agent: {goal}"]

    def reasoning(self, problem: str) -> str:
        """Perform reasoning about a problem.

        Args:
            problem: Problem to reason about

        Returns:
            Reasoning output
        """
        prompt = f"""Think step by step about this problem:
{problem}

Reasoning:"""

        return self._run_llama(prompt, n_predict=400)

    def __repr__(self) -> str:
        return f"LlamaCppProvider(model={self.model}, threads={self.n_threads})"
