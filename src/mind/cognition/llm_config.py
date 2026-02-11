"""LLM Configuration for Mind agents."""

import os
from typing import Optional
from pathlib import Path
from .providers.llama_cpp_provider import LlamaCppProvider
from .llm_interface import LLMProvider


# Environment variables for configuration
LLM_PROVIDER = os.getenv("MIND_LLM_PROVIDER", "llama_cpp")
LLM_MODEL = os.getenv("MIND_LLM_MODEL", "phi")  # "phi" or "qwen"
LLAMA_BIN = os.getenv("MIND_LLAMA_BIN", None)
MODELS_DIR = os.getenv("MIND_MODELS_DIR", None)


def get_llm_provider(
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMProvider:
    """Get LLM provider instance based on configuration.

    Args:
        provider: Provider name ("llama_cpp", etc.). Falls back to env var.
        model: Model name ("phi", "qwen"). Falls back to env var.

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
