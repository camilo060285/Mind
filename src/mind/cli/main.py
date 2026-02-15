"""
Mind CLI - Talk to Mind from your terminal

Usage:
  mind "Your question here"
  mind ask "What is X?"
  mind analyze file.csv "Find patterns"
  mind plan "Create a cartoon about Apple"
  mind help "I have this error"
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime

# Import Mind components
from mind.cognition import get_default_llm, init_llm
from mind.agents import ComicPipelineOrchestrator
from mind.cli.learn_commands import learn
from mind.cli.newscast_commands import newscast


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version="0.1.0", prog_name="mind")
def mind_cli(ctx):
    """
    🧠 Mind - Your AI assistant in the terminal

    Ask Mind questions, create plans, analyze data, get help with problems.
    """
    ctx.ensure_object(dict)

    # If no subcommand, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@mind_cli.command()
@click.argument("question")
@click.option(
    "--model",
    default="phi",
    type=click.Choice(["phi", "qwen"]),
    help="Model to use (phi=fast, qwen=smart)",
)
@click.option("--verbose", is_flag=True, help="Show detailed output")
@click.option("--save", is_flag=True, help="Save result to history")
def ask(question: str, model: str, verbose: bool, save: bool):
    """Ask Mind a question

    Examples:

      mind ask "What is machine learning?"

      mind ask "How do I sort a Python list?" --model qwen

      mind ask "Explain quantum computing" --verbose
    """
    try:
        if verbose:
            click.secho("[Initializing Mind...]", fg="cyan")
            click.secho(f"Model: {model}", fg="cyan")
            click.secho(f"Question: {question}", fg="cyan")
            click.secho("─" * 60, fg="cyan")

        llm = init_llm(model=model)

        if verbose:
            click.secho("[Thinking...]", fg="yellow")

        answer = llm.generate(question, n_predict=500)

        click.echo(answer)

        if verbose:
            click.secho("─" * 60, fg="cyan")
            click.secho("[✓ Complete]", fg="green")

        if save:
            _save_to_history("ask", question, answer)
            click.secho("✓ Saved to history", fg="green")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@mind_cli.command()
@click.argument("task")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--save", is_flag=True, help="Save plan to file")
def plan(task: str, output_json: bool, save: bool):
    """Create a step-by-step plan for a task

    Examples:

      mind plan "Build a website"

      mind plan "Create cartoon system" --json

      mind plan "Setup database" --save > plan.txt
    """
    try:
        click.secho("[Creating plan...]", fg="cyan")

        llm = get_default_llm()

        prompt = f"""Create a detailed step-by-step plan for this task.
Be specific and actionable. Format with numbered steps.

Task: {task}

Plan:"""

        plan_output = llm.generate(prompt, n_predict=700)

        if output_json:
            steps = [s.strip() for s in plan_output.split("\n") if s.strip()]
            plan_json = {
                "task": task,
                "steps": steps,
                "created_at": datetime.now().isoformat(),
            }
            click.echo(json.dumps(plan_json, indent=2))
        else:
            click.echo(plan_output)

        if save:
            _save_to_history("plan", task, plan_output)
            click.secho("✓ Saved to history", fg="green")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@mind_cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.argument("query")
@click.option(
    "--format",
    default="text",
    type=click.Choice(["text", "json", "csv"]),
    help="Output format",
)
@click.option("--save", is_flag=True, help="Save analysis to file")
def analyze(file_path: str, query: str, format: str, save: bool):
    """Analyze a file with Mind

    Examples:

      mind analyze data.csv "Find trends"

      mind analyze report.txt "Summarize key points"

      mind analyze numbers.txt "Calculate statistics" --format json
    """
    try:
        click.secho(f"[Reading file: {file_path}]", fg="cyan")

        with open(file_path, "r") as f:
            content = f.read()

        # Limit size for safety
        if len(content) > 50000:
            content = content[:50000] + "\n[... file truncated (50KB limit) ...]"

        click.secho("[Analyzing...]", fg="cyan")

        llm = get_default_llm()

        prompt = f"""Analyze this content and answer the query.

Content:
{content}

Query: {query}

Provide a clear, concise analysis. Format output as {format.upper()} if applicable."""

        analysis = llm.generate(prompt, n_predict=800)

        click.echo(analysis)

        if save:
            _save_to_history("analyze", f"{file_path}: {query}", analysis)
            click.secho("✓ Saved to history", fg="green")

    except FileNotFoundError:
        click.secho(f"✗ File not found: {file_path}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@mind_cli.command()
@click.argument("problem")
@click.option("--language", default="auto", help="Programming language")
@click.option("--save", is_flag=True, help="Save solution to file")
def help(problem: str, language: str, save: bool):
    """Get help with a problem or error

    Examples:

      mind help "ModuleNotFoundError: No module named 'tensorflow'"

      mind help "My code is too slow, how to optimize?"

      mind help "I got a CORS error" --save
    """
    try:
        click.secho("[Analyzing problem...]", fg="cyan")

        llm = get_default_llm()

        prompt = f"""Help me solve this problem. Provide clear, actionable solution.

