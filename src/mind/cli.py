import argparse
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mind.core.mind_orchestrator import MindOrchestrator

# Get the blueprints directory relative to this module
BLUEPRINTS_DIR = Path(__file__).parent / "blueprints"

console = Console()


def run_blueprint(path: str):
    orchestrator = MindOrchestrator()
    result = orchestrator.run(path)
    console.print(Panel(str(result), title="Mind Run"))


def design_blueprint(path: str):
    orchestrator = MindOrchestrator()
    result = orchestrator.act(path)
    console.print(Panel(str(result), title="Mind Design"))


def evolve_system():
    orchestrator = MindOrchestrator()
    evo = orchestrator.evolve()
    console.print(Panel(str(evo), title="Mind Evolution"))


def list_blueprints():
    table = Table(title="Available Blueprints")
    table.add_column("Blueprint")
    if BLUEPRINTS_DIR.exists():
        for file in os.listdir(BLUEPRINTS_DIR):
            if file.endswith(".yaml") or file.endswith(".yml"):
                table.add_row(file)
    else:
        console.print(
            f"[yellow]Blueprints directory not found at {BLUEPRINTS_DIR}[/yellow]"
        )
        return
    console.print(table)


def mind_info():
    console.print(Panel("Mind — Agentic Meta-System\nVersion 0.1.0", title="Info"))


def main():
    parser = argparse.ArgumentParser(description="Mind CLI")
    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run", help="Run a blueprint")
    run_cmd.add_argument("blueprint")

    design_cmd = sub.add_parser("design", help="Run meta-design pipeline")
    design_cmd.add_argument("blueprint")

    sub.add_parser("evolve", help="Trigger evolution step")
    sub.add_parser("list", help="List available blueprints")
    sub.add_parser("info", help="Show system info")

    args = parser.parse_args()

    if args.command == "run":
        run_blueprint(args.blueprint)
    elif args.command == "design":
        design_blueprint(args.blueprint)
    elif args.command == "evolve":
        evolve_system()
    elif args.command == "list":
        list_blueprints()
    elif args.command == "info":
        mind_info()
    else:
        parser.print_help()
