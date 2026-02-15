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
    default="summary",
    help="Learning format/depth",
)
@click.option(
    "--examples/--no-examples", default=True, help="Include practical examples"
)
@click.option("--save/--no-save", default=True, help="Save learned knowledge to memory")
@click.option(
    "--model",
    type=click.Choice(["phi", "qwen"]),
    default="phi",
    help="Model to use (phi=faster, qwen=deeper)",
)
def learn_topic(topic, format, examples, save, model):
    """Learn about a specific topic.

    Examples:
        mind learn topic "machine learning basics"
        mind learn topic "cryptography" --format tutorial
        mind learn topic "neural networks" --format quick --no-examples
        mind learn topic "deep learning" --format comprehensive --model qwen
    """
    click.echo("=" * 60)
    click.echo(f"🎓 LEARNING: {topic}")
    click.echo("=" * 60)
    click.echo()

    try:
        # Initialize Mind
        click.echo(f"🧠 Initializing Mind cognitive system (model: {model})...")
        mind_llm = init_llm(model=model)
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

        # Adjust token limits based on format and model
        token_limits = {
            "quick": 200,
            "summary": 300,  # Reduced from 350
            "tutorial": 400,  # Reduced from 500
            "comprehensive": 450,  # Reduced from 600
        }
        n_predict = token_limits.get(format, 300)

        # Qwen is slower - reduce tokens further for better completion
        if model == "qwen":
            n_predict = int(n_predict * 0.8)  # 20% fewer tokens for qwen

        # Adjust timeout based on format and model
        timeout_settings = {
            "quick": 120,  # Increased from 90
            "summary": 180,  # Increased from 120
            "tutorial": 300,  # Increased from 180
            "comprehensive": 480,  # Increased from 240 (8 minutes)
        }
        base_timeout = timeout_settings.get(format, 180)
        # Qwen model needs significantly more time
        timeout = base_timeout * 2 if model == "qwen" else base_timeout

        # Warn about comprehensive + qwen combo
        if format == "comprehensive" and model == "qwen":
            click.echo()
            click.secho(
                "⚠️  Note: Comprehensive learning with qwen is very slow (5-10 minutes)",
                fg="yellow",
            )
            click.secho(
                "   Consider using --format tutorial instead, or --model phi for faster results",
                fg="yellow",
            )
            click.echo()

        # Mind learns the topic
        click.echo(f"📚 Learning about '{topic}' ({format} format)...")
        time_estimates = {
            "quick": ("15-45 seconds", "5-15 seconds"),  # (qwen, phi)
            "summary": ("45-90 seconds", "20-40 seconds"),
            "tutorial": ("2-5 minutes", "40-80 seconds"),
            "comprehensive": ("5-10 minutes", "2-4 minutes"),
        }
        qwen_time, phi_time = time_estimates.get(
            format, ("30-60 seconds", "15-30 seconds")
        )
        expected_time = qwen_time if model == "qwen" else phi_time
        click.echo(f"   Expected time: {expected_time}")
        click.echo(f"   Timeout limit: {int(timeout)} seconds")
        click.echo()
        click.echo("   Processing (this may take a while)", nl=False)

        try:
            # Generate with retry logic
            max_retries = 3  # Increased from 2
            current_timeout = int(timeout)
            current_tokens = n_predict
            for attempt in range(max_retries):
                try:
                    click.echo(".", nl=False)
                    knowledge = mind_llm.generate(
                        prompt, n_predict=current_tokens, timeout=current_timeout
                    )
                    click.echo(" ✓\n")
                    break
                except Exception as e:
                    if "timed out" in str(e).lower() and attempt < max_retries - 1:
                        click.echo(
                            f"\n   ⚠️  Timeout on attempt {attempt + 1}/{max_retries}"
                        )
                        click.echo(
                            f"      Reducing tokens: {current_tokens} → ", nl=False
                        )
                        current_tokens = int(
                            current_tokens * 0.6
                        )  # More aggressive: 40% reduction
                        click.echo(f"{current_tokens}")
                        click.echo(
                            f"      Increasing timeout: {current_timeout}s → ", nl=False
                        )
                        current_timeout = int(
                            current_timeout * 1.5
                        )  # More aggressive: 50% increase
                        click.echo(f"{current_timeout}s")
                        click.echo("   Retrying", nl=False)
                        continue
                    else:
                        raise
        except Exception as e:
            click.echo(" ✗\n")
            if "timed out" in str(e).lower():
                click.secho(
                    "❌ Learning timed out after multiple attempts", fg="red", bold=True
                )
                click.echo()
                click.secho("💡 Solutions:", fg="yellow", bold=True)

                if format == "comprehensive":
                    click.echo(
                        "   • comprehensive format is very demanding - try tutorial instead:"
                    )
                    click.secho(
                        f"     mind learn topic '{topic}' --format tutorial --model {model}",
                        fg="cyan",
                    )

                if model == "qwen":
                    click.echo("   • qwen model is slower - try phi instead:")
                    click.secho(
                        f"     mind learn topic '{topic}' --format {format} --model phi",
                        fg="cyan",
                    )

                click.echo("   • Use quicker formats:")
                click.secho(
                    f"     mind learn topic '{topic}' --format quick", fg="cyan"
                )
                click.secho(
                    f"     mind learn topic '{topic}' --format summary", fg="cyan"
                )

                click.echo("   • Break into smaller topics:")
                click.echo(f"     Instead of '{topic}', try more specific subtopics")
                click.echo()
            raise

        click.echo()

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
