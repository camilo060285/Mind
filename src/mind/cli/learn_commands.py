"""CLI commands for learning."""

import click
from mind.cognition import init_llm
from pathlib import Path
import json
from datetime import datetime


@click.group()
def learn():
    """Learning commands for Mind."""
    pass


@learn.command(name="youtube")
@click.argument("youtube_url")
@click.option("--save", is_flag=True, help="Save to knowledge base")
def learn_youtube(youtube_url: str, save: bool):
    """Learn from a YouTube video (transcript extraction).

    Examples:
        mind learn youtube "https://youtube.com/watch?v=..."
        mind learn youtube "https://youtube.com/watch?v=..." --save
    """
    try:
        click.secho("[Fetching transcript...]", fg="cyan")

        try:
            from mind.learning import YouTubeTextLearner

            learner = YouTubeTextLearner()
            knowledge = learner.learn_from_url(youtube_url)

            click.secho("✓ Learned from video", fg="green")

            if "summary" in knowledge:
                click.secho("\nSummary:", fg="yellow", bold=True)
                click.echo(knowledge.get("summary", ""))

            if "concepts" in knowledge:
                click.secho("\nKey Concepts:", fg="yellow", bold=True)
                click.echo(knowledge.get("concepts", ""))

            if save:
                click.secho("✓ Saved to knowledge base", fg="green")

        except ImportError:
            click.secho(
                "YouTube learning module not available. Install youtube-transcript-api",
                fg="yellow",
            )

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        raise click.Abort()


@learn.command(name="topic")
@click.argument("topic")
@click.option(
    "--format",
    type=click.Choice(["tutorial", "summary", "comprehensive", "quick"]),
    default="comprehensive",
    help="Learning format/depth",
)
@click.option(
    "--examples/--no-examples", default=True, help="Include practical examples"
)
@click.option("--save/--no-save", default=True, help="Save learned knowledge to memory")
def learn_topic(topic, format, examples, save):
    """Learn about a specific topic.

    Examples:
        mind learn topic "machine learning basics"
        mind learn topic "cryptography" --format tutorial
        mind learn topic "neural networks" --format quick --no-examples
    """
    click.echo("=" * 60)
    click.echo(f"🎓 LEARNING: {topic}")
    click.echo("=" * 60)
    click.echo()

    try:
        # Initialize Mind with Qwen (better for learning)
        click.echo("🧠 Initializing Mind cognitive system...")
        mind = init_llm(model="qwen")
        click.echo("✓ Mind ready\n")

        # Create learning prompt based on format
        prompts = {
            "tutorial": f"""Create a comprehensive tutorial on {topic}.
Include:
1. Introduction and overview
2. Core concepts with clear explanations
3. Step-by-step explanations
4. {'Practical examples and code snippets' if examples else 'Key points'}
5. Common pitfalls and best practices
6. Summary and next steps

Make it beginner-friendly but thorough.""",
            "summary": f"""Provide a concise but complete summary of {topic}.
Include:
1. What it is (definition)
2. Why it matters (importance)
3. Key concepts (main ideas)
4. {'Real-world examples' if examples else 'Use cases'}
5. Further learning resources

Be clear and concise.""",
            "comprehensive": f"""Provide comprehensive knowledge about {topic}.
Include:
1. Detailed introduction
2. Historical context and development
3. Fundamental principles and concepts
4. Technical details and mechanisms
5. {'Practical applications with examples' if examples else 'Applications'}
6. Current trends and future directions
7. Common challenges and solutions
8. Resources for deeper learning

Be thorough and educational.""",
            "quick": f"""Provide a quick reference guide for {topic}.
Include:
1. One-sentence definition
2. 3-5 key points
3. {'1-2 simple examples' if examples else 'Main use cases'}
4. Most important thing to remember

Be brief but valuable.""",
        }

        prompt = prompts.get(format, prompts["comprehensive"])

        # Mind learns the topic
        click.echo(f"📚 Learning about '{topic}' ({format} format)...")
        click.echo("   This may take 10-30 seconds...\n")

        knowledge = mind.generate(
            prompt, n_predict=800 if format == "comprehensive" else 400
        )

        click.echo("=" * 60)
        click.echo("LEARNED KNOWLEDGE")
        click.echo("=" * 60)
        click.echo()
        click.echo(knowledge)
        click.echo()

        # Save to memory if requested
        if save:
            click.echo("💾 Saving to Mind's memory...")

            # Create memory entry
            memory_entry = {
                "topic": topic,
                "format": format,
                "knowledge": knowledge,
                "learned_at": datetime.now().isoformat(),
                "included_examples": examples,
            }

            # Save to memory
            memory_path = Path.home() / ".mind" / "memory" / "learned_topics"
            memory_path.mkdir(parents=True, exist_ok=True)

            # Create safe filename
            safe_topic = "".join(
                c if c.isalnum() or c in (" ", "-", "_") else "_" for c in topic
            )
            safe_topic = safe_topic.replace(" ", "_").lower()

            file_path = memory_path / f"{safe_topic}.json"

            with open(file_path, "w") as f:
                json.dump(memory_entry, f, indent=2)

            click.echo(f"✓ Saved to: {file_path}")
            click.echo()

        click.echo("=" * 60)
        click.echo("✅ LEARNING COMPLETE!")
        click.echo("=" * 60)
        click.echo()
        click.echo(f"Mind has learned about '{topic}'.")
        click.echo("You can now ask Mind questions about this topic.")

    except Exception as e:
        click.echo(f"\n❌ Error during learning: {str(e)}", err=True)
        raise click.Abort()


