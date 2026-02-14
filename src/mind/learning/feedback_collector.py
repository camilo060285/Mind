"""Feedback Collector - Gathers user feedback and performance data"""

from typing import Any, Dict, List
from pathlib import Path
import json
from datetime import datetime


class FeedbackCollector:
    """Collects and organizes feedback from users and systems"""

    def __init__(self):
        self.feedback_dir = Path.home() / ".mind" / "feedback"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

    def collect_broadcast_feedback(
        self,
        broadcast_id: str,
        engagement_metrics: Dict[str, Any],
        user_rating: int | None = None,
        comments: str | None = None,
        tags: list | None = None,
    ) -> Dict[str, Any]:
        """
        Collect feedback on a broadcast performance

        Args:
            broadcast_id: Broadcast identifier
            engagement_metrics: {views, shares, likes, comments, watch_time, etc}
            user_rating: 1-10 quality rating
            comments: User comments/suggestions
            tags: Performance tags (good_topic, poor_script, etc)

        Returns:
            Feedback record
        """
        feedback = {
            "timestamp": datetime.now().isoformat(),
            "broadcast_id": broadcast_id,
            "engagement": engagement_metrics,
            "user_rating": user_rating,
            "comments": comments,
            "tags": tags or [],
        }

        # Save feedback
        feedback_file = self.feedback_dir / f"{broadcast_id}_feedback.json"
        with open(feedback_file, "w") as f:
            json.dump(feedback, f, indent=2)

        return feedback

    def collect_agent_feedback(
        self,
        agent_name: str,
        broadcast_id: str,
        quality_score: int,
        improvement_areas: list | None = None,
        strengths: list | None = None,
    ) -> Dict[str, Any]:
        """Collect feedback specifically about agent performance"""

        feedback = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "broadcast_id": broadcast_id,
            "quality_score": quality_score,  # 1-10
            "improvement_areas": improvement_areas or [],
            "strengths": strengths or [],
        }

        agent_feedback_file = self.feedback_dir / f"{agent_name}_feedback.jsonl"
        with open(agent_feedback_file, "a") as f:
            f.write(json.dumps(feedback) + "\n")

        return feedback

    def get_agent_performance_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get performance summary for an agent"""
        agent_feedback_file = self.feedback_dir / f"{agent_name}_feedback.jsonl"

        if not agent_feedback_file.exists():
            return {"status": "no_feedback"}

        scores: List[int] = []
        improvement_areas_dict: Dict[str, int] = {}
        strengths_dict: Dict[str, int] = {}

        with open(agent_feedback_file, "r") as f:
            for line in f:
                if line.strip():
                    feedback = json.loads(line)
                    scores.append(feedback.get("quality_score", 0))

                    for area in feedback.get("improvement_areas", []):
                        improvement_areas_dict[area] = (
                            improvement_areas_dict.get(area, 0) + 1
                        )

                    for strength in feedback.get("strengths", []):
                        strengths_dict[strength] = strengths_dict.get(strength, 0) + 1

        avg_score: float = sum(scores) / len(scores) if scores else 0.0

        return {
            "agent_name": agent_name,
            "total_feedback": len(scores),
            "average_quality_score": avg_score,
            "top_improvement_areas": sorted(
                improvement_areas_dict.items(), key=lambda x: x[1], reverse=True
            )[:3],
            "top_strengths": sorted(
                strengths_dict.items(), key=lambda x: x[1], reverse=True
            )[:3],
        }

    def get_all_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of all feedback collected"""
        total_feedback_files = len(list(self.feedback_dir.glob("*_feedback.json")))
        agent_feedback_files = list(self.feedback_dir.glob("*_feedback.jsonl"))

        agent_summaries = {}
        for agent_file in agent_feedback_files:
            agent_name = agent_file.stem.replace("_feedback", "")
            agent_summaries[agent_name] = self.get_agent_performance_summary(agent_name)

        return {
            "total_broadcast_feedback": total_feedback_files,
            "total_agent_feedback_entries": sum(
                1 for f in agent_feedback_files for line in open(f) if line.strip()
            ),
            "agent_summaries": agent_summaries,
            "last_updated": datetime.now().isoformat(),
        }
