"""Broadcast Memory System - Captures learning from newscast-studio"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List


class BroadcastMemory:
    """Stores and analyzes broadcast performance data for Mind's learning"""

    def __init__(self):
        self.memory_dir = Path.home() / ".mind" / "broadcast_memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.performance_file = self.memory_dir / "performance_log.jsonl"
        self.insights_file = self.memory_dir / "insights.json"

    def record_broadcast(
        self,
        broadcast_id: str,
        topic: str,
        agent_outputs: Dict[str, Any],
        metadata: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """Record a broadcast and its agent outputs for learning"""

        record = {
            "timestamp": datetime.now().isoformat(),
            "broadcast_id": broadcast_id,
            "topic": topic,
            "agent_outputs": agent_outputs,
            "metadata": metadata or {},
            "feedback": None,
            "performance_score": None,
        }

        # Append to performance log
        with open(self.performance_file, "a") as f:
            f.write(json.dumps(record) + "\n")

        return record

    def add_feedback(
        self,
        broadcast_id: str,
        engagement_score: float,
        quality_rating: int,
        user_feedback: str = "",
        tags: List[str] | None = None,
    ) -> Dict[str, Any]:
        """Add performance feedback for a broadcast"""

        feedback = {
            "timestamp": datetime.now().isoformat(),
            "engagement_score": engagement_score,  # 0-100
            "quality_rating": quality_rating,  # 1-10
            "user_feedback": user_feedback,
            "tags": tags or [],
        }

        # Find and update the broadcast record
        records = self._read_records()
        for record in records:
            if record["broadcast_id"] == broadcast_id:
                record["feedback"] = feedback
                record["performance_score"] = (
                    engagement_score * 0.6 + quality_rating * 10
                ) / 2

        self._write_records(records)
        return feedback

    def extract_insights(self) -> Dict[str, Any]:
        """Analyze performance data to extract learning insights"""

        records = self._read_records()
        if not records:
            return {"status": "no_data"}

        # Calculate statistics
        with_feedback = [r for r in records if r.get("feedback")]
        if not with_feedback:
            return {"status": "no_feedback_yet"}

        scores: List[float] = [r["performance_score"] for r in with_feedback]
        avg_score: float = sum(scores) / len(scores)

        # Identify high performers
        high_performers = [
            r for r in with_feedback if r["performance_score"] >= avg_score + 10
        ]
        low_performers = [
            r for r in with_feedback if r["performance_score"] < avg_score - 10
        ]

        # Extract patterns
        insights = {
            "total_broadcasts": len(records),
            "broadcasts_with_feedback": len(with_feedback),
            "average_performance": avg_score,
            "high_performing_topics": self._extract_top_topics(high_performers),
            "low_performing_topics": self._extract_top_topics(low_performers),
            "agent_patterns": self._analyze_agent_patterns(high_performers),
            "recommendations": self._generate_recommendations(
                high_performers, low_performers
            ),
            "last_updated": datetime.now().isoformat(),
        }

        # Save insights
        with open(self.insights_file, "w") as f:
            json.dump(insights, f, indent=2)

        return insights

    def get_high_performers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing broadcasts to learn from"""
        records = self._read_records()
        with_feedback = [r for r in records if r.get("performance_score")]
        sorted_records = sorted(
            with_feedback, key=lambda x: x["performance_score"], reverse=True
        )
        return sorted_records[:limit]

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of what Mind has learned"""
        return self._load_insights()

    def _extract_top_topics(self, records: List[Dict]) -> List[Dict]:
        """Extract and rank topics by performance"""
        topics: Dict[str, Dict[str, Any]] = {}
        for record in records:
            topic = record.get("topic", "unknown")
            if topic not in topics:
                topics[topic] = {"count": 0, "avg_score": 0.0}
            topics[topic]["count"] += 1
            topics[topic]["avg_score"] += record.get("performance_score", 0)

        # Calculate averages and rank
        for topic in topics:
            topics[topic]["avg_score"] /= topics[topic]["count"]

        ranked = sorted(
            [{"topic": t, **v} for t, v in topics.items()],
            key=lambda x: x["avg_score"],
            reverse=True,
        )
        return ranked[:5]

    def _analyze_agent_patterns(self, high_performers: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in high-performing agent outputs"""
        patterns = {
            "script_length_range": (50, 150),  # words
            "analysis_depth": "detailed",
            "direction_specificity": "high",
            "common_themes": [],
        }

        script_lengths = []
        for record in high_performers:
            agent_outputs = record.get("agent_outputs", {})
            script = (
                agent_outputs.get("02_script", {}).get("result", {}).get("script", "")
            )
            if script:
                script_lengths.append(len(script.split()))

        if script_lengths:
            patterns["script_length_range"] = (
                min(script_lengths),
                max(script_lengths),
            )

        return patterns

    def _generate_recommendations(
        self, high_performers: List[Dict], low_performers: List[Dict]
    ) -> List[str]:
        """Generate recommendations for improving agents"""
        recommendations = []

        high_topics = self._extract_top_topics(high_performers)
        if high_topics:
            recommendations.append(
                f"Focus on topics like '{high_topics[0]['topic']}' - "
                f"they perform {high_topics[0]['avg_score']:.0f}/100"
            )

        if len(high_performers) > 5:
            recommendations.append(
                "Enough data collected - ready to fine-tune agent prompts"
            )

        if low_performers:
            recommendations.append(
                "Identify and improve low-performing scripts patterns"
            )

        recommendations.append(
            "Track user engagement metrics to refine success definition"
        )

        return recommendations

    def _read_records(self) -> List[Dict]:
        """Read all broadcast records"""
        records = []
        if self.performance_file.exists():
            with open(self.performance_file, "r") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        return records

    def _write_records(self, records: List[Dict]):
        """Write broadcast records"""
        with open(self.performance_file, "w") as f:
            for record in records:
                f.write(json.dumps(record) + "\n")

    def _load_insights(self) -> Dict[str, Any]:
        """Load cached insights"""
        if self.insights_file.exists():
            with open(self.insights_file, "r") as f:
                return json.load(f)
        return {}
