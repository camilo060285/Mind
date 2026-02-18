"""LLM Configuration for Mind agents."""

import os
from typing import Optional
from pathlib import Path
from .providers.llama_cpp_provider import LlamaCppProvider
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.ollama_provider import OllamaProvider
from .llm_interface import LLMProvider


# Environment variables for configuration
LLM_PROVIDER = os.getenv("MIND_LLM_PROVIDER", "llama_cpp")
LLM_MODEL = os.getenv("MIND_LLM_MODEL", "phi")  # "phi" or "qwen"
LLAMA_BIN = os.getenv("MIND_LLAMA_BIN", None)
MODELS_DIR = os.getenv("MIND_MODELS_DIR", None)
OPENAI_API_KEY = os.getenv("MIND_OPENAI_API_KEY", None)
OPENAI_BASE_URL = os.getenv("MIND_OPENAI_BASE_URL", "https://api.openai.com/v1")
ANTHROPIC_API_KEY = os.getenv("MIND_ANTHROPIC_API_KEY", None)
ANTHROPIC_BASE_URL = os.getenv("MIND_ANTHROPIC_BASE_URL", "https://api.anthropic.com")
OLLAMA_BASE_URL = os.getenv("MIND_OLLAMA_BASE_URL", "http://localhost:11434")


def get_llm_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    """Get LLM provider instance based on configuration.

    Args:
        provider: Provider name ("llama_cpp", "openai", "anthropic", "ollama").
            Falls back to env var.
        model: Model name. Falls back to env var.

    Returns:
        Configured LLM provider

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider or LLM_PROVIDER
    model = model or LLM_MODEL

    if provider == "llama_cpp":
        llama_bin: Optional[Path] = None
        if LLAMA_BIN:
            llama_bin = Path(LLAMA_BIN)

        models_dir: Optional[Path] = None
        if MODELS_DIR:
            models_dir = Path(MODELS_DIR)

        return LlamaCppProvider(model=model, llama_bin=llama_bin, models_dir=models_dir)

    if provider == "openai":
        if not OPENAI_API_KEY:
            raise ValueError("MIND_OPENAI_API_KEY is required for provider 'openai'")
        return OpenAIProvider(
            api_key=OPENAI_API_KEY,
            model=model,
            base_url=OPENAI_BASE_URL,
        )

    if provider == "anthropic":
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "MIND_ANTHROPIC_API_KEY is required for provider 'anthropic'"
            )
        return AnthropicProvider(
            api_key=ANTHROPIC_API_KEY,
            model=model,
            base_url=ANTHROPIC_BASE_URL,
        )

    if provider == "ollama":
        return OllamaProvider(
            model=model,
            base_url=OLLAMA_BASE_URL,
        )

    raise ValueError(f"Unknown LLM provider: {provider}")


# Default instance for easy import
default_llm: Optional[LLMProvider] = None


def init_llm(
    provider: Optional[str] = None, model: Optional[str] = None
) -> LLMProvider:
    """Initialize default LLM provider.

    Args:
        provider: Provider name
        model: Model name

    Returns:
        Initialized provider
    """
    global default_llm
    default_llm = get_llm_provider(provider=provider, model=model)
    return default_llm


def get_default_llm() -> LLMProvider:
    """Get default LLM provider instance.

    Returns:
        Default LLM provider (initializes if needed)
    """
    global default_llm
    if default_llm is None:
        default_llm = get_llm_provider()
    return default_llm
