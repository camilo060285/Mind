"""SpecializedAgentFactory - Creates agents that think using LLM

Each agent gets:
1. Clear role/expertise
2. Access to LLM for reasoning
3. Memory of previous steps
4. Ability to call other agents or APIs
"""

from typing import Any, Dict, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime


class SpecializedAgent(ABC):
    """Base class for specialized agents that use LLM to think"""

    def __init__(self, name: str, role: str, llm: Any, expertise: str):
        """
        Initialize a specialized agent

        Args:
            name: Agent name (e.g., "StoryWriterAgent")
            role: Agent role (e.g., "Writes compelling stories")
            llm: LLM provider instance
            expertise: Agent's area of expertise/instructions
        """
        self.name = name
        self.role = role
        self.llm = llm
        self.expertise = expertise
        self.memory: List[Dict[str, Any]] = []
        self.output: Optional[Dict[str, Any]] = None

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent's task using LLM reasoning

        Args:
            input_data: Input for the agent to process

        Returns:
            Agent's output with reasoning and results
        """
        pass

    def think(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Use LLM to think/reason about a task

        Args:
            prompt: The reasoning prompt
            max_tokens: Max tokens to generate

        Returns:
            LLM's reasoning/response
        """
        full_prompt = f"""{self.expertise}

Task: {prompt}

Provide clear, structured reasoning and output."""

        response = self.llm.generate(full_prompt, n_predict=max_tokens)
        self.memory.append({"step": "think", "prompt": prompt, "response": response})
        return response

    def remember(self, key: str, value: Any) -> None:
        """Add to agent memory"""
        self.memory.append({"type": "memory", "key": key, "value": value})

    def save_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save and return agent output

        Args:
            result: Result to save

        Returns:
            Formatted output with metadata
        """
        self.output = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "result": result,
            "reasoning_steps": len(self.memory),
        }
        return self.output


class ComicStudioAgent(SpecializedAgent):
    """Base for all comic studio agents"""

    def __init__(self, name: str, role: str, llm: Any, expertise: str):
        super().__init__(name, role, llm, expertise)
        self.agent_type = "comic_studio"


# ============================================================================
# AGENT IMPLEMENTATIONS
# ============================================================================


class MarketAnalystAgent(ComicStudioAgent):
    """Analyzes market news and identifies trending topics"""

    def __init__(self, llm: Any):
        expertise = """You are a market analysis expert for comic content creation.
Your role is to identify trending market topics and find the humor angle.
Focus on: stock movements, crypto trends, market events, business news.
Output should identify the core hook/angle for a funny story."""

        super().__init__(
            name="MarketAnalystAgent",
            role="Analyzes market news for comic potential",
            llm=llm,
            expertise=expertise,
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a topic to extract story angle

        Args:
            input_data: {"topic": str, "context": str}

        Returns:
            Analyzed topic with humor angle and story hooks
        """
        topic = input_data.get("topic", "")
        context = input_data.get("context", "")

        prompt = f"""Analyze this market topic for a funny cartoon story:

Topic: {topic}
Context: {context}

Analyze:
1. Core market event (what happened?)
2. Humor angle (why is it funny?)
3. Main characters (who would star in this?)
4. Story hooks (what's the narrative tension?)
5. Target audience (who should find this funny?)

Keep it concise and punchy."""

        analysis = self.think(prompt, max_tokens=600)

        result = {
            "original_topic": topic,
            "analysis": analysis,
            "identified_angle": self._extract_angle(analysis),
            "confidence": 0.85,
        }

        return self.save_output(result)

    def _extract_angle(self, analysis: str) -> str:
        """Extract the main story angle from analysis"""
        lines = analysis.split("\n")
        for line in lines:
            if "humor" in line.lower() or "angle" in line.lower():
                return line.strip()
        return "Trending market event with comedic potential"


