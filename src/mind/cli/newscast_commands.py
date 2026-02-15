"""CLI commands for NewscastStudio character and broadcast management."""

import click
from pathlib import Path
from tabulate import tabulate

from mind.agents.newscast_studio.character_manager import (
    CharacterAssetManager,
    create_default_newscast_characters,
)
from mind.agents.newscast_studio.broadcast_pipeline import NewscastBroadcastPipeline
from mind.cognition import get_default_llm


@click.group()
def newscast():
    """NewscastStudio commands for character and episode management."""
    pass


@newscast.group()
def character():
    """Manage NewscastStudio character assets."""
    pass


@character.command(name="create")
@click.argument("name")
@click.argument("description")
@click.option(
    "--tags", default="professional,friendly", help="Comma-separated style tags"
)
@click.option("--prompt", default=None, help="Custom base prompt (optional)")
def create_character(name, description, tags, prompt):
    """Create a new character asset.

    Examples:
        mind newscast character create "Sarah Nova" "professional news anchor, 30s"
        mind newscast character create "Alex Tech" "tech reporter" --tags "energetic,casual"
    """
    try:
        manager = CharacterAssetManager()

        style_tags = [tag.strip() for tag in tags.split(",")]

        character = manager.create_character(
            name=name,
            description=description,
            style_tags=style_tags,
            base_prompt=prompt,
        )

        click.echo("=" * 60)
        click.secho("✅ CHARACTER CREATED", fg="green", bold=True)
        click.echo("=" * 60)
        click.echo()
        click.echo(f"Name:        {character.name}")
        click.echo(f"ID:          {character.character_id}")
        click.echo(f"Seed:        {character.seed}")
        click.echo(f"Description: {character.description}")
        click.echo(f"Tags:        {', '.join(character.style_tags)}")
        click.echo()
        click.echo(f"Base Prompt: {character.base_prompt}")
        click.echo()
        click.secho(
            "💾 Character saved to ~/.mind/newscast_studio/character_assets/",
            fg="cyan",
        )

    except Exception as e:
        click.secho(f"❌ Error creating character: {e}", fg="red", err=True)
        raise click.Abort()


@character.command(name="list")
@click.option("--detailed", is_flag=True, help="Show detailed information")
def list_characters(detailed):
    """List all character assets."""
    try:
        manager = CharacterAssetManager()
        characters = manager.list_characters()

        if not characters:
            click.secho("📚 No characters created yet.", fg="yellow")
            click.echo()
            click.echo("Create one with:")
            click.secho(
                '  mind newscast character create "Name" "description"', fg="cyan"
            )
            return

        click.echo("=" * 60)
        click.secho("NEWSCAST CHARACTERS", fg="cyan", bold=True)
        click.echo("=" * 60)
        click.echo()

        if detailed:
            for char in characters:
                click.echo(f"📺 {char.name}")
                click.echo(f"   ID: {char.character_id}")
                click.echo(f"   Seed: {char.seed}")
                click.echo(f"   Description: {char.description}")
                click.echo(f"   Tags: {', '.join(char.style_tags)}")
                click.echo(f"   Used: {char.usage_count} times")
                click.echo(f"   Created: {char.created_at}")
                click.echo()
        else:
            # Table view
            table_data = []
            for char in characters:
                table_data.append(
                    [
                        char.name,
                        char.character_id[:8] + "...",
                        char.seed,
                        char.usage_count,
                        ", ".join(char.style_tags[:3]),
                    ]
                )

            headers = ["Name", "ID", "Seed", "Uses", "Tags"]
            click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
            click.echo()
            click.secho(f"Total: {len(characters)} characters", fg="cyan", bold=True)
            click.echo()
            click.echo("Use --detailed for more information")

    except Exception as e:
        click.secho(f"❌ Error listing characters: {e}", fg="red", err=True)
        raise click.Abort()


@character.command(name="show")
@click.argument("name")
def show_character(name):
    """Show detailed information about a character.

    Examples:
        mind newscast character show "Sarah Nova"
    """
    try:
        manager = CharacterAssetManager()
        character = manager.get_character_by_name(name)

        if not character:
            click.secho(f"❌ Character '{name}' not found.", fg="red")
            click.echo()
            click.echo("Available characters:")
            for char in manager.list_characters():
                click.echo(f"  • {char.name}")
            return

        click.echo("=" * 60)
        click.secho(f"CHARACTER: {character.name}", fg="cyan", bold=True)
        click.echo("=" * 60)
        click.echo()
        click.echo(f"ID:          {character.character_id}")
        click.echo(f"Seed:        {character.seed}")
        click.echo(f"Description: {character.description}")
        click.echo(f"Tags:        {', '.join(character.style_tags)}")
        click.echo()
        click.echo("Base Prompt:")
        click.echo(f"  {character.base_prompt}")
        click.echo()
        click.echo("Usage Statistics:")
        click.echo(f"  Times used:  {character.usage_count}")
        click.echo(f"  Created:     {character.created_at}")
        click.echo(f"  Last used:   {character.last_used}")

    except Exception as e:
        click.secho(f"❌ Error showing character: {e}", fg="red", err=True)
        raise click.Abort()


