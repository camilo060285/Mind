#!/bin/bash

###########################################################
# Mind CLI Installation Script
# 
# This script installs the Mind CLI tool globally
# so you can use "mind" commands from anywhere in the terminal
###########################################################

set -e

echo "=================================================="
echo "  Mind CLI Installation"
echo "=================================================="
echo ""

# Check if we're in the mind directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run this script from the Mind project root directory"
    echo "Usage: cd ~/mind && bash scripts/install_mind_cli.sh"
    exit 1
fi

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python version: $python_version"

# Install Mind in development mode
echo ""
echo "✓ Installing Mind CLI..."
pip install -e . > /dev/null 2>&1

# Verify installation
echo ""
echo "✓ Verifying installation..."

if command -v mind &> /dev/null; then
    echo "  Mind CLI command is available"
else
    echo "  Warning: 'mind' command not found in PATH"
    echo "  You may need to restart your terminal or add to PATH"
fi

# Create history directory
mkdir -p ~/.mind

# Test the CLI
echo ""
echo "✓ Testing Mind CLI..."

if mind status > /dev/null 2>&1; then
    echo "  ✓ Mind system is working!"
else
    echo "  ⚠ Warning: Could not access Mind system"
    echo "  Check that LLM models are available at:"
    echo "    ~/local_llms/models/llm_a/model.gguf"
    echo "    ~/local_llms/models/llm_b/model.gguf"
fi

# Create shell completion (optional)
echo ""
echo "✓ Setting up shell completion..."

# For zsh
if [ -f ~/.zshrc ]; then
    if ! grep -q "mind" ~/.zshrc; then
        cat >> ~/.zshrc << 'EOF'

# Mind CLI completion
eval "$(_MIND_COMPLETE=zsh_source mind)"
EOF
        echo "  Added Mind completion to ~/.zshrc"
    fi
fi

# For bash
if [ -f ~/.bashrc ]; then
    if ! grep -q "mind" ~/.bashrc; then
        cat >> ~/.bashrc << 'EOF'

# Mind CLI completion
eval "$(_MIND_COMPLETE=bash_source mind)"
EOF
        echo "  Added Mind completion to ~/.bashrc"
    fi
fi

echo ""
echo "=================================================="
echo "  Installation Complete! 🎉"
echo "=================================================="
echo ""
echo "Quick Start:"
echo ""
echo "  # Ask a question"
echo "  $ mind ask \"What is machine learning?\""
echo ""
echo "  # Get help with a problem"
echo "  $ mind help \"Error: module not found\""
echo ""
echo "  # Create a plan"
echo "  $ mind plan \"Build a website\""
echo ""
echo "  # Analyze a file"
echo "  $ mind analyze data.csv \"Find trends\""
echo ""
echo "  # Check status"
echo "  $ mind status"
echo ""
echo "  # See all commands"
echo "  $ mind --help"
echo ""
echo "Full documentation: https://github.com/camilo060285/Mind/docs/cli_guide.md"
echo ""
