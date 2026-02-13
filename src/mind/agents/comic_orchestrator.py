"""ComicPipelineOrchestrator - Orchestrates the entire comic creation flow

This is where agents work together to create a complete comic:
1. MarketAnalystAgent → Analyzes topic
2. StoryWriterAgent → Writes story
3. ConceptDesignAgent → Designs visuals
4. QualityCheckAgent → Validates output
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

from .specialized_agent_factory import SpecializedAgentFactory


class ComicPipelineOrchestrator:
    """Orchestrates the complete comic creation pipeline"""

    def __init__(self, llm: Any):
        """
        Initialize the orchestrator

        Args:
            llm: LLM provider instance
        """
        self.llm = llm
        self.projects_dir = Path.home() / ".mind" / "comic_projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

        # Create all agents
        self.analyzer = SpecializedAgentFactory.create_market_analyst(llm)
        self.writer = SpecializedAgentFactory.create_story_writer(llm)
        self.designer = SpecializedAgentFactory.create_concept_designer(llm)
        self.quality = SpecializedAgentFactory.create_quality_checker(llm)

    def create_comic(self, topic: str, context: str = "") -> Dict[str, Any]:
        """
        Create a complete comic through the full pipeline

        Args:
            topic: The topic/headline for the comic
            context: Additional context about the topic

        Returns:
            Complete comic project data
        """
        project_id = self._generate_project_id(topic)
        project_path = self.projects_dir / project_id

        try:
            # Initialize project
            project: Dict[str, Any] = {
                "id": project_id,
                "title": topic,
                "context": context,
                "created_at": datetime.now().isoformat(),
                "status": "in_progress",
                "execution_log": [],
                "estimated_cost": 0.53,
                "estimated_timeline": "30 minutes",
            }

            click_secho = self._get_click_echo()

            # ==================== STAGE 1: ANALYSIS ====================
            click_secho("[Stage 1/4] Analyzing market topic...", fg="cyan")

            analysis_output = self.analyzer.execute(
                {"topic": topic, "context": context}
            )
            project["01_analysis"] = analysis_output
            project["execution_log"].append(
                {
                    "stage": 1,
                    "agent": "MarketAnalystAgent",
                    "status": "complete",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            if analysis_output.get("status") != "success":
                return {
                    "status": "failed",
                    "error": "Failed to analyze topic",
                    "project_id": project_id,
                }

            click_secho("✓ Market analysis complete", fg="green")

            # ==================== STAGE 2: STORY ====================
            click_secho("[Stage 2/4] Writing comic story...", fg="cyan")

            story_input = {
                "topic": topic,
                "angle": analysis_output.get("result", {}).get(
                    "identified_angle", topic
                ),
                "style": "satirical",
            }

            story_output = self.writer.execute(story_input)
            project["02_story"] = story_output
            project["execution_log"].append(
                {
                    "stage": 2,
                    "agent": "StoryWriterAgent",
                    "status": "complete",
                    "panels": len(story_output.get("result", {}).get("panels", [])),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            if story_output.get("status") != "success":
                return {
                    "status": "failed",
                    "error": "Failed to write story",
                    "project_id": project_id,
                }

            click_secho("✓ Story written", fg="green")

            # ==================== STAGE 3: VISUAL CONCEPTS ====================
            click_secho("[Stage 3/4] Designing visual concepts...", fg="cyan")

            concepts_input = {
                "panels": story_output.get("result", {}).get("panels", []),
                "topic": topic,
            }

            concepts_output = self.designer.execute(concepts_input)
            project["03_concepts"] = concepts_output
            project["execution_log"].append(
                {
                    "stage": 3,
                    "agent": "ConceptDesignAgent",
                    "status": "complete",
                    "timestamp": datetime.now().isoformat(),
                }
            )

            if concepts_output.get("status") != "success":
                return {
                    "status": "failed",
                    "error": "Failed to design concepts",
                    "project_id": project_id,
                }

            click_secho("✓ Visual concepts designed", fg="green")

            # ==================== STAGE 4: QUALITY CHECK ====================
            click_secho("[Stage 4/4] Running quality checks...", fg="cyan")

            quality_input = {
                "story": story_output.get("result", {}).get("full_story", ""),
                "concepts": concepts_output.get("result", {}).get("design_notes", ""),
            }

            quality_output = self.quality.execute(quality_input)
            project["04_quality"] = quality_output
            project["execution_log"].append(
                {
                    "stage": 4,
                    "agent": "QualityCheckAgent",
                    "status": "complete",
                    "quality_score": quality_output.get("result", {}).get(
                        "average_score"
                    ),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # ==================== GENERATION PLANS ====================
            # Create placeholder plans for cloud generation phases
            project["05_dalle_prompts"] = {
                "agent": "PromptOptimizationAgent",
                "status": "ready",
                "estimated_cost": 0.32,
                "result": self._generate_dalle_prompts(story_output, concepts_output),
            }

            project["06_animation_plan"] = {
                "agent": "AnimatorAgent",
                "status": "ready",
                "estimated_cost": 0.06,
                "result": self._generate_animation_plan(story_output, concepts_output),
            }

            # Determine final status
            quality_status = quality_output.get("result", {}).get("status", "approved")
            if quality_status == "approved":
                project["status"] = "approved"
                click_secho("✓ Comic pipeline approved!", fg="green", bold=True)
                result_status = "success"
            else:
                project["status"] = "revision_needed"
                click_secho("⚠ Comic needs revisions - but proceeding", fg="yellow")
                result_status = "partial"

            # Save project
            project_path.mkdir(parents=True, exist_ok=True)
            project_file = project_path / "project.json"
            with open(project_file, "w") as f:
                json.dump(project, f, indent=2)

            return {
                "status": result_status,
                "project_id": project_id,
                "project_path": str(project_path),
                "estimated_cost": project.get("estimated_cost"),
                "estimated_timeline": project.get("estimated_timeline"),
                "execution_steps": len(project.get("execution_log", [])),
                "next_steps": [
                    "Generate assets with DALL-E (costs $0.32)",
                    "Create animations with Runway ML (costs $0.06)",
                    "Validate final output",
                    "Publish to social media",
                ],
                "message": quality_output.get("result", {}).get("review", ""),
            }

        except Exception as e:  # pylint: disable=broad-except
            return {
                "status": "failed",
                "error": str(e),
                "project_id": project_id,
            }

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all comic projects"""
        projects = []

        for project_dir in sorted(self.projects_dir.iterdir(), reverse=True):
            if project_dir.is_dir():
                project_file = project_dir / "project.json"
                if project_file.exists():
                    with open(project_file, "r") as f:
                        project = json.load(f)
                        projects.append(
                            {
                                "id": project.get("id"),
                                "title": project.get("title"),
                                "created_at": project.get("created_at"),
                                "status": project.get("status"),
                            }
                        )

        return projects

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project details"""
        project_file = self.projects_dir / project_id / "project.json"

        if project_file.exists():
            with open(project_file, "r") as f:
                return json.load(f)

        return None

    def _generate_project_id(self, topic: str) -> str:
        """Generate unique project ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = topic[:20].lower().replace(" ", "_")
        return f"comic_{timestamp}_{topic_slug}"

    def _generate_dalle_prompts(
        self, story_output: Dict, concepts_output: Dict
    ) -> Dict[str, Any]:
        """Generate DALL-E prompts from story and concepts"""
        prompts = []

        # Extract concepts
        concepts = concepts_output.get("result", {}).get("panel_concepts", [])

        for i, concept in enumerate(concepts[:4], 1):
            visual_desc = concept.get("visual_description", "")
            prompts.append(
                {
                    "panel": i,
                    "type": "character_and_setting",
                    "description": f"Cartoon illustration: {visual_desc}",
                    "style": "modern vector cartoon",
                    "aspect_ratio": "16:9",
                }
            )

        return {
            "total_prompts": len(prompts),
            "estimated_cost": len(prompts) * 0.04,
            "prompts": prompts,
        }

    def _generate_animation_plan(
        self, story_output: Dict, concepts_output: Dict
    ) -> Dict[str, Any]:
        """Generate animation plan from story and concepts"""
        return {
            "total_duration": 6,
            "duration_per_panel": 1.5,
            "transitions": "smooth_pan_and_zoom",
            "music_type": "upbeat_background_track",
            "animation_style": "character_movement_with_effects",
            "estimated_cost": 0.06,
        }

    @staticmethod
    def _get_click_echo() -> Any:
        """Get click echo function safely"""
        try:
            import click

            return click.secho
        except ImportError:

            def fallback(text: str, **kwargs: Any) -> None:
                print(text)

            return fallback
