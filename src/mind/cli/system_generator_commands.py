"""CLI commands for system generation."""

import json

from mind.system_generator import SystemGenerator


class SystemGeneratorCommandHandler:
    """Handler for system generation commands."""

    def __init__(self):
        """Initialize handler."""
        self.generator = SystemGenerator()

    def handle_create_system(self, args: str = "") -> str:
        """Create a new autonomous system.

        Usage: create_system <name> <goal> <features> <tools>
        Example: create_system "2D Studio" "Generate animations" "concept,animation,composite" "stable_diffusion,blender,ffmpeg"
        """
        parts = args.split("|")
        if len(parts) < 4:
            return "Usage: create_system <name>|<goal>|<features>|<tools>"

        name = parts[0].strip().strip("\"'")
        goal = parts[1].strip().strip("\"'")
        features = [f.strip() for f in parts[2].split(",")]
        tools = [t.strip() for t in parts[3].split(",")]

        try:
            system = self.generator.create(
                name=name,
                goal=goal,
                features=features,
                tools=tools,
            )

            info = system.get_info()
            output = f"\n✓ System Created: {info['name']}\n"
            output += f"  ID: {info['system_id']}\n"
            output += f"  Root: {info['root']}\n"
            output += f"  Components: {info['components']}\n"
            output += f"  Workflows: {info['workflows']}\n"

            return output
        except Exception as e:
            return f"Error creating system: {str(e)}"

    def handle_list_systems(self, args: str = "") -> str:
        """List all generated systems.

        Usage: list_systems
        """
        base_dir = self.generator.base_dir
        if not base_dir.exists():
            return "No systems generated yet."

        systems = list(base_dir.glob("*"))
        if not systems:
            return "No systems found."

        output = "\nGenerated Systems:\n"
        for sys_dir in systems:
            manifest_file = sys_dir / "manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r") as f:
                        manifest = json.load(f)
                    output += f"\n  {manifest['name']}\n"
                    output += f"    ID: {manifest['system_id']}\n"
                    output += f"    Goal: {manifest['goal']}\n"
                    output += f"    Path: {sys_dir}\n"
                except Exception:
                    pass

        return output

    def handle_system_info(self, args: str = "") -> str:
        """Get info about a generated system.

        Usage: system_info <system_id>
        """
        if not args.strip():
            return "Usage: system_info <system_id>"

        system_id = args.strip()
        base_dir = self.generator.base_dir

        for sys_dir in base_dir.glob("*"):
            manifest_file = sys_dir / "manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r") as f:
                        manifest = json.load(f)
                    if manifest["system_id"] == system_id:
                        spec = manifest["spec"]
                        output = f"\n{spec['name']}\n"
                        output += f"Goal: {spec['goal']}\n"
                        output += f"Features: {', '.join(spec['features'])}\n"
                        output += f"Tools: {', '.join(spec['tools'])}\n"
                        output += f"Components: {len(spec['components'])}\n"
                        return output
                except Exception:
                    pass

        return f"System not found: {system_id}"

    def handle_show_blueprint(self, args: str = "") -> str:
        """Show blueprint for a system.

        Usage: show_blueprint <system_id>
        """
        if not args.strip():
            return "Usage: show_blueprint <system_id>"

        system_id = args.strip()
        base_dir = self.generator.base_dir

        for sys_dir in base_dir.glob("*"):
            manifest_file = sys_dir / "manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file, "r") as f:
                        manifest = json.load(f)
                    if manifest["system_id"] == system_id:
                        blueprint_file = (
                            sys_dir / "blueprints" / "default_workflow.yaml"
                        )
                        if blueprint_file.exists():
                            return f"\n{blueprint_file.read_text()}\n"
                except Exception:
                    pass

        return f"Blueprint not found for system: {system_id}"