@character.command(name="scene")
@click.argument("name")  # Character name
@click.argument("scene")  # Scene description
@click.option("--details", default="", help="Additional scene details")
def generate_scene(name, scene, details):
    """Generate a scene prompt for a character.

    Examples:
        mind newscast character scene "Sarah Nova" "sitting at news desk"
        mind newscast character scene "Sarah Nova" "standing" --details "presenting graphics"
    """
    try:
        manager = CharacterAssetManager()
        character = manager.get_character_by_name(name)

        if not character:
            click.secho(f"❌ Character '{name}' not found.", fg="red")
            return

        scene_params = manager.generate_prompt_for_scene(
            character, scene, details if details else None
        )

        click.echo("=" * 60)
        click.secho("SCENE GENERATION", fg="cyan", bold=True)
        click.echo("=" * 60)
        click.echo()
        click.echo(f"Character:        {scene_params['character_name']}")
        click.echo(f"Seed:             {scene_params['seed']}")
        click.echo()
        click.echo("Full Prompt:")
        click.echo(f"  {scene_params['prompt']}")
        click.echo()
        click.echo("Negative Prompt:")
        click.echo(f"  {scene_params['negative_prompt']}")
        click.echo()
        click.secho(
            "💡 Use this seed and prompt with Stable Diffusion for consistent results!",
            fg="green",
        )

    except Exception as e:
        click.secho(f"❌ Error generating scene: {e}", fg="red", err=True)
        raise click.Abort()


@character.command(name="delete")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_character(name, yes):
    """Delete a character asset.

    Examples:
        mind newscast character delete "Old Character"
        mind newscast character delete "Test" --yes
    """
    try:
        manager = CharacterAssetManager()
        character = manager.get_character_by_name(name)

        if not character:
            click.secho(f"❌ Character '{name}' not found.", fg="red")
            return

        if not yes:
            click.echo(f"Delete character '{character.name}'?")
            click.echo(f"  ID: {character.character_id}")
            click.echo(f"  Used {character.usage_count} times")
            if not click.confirm("Are you sure?"):
                click.echo("Cancelled.")
                return

        manager.delete_character(character.character_id)
        click.secho(f"✅ Deleted character '{name}'", fg="green")

    except Exception as e:
        click.secho(f"❌ Error deleting character: {e}", fg="red", err=True)
        raise click.Abort()


@character.command(name="export")
@click.argument("name")
@click.argument("output_path")
def export_character(name, output_path):
    """Export a character to a JSON file.

    Examples:
        mind newscast character export "Sarah Nova" ~/sarah.json
    """
    try:
        manager = CharacterAssetManager()
        character = manager.get_character_by_name(name)

        if not character:
            click.secho(f"❌ Character '{name}' not found.", fg="red")
            return

        export_path = Path(output_path).expanduser()
        success = manager.export_character(character.character_id, export_path)

        if success:
            click.secho(f"✅ Exported '{name}' to {export_path}", fg="green")
        else:
            click.secho("❌ Export failed", fg="red")

    except Exception as e:
        click.secho(f"❌ Error exporting character: {e}", fg="red", err=True)
        raise click.Abort()


@character.command(name="import")
@click.argument("input_path")
def import_character(input_path):
    """Import a character from a JSON file.

    Examples:
        mind newscast character import ~/sarah.json
    """
    try:
        manager = CharacterAssetManager()
        import_path = Path(input_path).expanduser()

        if not import_path.exists():
            click.secho(f"❌ File not found: {import_path}", fg="red")
            return

        character = manager.import_character(import_path)

        if character:
            click.secho(f"✅ Imported character '{character.name}'", fg="green")
            click.echo(f"   ID: {character.character_id}")
            click.echo(f"   Seed: {character.seed}")
        else:
            click.secho("❌ Import failed", fg="red")

    except Exception as e:
        click.secho(f"❌ Error importing character: {e}", fg="red", err=True)
        raise click.Abort()


@newscast.group()
def broadcast():
    """Manage NewscastStudio broadcasts."""
    pass


