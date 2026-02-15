"""Output formatting for system generation results.

Provides human-friendly and machine-readable output for system
generation results.
"""

from typing import Any, Dict
from datetime import datetime


class SystemGenerationOutput:
    """Formats system generation output."""

    @staticmethod
    def format_console_output(
        repo_info: Dict[str, Any],
        system_spec: Dict[str, Any],
        readme_content: str,
    ) -> str:
        """Format output for console/terminal display.

        Args:
            repo_info: Repository creation information
            system_spec: System specification
            readme_content: Generated README content

        Returns:
            Formatted console output string
        """
        output = f"""
╔════════════════════════════════════════════════════════════════╗
║           SYSTEM GENERATION COMPLETE                           ║
╚════════════════════════════════════════════════════════════════╝

✅ Repository Created Successfully

📍 Repository Location
   Path: {repo_info.get('repo_path')}
   URL:  {repo_info.get('repo_url')}

🆔 System Information
   ID:          {repo_info.get('system_id')}
   Name:        {repo_info.get('system_name')}
   Type:        {repo_info.get('system_type')}
   Created:     {repo_info.get('created_at')}

🔗 Git Details
   Branches:    {', '.join(repo_info.get('branches', []))}
   Initial Commit: {repo_info.get('initial_commit', 'N/A')[:8]}...
   Status:      {repo_info.get('status')}

📋 System Specification
   Name:        {system_spec.get('name')}
   Goal:        {system_spec.get('goal')}
   Features:    {len(system_spec.get('features', []))} configured
   Components:  {len(system_spec.get('components', []))} total
   Tools:       {len(system_spec.get('tools', []))} integrations

📁 Project Structure
   ├── agents/         (Agent implementations)
   ├── models/         (Data models)
   ├── blueprints/     (Workflow definitions)
   ├── core/           (Orchestration logic)
   ├── tests/          (Test suite)
   ├── data/           (Runtime data)
   ├── config/         (Configuration)
   ├── scripts/        (Utilities)
   ├── docs/           (Documentation)
   ├── .gitignore      (Generated)
   ├── README.md       (Generated)
   └── system.metadata.json

🚀 Next Steps

1. Navigate to repository:
   cd {repo_info.get('repo_path')}

2. Review system documentation:
   cat README.md

3. Check system configuration:
   cat system.metadata.json

4. Install dependencies (if applicable):
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

5. Run the system:
   python cli.py

📚 Key Files

✦ README.md
  Complete system documentation and user guide

✦ system.metadata.json
  System creation metadata, specification, and dependencies

✦ blueprints/
  Workflow definitions (YAML format)

✦ agents/
  Agent implementations for system tasks

✦ core/orchestrator.py
  Main orchestration and coordination logic

🔄 Git Workflow

Main Branch:     Stable releases
Dev Branch:      Active development

To switch branches:
  cd {repo_info.get('repo_path')}
  git checkout dev    # for development
  git checkout main   # for stable

📦 Important Notes

✓ This repository is COMPLETELY INDEPENDENT from Mind
✓ You have full control over the code and history
✓ Mind only stores a reference in its registry
✓ You can fork, modify, and deploy independently
✓ Branching model supports parallel development

🔗 Integration with Mind

Mind stores only:
  • Reference to this repository
  • System metadata (in Mind registry)
  • Orchestration pointers
  • No system code is stored in Mind

This maintains clean architecture boundaries and gives you complete
sovereignty over your generated systems.

═════════════════════════════════════════════════════════════════

Generated: {datetime.now().isoformat()}
Mind Meta-System

═════════════════════════════════════════════════════════════════
"""
        return output

    @staticmethod
    def format_json_output(
        repo_info: Dict[str, Any],
        system_spec: Dict[str, Any],
        registry_entry: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Format output as JSON for machine consumption.

        Args:
            repo_info: Repository creation information
            system_spec: System specification
            registry_entry: Registry entry

        Returns:
            Dictionary formatted for JSON serialization
        """
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "repository": repo_info,
            "specification": system_spec,
            "registry_entry": registry_entry,
            "instructions": {
                "navigate": f"cd {repo_info.get('repo_path')}",
                "view_readme": "cat README.md",
                "view_metadata": "cat system.metadata.json",
                "run_system": "python cli.py",
                "switch_to_dev": "git checkout dev",
            },
        }

    @staticmethod
    def format_manifest_output(
        repo_info: Dict[str, Any],
        system_spec: Dict[str, Any],
    ) -> str:
        """Format brief manifest for quick reference.

        Args:
            repo_info: Repository creation information
            system_spec: System specification

        Returns:
            Manifest text
        """
        components_str = "\n  - ".join(
            [f"{c['name']} ({c['role']})" for c in system_spec.get("components", [])]
        )
        features_str = "\n  - ".join(system_spec.get("features", []))
        tools_str = "\n  - ".join(system_spec.get("tools", []))

        manifest = f"""
System Manifest
===============

ID:              {repo_info.get('system_id')}
Name:            {repo_info.get('system_name')}
Type:            {repo_info.get('system_type')}
Repository:      {repo_info.get('repo_path')}
Status:          {repo_info.get('status')}

Specification
=============
Goal:            {system_spec.get('goal')}
Description:     {system_spec.get('description')}
Version:         {system_spec.get('version', 'N/A')}

Components
==========
  - {components_str if components_str else 'None'}

Features
========
  - {features_str if features_str else 'None'}

Tools
=====
  - {tools_str if tools_str else 'None'}

Created: {repo_info.get('created_at')}
"""
        return manifest

    @staticmethod
    def format_integration_guide(
        system_spec: Dict[str, Any],
        repo_path: str,
    ) -> str:
        """Format integration guide for the generated system.

        Args:
            system_spec: System specification
            repo_path: Path to generated system repository

        Returns:
            Integration guide text
        """
        guide = f"""
Integration Guide
==================

System: {system_spec.get('name')}
Repository: {repo_path}

QUICK START
-----------

1. Navigate to system:
   $ cd {repo_path}

2. Create virtual environment:
   $ python -m venv venv
   $ source venv/bin/activate  # or on Windows: venv\\Scripts\\activate

3. Install dependencies:
   $ pip install -r requirements.txt

4. Review documentation:
   $ cat README.md

5. Check system metadata:
   $ cat system.metadata.json

6. Run the system:
   $ python cli.py

DEVELOPMENT WORKFLOW
--------------------

1. Create feature branch:
   $ git checkout -b feature/my-feature

2. Make changes to agents, blueprints, or models

3. Add and commit changes:
   $ git add .
   $ git commit -m "Add my feature"

4. Switch to dev branch for integration:
   $ git checkout dev
   $ git merge feature/my-feature

5. Test on main when stable:
   $ git checkout main
   $ git merge dev

EXTENDING THE SYSTEM
--------------------

Add New Agent:
  1. Create agents/my_agent.py
  2. Extend BaseAgent class
  3. Register in core/orchestrator.py
  4. Add workflow steps in blueprints/

Add External Tool:
  1. Create agents/tools/my_tool.py
  2. Define inputs/outputs
  3. Configure in config/
  4. Update blueprints to use tool

Modify Workflows:
  1. Edit YAML files in blueprints/
  2. Test with existing agents
  3. Add new blueprint definitions as needed
  4. Commit changes to appropriate branch

TROUBLESHOOTING
---------------

System won't start:
  - Check Python version (3.10+ required)
  - Verify all dependencies installed
  - Review logs in the system

Missing dependencies:
  - Run: pip install -r requirements.txt
  - Or: pip install <missing-package>

Git issues:
  - Check status: git status
  - View history: git log
  - Help: git help <command>

MONITORING
----------

Monitor system execution:
  $ python scripts/monitor.py

View system state:
  $ cat data/system_state.json

Check metrics:
  $ cat data/metrics.json

IMPORTANT ARCHITECTURE NOTES
----------------------------

• This system is INDEPENDENT from Mind
• You control this repository completely
• Mind only has a reference (in ~/.mind/)
• Clone, fork, or redistribute as you choose
• No automatic sync with Mind necessary
• Architecture boundaries are cleanly defined

QUESTIONS OR ISSUES?
---------------------

1. Check README.md for system-specific info
2. Review system.metadata.json for dependencies
3. Examine agents/ and blueprints/ for examples
4. Add debug logging to agents for troubleshooting
"""
        return guide