class StoryWriterAgent(ComicStudioAgent):
    """Writes story narratives for comics"""

    def __init__(self, llm: Any):
        expertise = """You are a comic script writer specializing in 4-panel stories.
Create engaging narratives with setup, tension, twist, and punchline.
Each panel should have visual and dialogue elements.
Keep it funny, concise, and visually interesting."""

        super().__init__(
            name="StoryWriterAgent",
            role="Writes 4-panel comic stories",
            llm=llm,
            expertise=expertise,
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a 4-panel comic story

        Args:
            input_data: {"topic": str, "angle": str, "style": str}

        Returns:
            4-panel story with dialogue and descriptions
        """
        topic = input_data.get("topic", "")
        angle = input_data.get("angle", "")
        style = input_data.get("style", "satirical")

        prompt = f"""Write a 4-panel comic story for this topic:

Topic: {topic}
Angle: {angle}
Style: {style}

Create exactly 4 panels following this structure:
Panel 1: Setup - introduce the situation/characters
Panel 2: Development - where does it go?
Panel 3: Complication - twist or escalation
Panel 4: Payoff - funny punchline ending

For each panel provide:
- Visual description (what we see)
- Dialogue (what they say)
- Actions (any motion/animation)

Make it relatable and hilarious!"""

        story = self.think(prompt, max_tokens=800)

        # Parse the story into panels
        panels = self._parse_panels(story)

        result = {
            "topic": topic,
            "style": style,
            "panels": panels,
            "full_story": story,
            "panel_count": len(panels),
        }

        return self.save_output(result)

    def _parse_panels(self, story: str) -> List[Dict[str, Any]]:
        """Parse story into 4 panel structure"""
        panels: List[Dict[str, Any]] = []
        panel_text = story.split("Panel")

        for i, text in enumerate(panel_text[1:], 1):
            if text.strip():
                panels.append(
                    {
                        "number": i,
                        "content": text.strip()[:300],
                    }
                )

        while len(panels) < 4:
            panels.append({"number": len(panels) + 1, "content": "..."})

        return panels[:4]


class ConceptDesignAgent(ComicStudioAgent):
    """Designs visual concepts and character descriptions"""

    def __init__(self, llm: Any):
        expertise = """You are a visual design specialist for cartoon animation.
Create detailed visual descriptions for characters, scenes, and animations.
Think about: art style, color schemes, character personalities, scene composition.
Output should be clear enough for an AI image generator (DALL-E) to interpret."""

        super().__init__(
            name="ConceptDesignAgent",
            role="Designs visual concepts for animations",
            llm=llm,
            expertise=expertise,
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design visual concepts from a story

        Args:
            input_data: {"panels": List[Dict], "topic": str}

        Returns:
            Visual design concepts for each panel
        """
        panels = input_data.get("panels", [])
        topic = input_data.get("topic", "")

        prompt = f"""Design visual concepts for this 4-panel comic about: {topic}

Create detailed visual descriptions for each of the {len(panels)} panels.

For each panel describe:
1. Main characters (appearance, emotion, pose)
2. Background/setting (location, style, mood)
3. Color scheme (dominant colors)
4. Animation notes (movement, emphasis)
5. Art style recommendation (cartoon, minimalist, etc.)

Keep each description concise but visual enough for AI image generation."""

        concepts = self.think(prompt, max_tokens=1000)

        result = {
            "topic": topic,
            "visual_style": "Modern cartoon with market humor",
            "panel_concepts": self._extract_concepts(concepts),
            "design_notes": concepts,
            "character_count": 2,
            "scene_count": len(panels),
        }

        return self.save_output(result)

    def _extract_concepts(self, design_text: str) -> List[Dict[str, Any]]:
        """Extract visual concepts for each panel"""
        concepts: List[Dict[str, Any]] = []
        sections = design_text.split("Panel")

        for i, section in enumerate(sections[1:], 1):
            if section.strip():
                concepts.append(
                    {
                        "panel": i,
                        "visual_description": section.strip()[:250],
                    }
                )

        return concepts[:4]


class QualityCheckAgent(ComicStudioAgent):
    """Validates comic quality and consistency"""

    def __init__(self, llm: Any):
        expertise = """You are a quality assurance expert for comic content.
Evaluate stories for humor quality, visual consistency, narrative flow, and market relevance.
Provide constructive feedback on what works and what needs improvement."""

        super().__init__(
            name="QualityCheckAgent",
            role="Validates comic quality",
            llm=llm,
            expertise=expertise,
        )

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate comic project

        Args:
            input_data: Full comic project data

        Returns:
            Quality assessment and recommendations
        """
        story = input_data.get("story", "")
        concepts = input_data.get("concepts", "")

        prompt = f"""Review this comic project for quality:

Story: {story[:500]}...

Visual Concepts: {concepts[:500]}...

Assess:
1. Humor quality (1-10)
2. Story clarity (1-10)
3. Visual appeal (1-10)
4. Market relevance (1-10)
5. Overall cohesion (1-10)

Provide brief feedback and one recommendation for improvement."""

        review = self.think(prompt, max_tokens=400)

        # Extract quality scores
        scores = self._extract_scores(review)

        result = {
            "quality_scores": scores,
            "average_score": sum(scores.values()) / len(scores) if scores else 0,
            "status": (
                "approved"
                if sum(scores.values()) / len(scores) >= 7
                else "needs_revision"
            ),
            "review": review,
        }

        return self.save_output(result)

    def _extract_scores(self, review_text: str) -> Dict[str, float]:
        """Extract quality scores from review"""
        scores = {}
        # Simple score extraction - looks for "X-10" or "X/10" patterns
        import re

        pattern = r"(\d+)[/-]10"
        matches = re.findall(pattern, review_text)

        categories = ["humor", "clarity", "appeal", "relevance", "cohesion"]
        for i, score_str in enumerate(matches[:5]):
            if i < len(categories):
                scores[categories[i]] = float(score_str)

        return scores


class SpecializedAgentFactory:
    """Factory for creating specialized agents"""

    @staticmethod
    def create_market_analyst(llm: Any) -> MarketAnalystAgent:
        """Create a market analyst agent"""
        return MarketAnalystAgent(llm)

    @staticmethod
    def create_story_writer(llm: Any) -> StoryWriterAgent:
        """Create a story writer agent"""
        return StoryWriterAgent(llm)

    @staticmethod
    def create_concept_designer(llm: Any) -> ConceptDesignAgent:
        """Create a concept designer agent"""
        return ConceptDesignAgent(llm)

    @staticmethod
    def create_quality_checker(llm: Any) -> QualityCheckAgent:
        """Create a quality check agent"""
        return QualityCheckAgent(llm)

    @staticmethod
    def create_all_comic_agents(llm: Any) -> Dict[str, SpecializedAgent]:
        """Create all comic studio agents"""
        return {
            "analyzer": SpecializedAgentFactory.create_market_analyst(llm),
            "writer": SpecializedAgentFactory.create_story_writer(llm),
            "designer": SpecializedAgentFactory.create_concept_designer(llm),
            "quality": SpecializedAgentFactory.create_quality_checker(llm),
        }
