"""Abstract LLM provider interface for Mind agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt.

        Args:
            prompt: Input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text
        """
        pass

    @abstractmethod
    def parse_task(self, description: str) -> Dict[str, Any]:
        """Parse natural language task description into structured format.

        Args:
            description: Natural language task description

        Returns:
            Structured task specification
        """
        pass

    @abstractmethod
    def create_plan(self, goal: str, available_agents: list) -> list:
        """Create an execution plan given a goal and available agents.

        Args:
            goal: High-level objective
            available_agents: List of available agents with their capabilities

        Returns:
            List of execution steps
        """
        pass

    @abstractmethod
    def reasoning(self, problem: str) -> str:
        """Reasoning/thinking about a problem.

        Args:
            problem: Problem to reason about

        Returns:
            Reasoning output
        """
        pass
