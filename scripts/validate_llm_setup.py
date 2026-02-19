#!/usr/bin/env python3
"""Validate phi/llama.cpp setup before starting Mind or 2d_animation_studio.

Usage:
    python scripts/validate_llm_setup.py

Exit codes:
    0: All systems ready
    1: Critical missing components
    2: Non-critical warnings only
"""

import os
import sys
from pathlib import Path
from typing import Callable


def check_llama_binary() -> bool:
    """Check if llama-completion binary exists."""
    llama_bin = Path.home() / "llama.cpp" / "build" / "bin" / "llama-completion"
    custom_bin = os.getenv("MIND_LLAMA_BIN")
    if custom_bin:
        llama_bin = Path(custom_bin)

    if llama_bin.exists():
        print(f"✓ llama.cpp binary found: {llama_bin}")
        return True
    else:
        print(f"✗ CRITICAL: llama-completion not found at {llama_bin}")
        print(
            "  Build with: cd ~/llama.cpp && mkdir -p build && cd build && cmake .. && make"
        )
        return False


def check_models_dir() -> bool:
    """Check if models directory exists."""
    models_dir = Path.home() / "local_llms" / "models"
    custom_dir = os.getenv("MIND_MODELS_DIR")
    if custom_dir:
        models_dir = Path(custom_dir)

    if models_dir.exists():
        print(f"✓ Models directory found: {models_dir}")
        return True
    else:
        print(f"✗ CRITICAL: Models directory not found at {models_dir}")
        print(f"  Create with: mkdir -p {models_dir}/llm_a {models_dir}/llm_b")
        return False


def check_phi_model() -> bool:
    """Check if phi model exists."""
    models_dir = Path.home() / "local_llms" / "models"
    custom_dir = os.getenv("MIND_MODELS_DIR")
    if custom_dir:
        models_dir = Path(custom_dir)

    phi_path = models_dir / "llm_a" / "model.gguf"
    if phi_path.exists():
        size_mb = phi_path.stat().st_size / (1024 * 1024)
        print(f"✓ Phi model found: {phi_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"✗ CRITICAL: Phi model not found at {phi_path}")
        print(
            "  Download from: https://huggingface.co/lmstudio-community/Phi-3-mini-4k-instruct-GGUF"
        )
        print(f"  Extract as: {phi_path}")
        return False


def check_qwen_model() -> bool | None:
    """Check if qwen model exists (optional but useful)."""
    models_dir = Path.home() / "local_llms" / "models"
    custom_dir = os.getenv("MIND_MODELS_DIR")
    if custom_dir:
        models_dir = Path(custom_dir)

    qwen_path = models_dir / "llm_b" / "model.gguf"
    if qwen_path.exists():
        size_mb = qwen_path.stat().st_size / (1024 * 1024)
        print(f"✓ Qwen model found: {qwen_path} ({size_mb:.1f} MB)")
        return True
    else:
        print(f"⊘ Qwen model not found at {qwen_path} (optional)")
        print("  To use: Download from HuggingFace and extract to path above")
        return None


def check_env_config() -> bool:
    """Check environment configuration."""
    provider = os.getenv("MIND_LLM_PROVIDER", "llama_cpp")
    model = os.getenv("MIND_LLM_MODEL", "phi")
    print(f"✓ Configuration: provider={provider}, model={model}")
    return True


def main() -> int:
    """Run all validation checks."""
    print("=" * 60)
    print("Mind LLM Setup Validation")
    print("=" * 60)

    checks: list[tuple[str, Callable[[], bool | None]]] = [
        ("Environment Configuration", check_env_config),
        ("llama.cpp Binary", check_llama_binary),
        ("Models Directory", check_models_dir),
        ("Phi Model", check_phi_model),
        ("Qwen Model (optional)", check_qwen_model),
    ]

    results: list[tuple[str, bool | None]] = []
    for name, check_fn in checks:
        print(f"\nChecking {name}...")
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Error checking {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    critical: list[bool | None] = [
        ok
        for name, ok in results
        if name != "Qwen Model (optional)" and ok is not None and not ok
    ]
    warnings: list[bool | None] = [
        ok for name, ok in results if name == "Qwen Model (optional)" and ok is None
    ]

    if critical:
        print(f"✗ {len(critical)} critical issue(s) found. System cannot start.")
        return 1
    elif warnings:
        print(
            "⊘ Some optional components missing. System will work but may have reduced capabilities."
        )
        return 2
    else:
        print("✓ All systems ready for autonomous operation!")
        print("\nStart Mind with:")
        print("  python cli/studio.py --help")
        print("  python -m mind.cognition  # Direct API")
        return 0


if __name__ == "__main__":
    sys.exit(main())
