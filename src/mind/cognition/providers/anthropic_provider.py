"""Anthropic Messages API provider for Mind agents."""

from __future__ import annotations

import json
import re
from typing import Any, cast

import requests  # type: ignore[import-untyped]

from ..llm_interface import LLMProvider


class AnthropicProvider(LLMProvider):
    """LLM provider using Anthropic's Messages API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-latest",
        base_url: str = "https://api.anthropic.com",
        timeout: int = 60,
        temperature: float = 0.7,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature

    def _message(self, prompt: str, max_tokens: int = 400) -> str:
        url = f"{self.base_url}/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise RuntimeError(
                f"Anthropic request failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        content_items = data.get("content", [])
        if not content_items:
            return ""

        text_parts: list[str] = []
        for item in content_items:
            if not isinstance(item, dict):
                continue
            item_dict = cast(dict[str, Any], item)
            if item_dict.get("type") == "text":
                text = item_dict.get("text", "")
                if isinstance(text, str) and text:
                    text_parts.append(text)

        return "\n".join(text_parts).strip()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        max_tokens = int(kwargs.get("n_predict", kwargs.get("max_tokens", 400)))
        return self._message(prompt, max_tokens=max_tokens)

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
        return f"AnthropicProvider(model={self.model})"