@broadcast.command(name="create")
@click.argument("topic")
@click.option("--context", default="", help="Market context for broadcast")
@click.option("--duration", default=60, type=int, help="Duration in seconds")
@click.option("--tone", default="professional", help="Broadcast tone")
@click.option("--verbose", is_flag=True, help="Show detailed output")
def create_broadcast(topic, context, duration, tone, verbose):
    """Create a new market news broadcast.

    Examples:
        mind newscast broadcast create "Apple stock surge"
        mind newscast broadcast create "Tesla earnings" --context "Q4 results" --duration 90
        mind newscast broadcast create "Market crash" --tone "urgent" --verbose
    """
    try:
        if verbose:
            click.secho("[Initializing broadcast pipeline...]", fg="cyan")
            click.secho(f"Topic: {topic}", fg="cyan")
            click.secho(f"Duration: {duration}s", fg="cyan")
            click.secho(f"Tone: {tone}", fg="cyan")
            click.echo()

        llm = get_default_llm()
        pipeline = NewscastBroadcastPipeline(llm)

        if verbose:
            click.secho("[Creating broadcast...]", fg="yellow")

        result = pipeline.create_broadcast(
            topic=topic,
            context=context,
            duration=duration,
            tone=tone,
        )

        if result["status"] == "success":
            click.secho("✅ BROADCAST CREATED", fg="green", bold=True)
            click.echo()
            click.echo(f"ID: {result['broadcast_id']}")
            click.echo(f"Path: {result['broadcast_path']}")
            click.echo()
            click.secho(
                "💡 View with: mind newscast broadcast show " + result["broadcast_id"],
                fg="cyan",
            )
        else:
            click.secho(f"❌ Error: {result.get('error')}", fg="red")

    except Exception as e:
        click.secho(f"❌ Error creating broadcast: {e}", fg="red", err=True)
        raise click.Abort()


@broadcast.command(name="list")
@click.option("--limit", default=10, type=int, help="Number of broadcasts to show")
def list_broadcasts(limit):
    """List recent broadcasts."""
    try:
        llm = get_default_llm()
        pipeline = NewscastBroadcastPipeline(llm)

        broadcasts = pipeline.list_broadcasts()[:limit]

        if not broadcasts:
            click.secho("📚 No broadcasts created yet.", fg="yellow")
            return

        click.echo("=" * 60)
        click.secho("RECENT BROADCASTS", fg="cyan", bold=True)
        click.echo("=" * 60)
        click.echo()

        table_data = []
        for bc in broadcasts:
            table_data.append(
                [
                    bc["title"][:30],
                    bc["id"][:12],
                    bc["created_at"].split("T")[0],
                    bc["status"],
                ]
            )

        headers = ["Title", "ID", "Date", "Status"]
        click.echo(tabulate(table_data, headers=headers, tablefmt="simple"))
        click.echo()
        click.secho(f"Total: {len(broadcasts)} broadcasts", fg="cyan", bold=True)

    except Exception as e:
        click.secho(f"❌ Error listing broadcasts: {e}", fg="red", err=True)
        raise click.Abort()


@broadcast.command(name="show")
@click.argument("broadcast_id")
@click.option("--section", default="all", help="Section to show (all, analysis, script)")
def show_broadcast(broadcast_id, section):
    """Show broadcast details.

    Examples:
        mind newscast broadcast show broadcast_20260215_120000_apple_stock
        mind newscast broadcast show <id> --section script
    """
    try:
        llm = get_default_llm()
        pipeline = NewscastBroadcastPipeline(llm)

        broadcast = pipeline.get_broadcast(broadcast_id)

        if not broadcast:
            click.secho(f"❌ Broadcast not found: {broadcast_id}", fg="red")
            return

        click.echo("=" * 60)
        click.secho(f"BROADCAST: {broadcast['title']}", fg="cyan", bold=True)
        click.echo("=" * 60)
        click.echo()
        click.echo(f"ID:       {broadcast['id']}")
        click.echo(f"Status:   {broadcast['status']}")
        click.echo(f"Duration: {broadcast['duration_seconds']}s")
        click.echo(f"Created:  {broadcast['created_at']}")
        click.echo()

        if section in ["all", "analysis"]:
            click.secho("📊 ANALYSIS:", fg="yellow", bold=True)
            click.echo(broadcast["analysis"][:500])
            click.echo()

        if section in ["all", "script"]:
            click.secho("📝 SCRIPT:", fg="yellow", bold=True)
            click.echo(broadcast["script"][:500])
            if len(broadcast["script"]) > 500:
                click.echo("[... truncated ...]")

    except Exception as e:
        click.secho(f"❌ Error showing broadcast: {e}", fg="red", err=True)
        raise click.Abort()


@newscast.command(name="init")
def init_defaults():
    """Initialize NewscastStudio with default characters.

    Creates three default characters:
    - Alex Tech (Tech News Host)
    - Dr. Sarah Chen (AI Expert)
    - Mike Rivers (Field Reporter)
    """
    try:
        click.echo("🎬 Initializing NewscastStudio with default characters...")
        click.echo()

        characters = create_default_newscast_characters()

        click.secho("✅ Created default characters:", fg="green", bold=True)
        click.echo()

        for char_id, char in characters.items():
            click.echo(f"📺 {char.name}")
            click.echo(f"   Role: {', '.join(char.style_tags)}")
            click.echo(f"   Seed: {char.seed}")
            click.echo()

        click.secho(
            "💡 Use 'mind newscast character list' to see all characters", fg="cyan"
        )

    except Exception as e:
        click.secho(f"❌ Error initializing: {e}", fg="red", err=True)
        raise click.Abort()