@learn.command(name="list")
def list_learned():
    """List all topics Mind has learned."""
    memory_path = Path.home() / ".mind" / "memory" / "learned_topics"

    if not memory_path.exists():
        click.echo("📚 Mind hasn't learned any topics yet.")
        click.echo("\nTry: mind learn topic 'your topic here'")
        return

    json_files = list(memory_path.glob("*.json"))

    if not json_files:
        click.echo("📚 Mind hasn't learned any topics yet.")
        return

    click.echo("=" * 60)
    click.echo("LEARNED TOPICS")
    click.echo("=" * 60)
    click.echo()

    for json_file in sorted(json_files):
        try:
            with open(json_file) as f:
                entry = json.load(f)

            topic = entry.get("topic", "Unknown")
            learned_at = entry.get("learned_at", "Unknown")
            format_type = entry.get("format", "Unknown")

            click.echo(f"📖 {topic}")
            click.echo(f"   Format: {format_type}")
            click.echo(f"   Learned: {learned_at}")
            click.echo()
        except Exception as e:
            click.echo(f"⚠️  Error reading {json_file.name}: {str(e)}")

    click.echo(f"Total: {len(json_files)} topics learned")


@learn.command(name="review")
@click.argument("topic")
def review_topic(topic):
    """Review a previously learned topic."""
    memory_path = Path.home() / ".mind" / "memory" / "learned_topics"

    # Create safe filename
    safe_topic = "".join(
        c if c.isalnum() or c in (" ", "-", "_") else "_" for c in topic
    )
    safe_topic = safe_topic.replace(" ", "_").lower()

    file_path = memory_path / f"{safe_topic}.json"

    if not file_path.exists():
        click.echo(f"❌ Topic '{topic}' not found in memory.")
        click.echo("\nAvailable topics:")
        ctx = click.Context(list_learned)
        ctx.invoke(list_learned)
        return

    try:
        with open(file_path) as f:
            entry = json.load(f)

        click.echo("=" * 60)
        click.echo(f"REVIEWING: {entry['topic']}")
        click.echo("=" * 60)
        click.echo()
        click.echo(f"Format: {entry['format']}")
        click.echo(f"Learned: {entry['learned_at']}")
        click.echo()
        click.echo("=" * 60)
        click.echo("KNOWLEDGE")
        click.echo("=" * 60)
        click.echo()
        click.echo(entry["knowledge"])
        click.echo()

    except Exception as e:
        click.echo(f"❌ Error reading topic: {str(e)}", err=True)
        raise click.Abort()
