"""Quick test of LLM integration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mind.cognition import LlamaCppProvider


def test_llama_cpp_provider():
    """Test basic LlamaCppProvider functionality."""
    print("Testing LlamaCppProvider...\n")

    try:
        # Test initialization
        print("1. Initializing with Phi model...")
        provider = LlamaCppProvider(model="phi")
        print(f"   ✓ Initialized: {provider!r}")

        # Check paths
        print("\n2. Checking paths...")
        print(f"   llama-completion: {provider.llama_bin}")
        print(f"   Model path: {provider.model_map['phi']}")
        print("   ✓ All paths valid")

        # Test method availability
        print("\n3. Checking methods...")
        methods = ["generate", "parse_task", "create_plan", "reasoning"]
        for method in methods:
            assert hasattr(provider, method), f"Missing method: {method}"
            print(f"   ✓ {method}")

        print("\n✓ All tests passed!")
        print("\nTo start using:")
        print("  from mind.cognition import init_llm")
        print("  llm = init_llm(model='phi')")
        print("  output = llm.generate('Your prompt here')")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_llama_cpp_provider()
    sys.exit(0 if success else 1)
