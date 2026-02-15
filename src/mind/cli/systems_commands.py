"""CLI commands for system generation.

Provides command-line interface for creating, listing, and managing
autonomously generated systems.
"""

import json
import click
from tabulate import tabulate

from mind.system_generator import SystemGenerator, SystemRegistry


@click.group()
def systems():
    """Manage autonomously generated systems."""
    pass


@systems.command()
@click.option("--name", prompt="System name", help="Name of the system")
@click.option("--goal", prompt="System goal", help="Goal/purpose of system")
@click.option(
    "--features",
    prompt="Features (comma-separated)",
    help="Features to include",
)
@click.option("--tools", default="", help="External tools (comma-separated)")
@click.option(
    "--type",
    default="agent-cluster",
    type=click.Choice(
        ["agent-cluster", "subsystem", "service", "pipeline", "monitor", "orchestrator"]
    ),
    help="Type of system",
)
@click.option(
    "--description",
    default="",
    help="Detailed description",
)
def create(name, goal, features, tools, type, description):
    """Create a new autonomous system repository.

    Mind will:
    1. Generate a unique Git repository
    2. Initialize folder structure
    3. Create README and documentation
    4. Register in Mind's system registry
    5. Output creation details and next steps
    """
    click.echo("\n" + "=" * 60)
    click.echo("CREATING AUTONOMOUS SYSTEM")
    click.echo("=" * 60 + "\n")

    try:
        # Parse features and tools
        features_list = [f.strip() for f in features.split(",") if f.strip()]
        tools_list = [t.strip() for t in tools.split(",") if t.strip()]

        generator = SystemGenerator()

        click.echo(f"System:      {name}")
        click.echo(f"Goal:        {goal}")
        click.echo(f"Type:        {type}")
        click.echo(f"Features:    {', '.join(features_list)}")
        click.echo(f"Tools:       {', '.join(tools_list) if tools_list else 'None'}")
        click.echo()

        click.echo("🔧 Generating system...", nl=False)
        click.echo(" ", nl=False)

        system = generator.create(
            name=name,
            goal=goal,
            features=features_list,
            tools=tools_list,
            description=description,
            system_type=type,
        )

        click.echo("✓\n")

        # Display results
        click.echo("✅ System created successfully!\n")
        click.echo(f"System ID:   {system.system_id}")
        click.echo(f"Repository: {system.get_repo_path()}\n")

        # Output summary
        click.echo(system.get_output_summary())

    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise


@systems.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json", "list"]),
    default="table",
    help="Output format",
)
def list(format):
    """List all generated systems."""
    registry = SystemRegistry()
    systems_list = registry.list_systems()

    if not systems_list:
        click.echo("No systems generated yet.")
        return

    if format == "json":
        click.echo(json.dumps(systems_list, indent=2))
    elif format == "list":
        for system in systems_list:
            click.echo(f"- {system['name']} ({system['id']})")
    else:  # table
        table_data = [
            [
                s["name"],
                s["id"],
                s["status"],
                s["repository"]["path"].split("/")[-1],
            ]
            for s in systems_list
        ]
        headers = ["Name", "ID", "Status", "Directory"]
        click.echo(tabulate(table_data, headers=headers))

    click.echo(f"\nTotal: {len(systems_list)} systems")


@systems.command()
@click.argument("system_id")
def info(system_id):
    """Show information about a specific system."""
    registry = SystemRegistry()
    system = registry.get_system(system_id)

    if not system:
        click.echo(f"System not found: {system_id}", err=True)
        return

    click.echo(f"\nSystem: {system['name']}")
    click.echo(f"ID:     {system['id']}")
    click.echo(f"Type:   {system['specification'].get('system_type', 'unknown')}")
    click.echo(f"Status: {system['status']}")
    click.echo(f"Repository: {system['repository']['path']}")

    spec = system["specification"]
    if spec.get("goal"):
        click.echo(f"Goal:   {spec['goal']}")

    if spec.get("features"):
        click.echo("\nFeatures:")
        for feature in spec["features"]:
            click.echo(f"  - {feature}")

    if spec.get("tools"):
        click.echo("\nTools:")
        for tool in spec["tools"]:
            click.echo(f"  - {tool}")

    click.echo(f"\nCreated: {system['created_at']}")


@systems.command()
@click.argument("system_id")
def archive(system_id):
    """Archive a system."""
    registry = SystemRegistry()
    system = registry.get_system(system_id)

    if not system:
        click.echo(f"System not found: {system_id}", err=True)
        return

    registry.archive_system(system_id)
    click.echo(f"✓ System archived: {system['name']}")


@systems.command()
def stats():
    """Show system generation statistics."""
    registry = SystemRegistry()
    summary = registry.get_registry_summary()

    click.echo("\n" + "=" * 40)
    click.echo("SYSTEM GENERATION STATISTICS")
    click.echo("=" * 40)
    click.echo(f"Total Systems:   {summary['total_systems']}")
    click.echo(f"Active:          {summary['active']}")
    click.echo(f"Archived:        {summary['archived']}")
    click.echo(f"Registry:        {summary['registry_path']}")
    click.echo(f"Last Updated:    {summary['last_updated']}")
    click.echo("=" * 40 + "\n")


@systems.command()
@click.argument("system_id")
@click.option(
    "--output",
    type=click.Path(),
    help="Output file (default: stdout)",
)
def export(system_id, output):
    """Export system registry entry."""
    registry = SystemRegistry()
    system = registry.get_system(system_id)

    if not system:
        click.echo(f"System not found: {system_id}", err=True)
        return

    output_str = json.dumps(system, indent=2)

    if output:
        with open(output, "w") as f:
            f.write(output_str)
        click.echo(f"✓ Exported to: {output}")
    else:
        click.echo(output_str)


if __name__ == "__main__":
    systems()
