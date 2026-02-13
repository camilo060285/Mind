#!/usr/bin/env python3
"""
Quick demo: How Mind Comic Studio agents think and work together

This shows the REAL action - agents using LLM to reason about tasks,
not placeholder logic.
"""

from mind.cognition import init_llm
from mind.agents import SpecializedAgentFactory, ComicPipelineOrchestrator


def demo_market_analyst():
    """Show MarketAnalystAgent thinking"""
    print("\n" + "=" * 70)
    print("DEMO 1: MarketAnalystAgent - Analyzing Market Topics")
    print("=" * 70)

    llm = init_llm(model="phi")
    analyzer = SpecializedAgentFactory.create_market_analyst(llm)

    topic = "Tesla stock surge 50%"
    print(f"\n📰 Topic: {topic}")
    print("\n🧠 Agent is THINKING using LLM....\n")

    result = analyzer.execute({"topic": topic, "context": "Market news"})

    if result.get("status") == "success":
        analysis = result.get("result", {})
        print(f"✓ Status: {result['status']}")
        print(f"\n📊 Market Analysis:\n{analysis.get('analysis', '')[:300]}...")
        print(f"\n💡 Humor Angle: {analysis.get('identified_angle', 'N/A')}")
    else:
        print(f"✗ Error: {result.get('error')}")


def demo_story_writer():
    """Show StoryWriterAgent thinking"""
    print("\n" + "=" * 70)
    print("DEMO 2: StoryWriterAgent - Creating 4-Panel Stories")
    print("=" * 70)

    llm = init_llm(model="phi")
    writer = SpecializedAgentFactory.create_story_writer(llm)

    print("\n📚 Writing 4-panel comic story...")
    print("🧠 Agent is THINKING using LLM....\n")

    result = writer.execute(
        {
            "topic": "Market volatility",
            "angle": "Traders panicking over price swings",
            "style": "satirical",
        }
    )

    if result.get("status") == "success":
        story = result.get("result", {})
        print(f"✓ Status: {result['status']}")
        print(f"✓ Panels created: {story.get('panel_count')}")

        panels = story.get("panels", [])
        for i, panel in enumerate(panels[:2], 1):
            print(f"\n📖 Panel {i}:")
            print(f"{panel.get('content', '')[:150]}...")
    else:
        print(f"✗ Error: {result.get('error')}")


def demo_concept_designer():
    """Show ConceptDesignAgent thinking"""
    print("\n" + "=" * 70)
    print("DEMO 3: ConceptDesignAgent - Designing Visuals")
    print("=" * 70)

    llm = init_llm(model="phi")
    designer = SpecializedAgentFactory.create_concept_designer(llm)

    print("\n🎨 Designing visual concepts for comic...")
    print("🧠 Agent is THINKING using LLM....\n")

    result = designer.execute(
        {
            "panels": [
                {"number": 1, "content": "Setup scene"},
                {"number": 2, "content": "Build tension"},
                {"number": 3, "content": "Twist"},
                {"number": 4, "content": "Punchline"},
            ],
            "topic": "Crypto collapse",
        }
    )

    if result.get("status") == "success":
        concepts = result.get("result", {})
        print(f"✓ Status: {result['status']}")
        print(f"✓ Visual style: {concepts.get('visual_style')}")
        print(f"✓ Concepts created: {len(concepts.get('panel_concepts', []))}")

        for concept in concepts.get("panel_concepts", [])[:2]:
            print(f"\n🎬 Panel {concept.get('panel')} Visual:")
            print(f"{concept.get('visual_description', '')[:150]}...")
    else:
        print(f"✗ Error: {result.get('error')}")


def demo_full_pipeline():
    """Show complete pipeline in action"""
    print("\n" + "=" * 70)
    print("DEMO 4: FULL PIPELINE - Complete Comic Creation")
    print("=" * 70)

    llm = init_llm(model="phi")
    orchestrator = ComicPipelineOrchestrator(llm)

    topic = "Meme stock mania"
    print(f"\n🚀 Creating comic: '{topic}'")
    print("🧠 All agents thinking & working together...\n")

    result = orchestrator.create_comic(topic, context="Wall Street frenzy")

    if result.get("status") in ["success", "partial"]:
        print("\n✅ Pipeline Complete!")
        print(f"   Project ID: {result['project_id']}")
        print(f"   Estimated Cost: ${result.get('estimated_cost', 0):.2f}")
        print(f"   Timeline: {result.get('estimated_timeline')}")
        print(f"   Execution Steps: {result.get('execution_steps')}")

        print("\n📋 Completed Stages:")
        for step in result.get("next_steps", [])[:3]:
            print(f"   • {step}")
    else:
        print(f"✗ Error: {result.get('error')}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print(
        "║"
        + "  🧠 MIND COMIC STUDIO - Real Agents Using LLM to Think  ".center(68)
        + "║"
    )
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    print("\nShowing 4 demos of how Mind agents reason using LLM...\n")

    # Run demos
    try:
        demo_market_analyst()
        demo_story_writer()
        demo_concept_designer()
        demo_full_pipeline()

        print("\n" + "=" * 70)
        print("✅ All Demos Complete!")
        print("=" * 70)
        print("\nNow use Mind from terminal:")
        print("  $ mind comic create 'Your topic here' --model phi --verbose")
        print("  $ mind comic list")
        print("  $ mind comic show <project_id> --show all")
        print()

    except KeyboardInterrupt:
        print("\n\n⏸ Demo interrupted")
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