Problem: {problem}

Provide:
1. What's likely causing this
2. How to fix it
3. How to prevent it in future

Be concise and practical."""

        solution = llm.generate(prompt, n_predict=700)

        click.echo(solution)

        if save:
            _save_to_history("help", problem, solution)
            click.secho("✓ Saved to history", fg="green")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


# Add learn command group
mind_cli.add_command(learn)

# Add newscast command group
mind_cli.add_command(newscast)


@mind_cli.command()
def status():
    """Check Mind system status"""

    try:
        click.secho("Mind System Status", fg="cyan", bold=True)
        click.secho("=" * 60, fg="cyan")

        llm = get_default_llm()

        click.secho(f"✓ LLM Provider: {llm}", fg="green")
        click.secho(f"✓ Model: {llm.model}", fg="green")
        click.secho("✓ Status: Ready", fg="green")
        click.secho(f"✓ Timestamp: {datetime.now().isoformat()}", fg="green")

    except Exception as error:
        click.secho(f"✗ Error: LLM not available - {error}", fg="red", err=True)
        sys.exit(1)


@mind_cli.command()
def history():
    """Show recent Mind commands and results"""

    try:
        history_file = Path.home() / ".mind" / "history.json"

        if not history_file.exists():
            click.secho("No history yet", fg="yellow")
            return

        with open(history_file, "r") as f:
            history = json.load(f)

        click.secho("Recent Mind Commands", fg="cyan", bold=True)
        click.secho("=" * 60, fg="cyan")

        for i, entry in enumerate(history[-10:], 1):
            click.secho(f"\n[{i}] {entry['type'].upper()}", fg="yellow", bold=True)
            click.echo(f"    Input: {entry['input'][:60]}...")
            click.echo(f"    Time: {entry['timestamp']}")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@mind_cli.command()
def version():
    """Show Mind version and system info"""

    click.secho("Mind System Information", fg="cyan", bold=True)
    click.secho("=" * 60, fg="cyan")
    click.secho("Version: 0.1.0", fg="green")
    click.secho("Type: AI Assistant CLI", fg="green")
    click.secho("Status: Beta", fg="green")
    click.secho("Homepage: https://github.com/camilo060285/Mind", fg="green")


# ============================================================================
# Comic Studio Commands
# ============================================================================


@mind_cli.group()
def comic():
    """Comic Studio - Create 2D cartoons about market news"""
    pass


@comic.command()
@click.argument("topic")
@click.option("--context", default="", help="Market context for the story")
@click.option(
    "--model", default="qwen", type=click.Choice(["phi", "qwen"]), help="Model to use"
)
@click.option("--verbose", is_flag=True, help="Show detailed output")
@click.option("--save", is_flag=True, help="Save project info")
def create(topic: str, context: str, model: str, verbose: bool, save: bool):
    """Create a new comic from a topic

    Examples:

      mind comic create "Tesla stock surge"

      mind comic create "Meme stocks rally" --context "Wall Street frenzy" --model qwen

      mind comic create "Bitcoin crash" --verbose --save
    """
    try:
        click.secho("[Initializing Comic Studio...]", fg="cyan")

        llm = init_llm(model=model)
        orchestrator = ComicPipelineOrchestrator(llm)

        if verbose:
            click.secho(f"Model: {model}", fg="cyan")
            click.secho(f"Topic: {topic}", fg="cyan")
            click.secho("─" * 60, fg="cyan")

        click.secho("[Creating comic pipeline...]", fg="yellow")

        result = orchestrator.create_comic(topic, context)

        if result.get("status") == "success":
            click.secho("✓ Comic Pipeline Complete!", fg="green", bold=True)
            click.secho(f"\nProject ID: {result['project_id']}", fg="green")
            click.secho(f"Project Path: {result['project_path']}", fg="cyan")

            click.secho("\n📋 Outputs Generated:", fg="yellow", bold=True)
            click.echo("  ✓ Story (01_story.json)")
            click.echo("  ✓ Visual Concepts (03_concepts.json)")
            click.echo("  ✓ DALL-E Prompts (04_dalle_prompts.json)")
            click.echo("  ✓ Asset Generation Plan (06_asset_plan.json)")
            click.echo("  ✓ Animation Plan (07_animation_plan.json)")

            click.secho("\n📊 Metrics:", fg="yellow", bold=True)
            click.echo(f"  • Estimated Cost: ${result.get('estimated_cost', 0):.2f}")
            click.echo(f"  • Timeline: {result.get('estimated_timeline', 'Unknown')}")
            click.echo(f"  • Execution Steps: {result.get('execution_steps', 0)}")

            click.secho("\n🚀 Next Steps:", fg="yellow", bold=True)
            for step in result.get("next_steps", []):
                click.echo(f"  {step}")

            if save:
                _save_to_history("comic_create", topic, json.dumps(result))
                click.secho("\n✓ Saved to history", fg="green")

        elif result.get("status") == "partial":
            click.secho("⚠ Comic Pipeline Stopped (QA Issue)", fg="yellow", bold=True)
            click.echo(result.get("message"))
        else:
            click.secho(f"✗ Error: {result.get('error')}", fg="red", err=True)

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@comic.command()
@click.option("--limit", default=10, help="Number of projects to show")
@click.option("--verbose", is_flag=True, help="Show detailed info")
def list(limit: int, verbose: bool):
    """List recent comic projects

    Examples:

      mind comic list

      mind comic list --limit 20

      mind comic list --verbose
    """
    try:
        llm = get_default_llm()
        orchestrator = ComicPipelineOrchestrator(llm)

        projects = orchestrator.list_projects()[:limit]

        if not projects:
            click.secho("No comic projects yet", fg="yellow")
            return

        click.secho("Recent Comic Projects", fg="cyan", bold=True)
        click.secho("=" * 60, fg="cyan")

        for i, project in enumerate(projects, 1):
            click.secho(f"\n[{i}] {project['title']}", fg="yellow", bold=True)
            click.echo(f"    ID: {project['id']}")

            if verbose:
                proj_data = orchestrator.get_project(project["id"])
                if proj_data and "execution_log" in proj_data:
                    click.echo(f"    Steps: {len(proj_data['execution_log'])}")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


@comic.command()
@click.argument("project_id")
@click.option(
    "--show",
    type=click.Choice(["story", "concepts", "prompts", "plans", "all"]),
    default="story",
    help="What to show",
)
def show(project_id: str, show: str):
    """Show comic project details

    Examples:

      mind comic show comic_20260213_101010

      mind comic show comic_20260213_101010 --show concepts

      mind comic show comic_20260213_101010 --show all
    """
    try:
        llm = get_default_llm()
        orchestrator = ComicPipelineOrchestrator(llm)

        project = orchestrator.get_project(project_id)

        if not project:
            click.secho(f"Project not found: {project_id}", fg="red", err=True)
            sys.exit(1)

        click.secho(f"Comic Project: {project_id}", fg="cyan", bold=True)
        click.secho("=" * 60, fg="cyan")

        if show in ["story", "all"]:
            if "01_story" in project:
                story = project["01_story"].get("result", {})
                click.secho("\n📖 Story:", fg="yellow", bold=True)
                click.echo(f"Title: {story.get('title')}")
                click.echo(f"Punchline: {story.get('punchline')}")

        if show in ["concepts", "all"]:
            if "03_concepts" in project:
                concepts = project["03_concepts"].get("result", {})
                click.secho("\n🎨 Visual Concepts:", fg="yellow", bold=True)
                click.echo(f"Style: {concepts.get('visual_style')}")
                if "characters" in concepts:
                    click.echo(f"Characters: {len(concepts['characters'])}")

        if show in ["prompts", "all"]:
            if "04_dalle_prompts" in project:
                prompts = project["04_dalle_prompts"].get("result", {})
                click.secho("\n🖼️  DALL-E Prompts:", fg="yellow", bold=True)
                if "prompts" in prompts:
                    for i, prompt in enumerate(prompts["prompts"][:3], 1):
                        click.echo(
                            f"  {i}. [{prompt.get('type')}] {prompt.get('description', 'N/A')[:50]}..."
                        )

        if show in ["plans", "all"]:
            if "07_animation_plan" in project:
                anim = project["07_animation_plan"].get("result", {})
                click.secho("\n🎬 Animation Plan:", fg="yellow", bold=True)
                click.echo(f"Duration: {anim.get('total_duration')} seconds")
                click.echo(f"Music: {anim.get('music_type')}")

    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red", err=True)
        sys.exit(1)


def _save_to_history(command_type: str, input_text: str, output: str) -> None:
    """Save command to history file"""

    try:
        history_dir = Path.home() / ".mind"
        history_dir.mkdir(exist_ok=True)

        history_file = history_dir / "history.json"

        history = []
        if history_file.exists():
            with open(history_file, "r") as f:
                history = json.load(f)

        entry = {
            "type": command_type,
            "input": input_text[:200],
            "output": output[:500],
            "timestamp": datetime.now().isoformat(),
        }

        history.append(entry)

        # Keep last 100 entries
        history = history[-100:]

        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

    except Exception:
        # Silently fail on history save
        pass


def main():
    """Entry point for CLI"""
    mind_cli(obj={})


if __name__ == "__main__":
    main()
