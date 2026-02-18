"""Ollama HTTP provider for local/remote model execution."""

from __future__ import annotations

import json
import re
from typing import Any, cast

import requests  # type: ignore[import-untyped]

from ..llm_interface import LLMProvider


class OllamaProvider(LLMProvider):
    """LLM provider using Ollama's /api/generate endpoint."""

    def __init__(
        self,
        model: str = "qwen2.5:7b-instruct",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        temperature: float = 0.7,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature

    def _generate_once(self, prompt: str, n_predict: int = 400) -> str:
        url = f"{self.base_url}/api/generate"
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": n_predict,
            },
        }

        response = requests.post(url, json=payload, timeout=self.timeout)
        if response.status_code >= 400:
            raise RuntimeError(
                f"Ollama request failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        return str(data.get("response", "")).strip()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        n_predict = int(kwargs.get("n_predict", kwargs.get("max_tokens", 400)))
        return self._generate_once(prompt, n_predict=n_predict)

    def parse_task(self, description: str) -> dict[str, Any]:
        prompt = f"""Parse the following task description into JSON format with:
- task_type (string)
- goal (string)
- subtasks (list of strings)
- parameters (dict)

Task: {description}

JSON:"""

        output = self.generate(prompt, n_predict=350)

        try:
            json_match = re.search(r"\{.*\}", output, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        return {
            "task_type": "generic",
            "goal": description,
            "subtasks": [],
            "parameters": {},
        }

    def create_plan(self, goal: str, available_agents: list[Any]) -> list[str]:
        labels: list[str] = []
        for agent in available_agents:
            if not isinstance(agent, dict):
                continue
            agent_dict = cast(dict[str, Any], agent)
            labels.append(f"- {agent_dict.get('name')}: {agent_dict.get('role')}")

        agents_str = "\n".join(labels)

        prompt = f"""Create an execution plan to achieve this goal:
Goal: {goal}

Available agents:
{agents_str}

Create a step-by-step plan. Format each step as:
1. [Agent Name]: [Action] -> [Expected Output]
2. ...

Plan:"""

        output = self.generate(prompt, n_predict=500)

        steps: list[str] = []
        for line in output.split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                steps.append(line)

        return steps if steps else [f"Execute with any available agent: {goal}"]

    def reasoning(self, problem: str) -> str:
        prompt = f"""Think step by step about this problem:
{problem}

Reasoning:"""
        return self.generate(prompt, n_predict=400)

    def __repr__(self) -> str:
        return f"OllamaProvider(model={self.model})"
