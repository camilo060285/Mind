"""Learning Engine - Processes feedback to improve Mind's agents"""

from typing import Dict, Any, List
from pathlib import Path
import json
from datetime import datetime
from .broadcast_memory import BroadcastMemory
from .feedback_collector import FeedbackCollector


class LearningEngine:
    """Processes data from broadcasts to improve agents"""

    def __init__(self):
        self.memory = BroadcastMemory()
        self.feedback = FeedbackCollector()
        self.insights_dir = Path.home() / ".mind" / "learning_insights"
        self.insights_dir.mkdir(parents=True, exist_ok=True)

    def analyze_learning_opportunity(self) -> Dict[str, Any]:
        """Identify what Mind should learn next"""

        # Get insights from broadcast memory
        memory_insights = self.memory.extract_insights()

        # Get feedback summaries
        feedback_summary = self.feedback.get_all_feedback_summary()

        # Identify learning opportunities
        opportunities = {
            "timestamp": datetime.now().isoformat(),
            "broadcast_patterns": self._analyze_broadcast_patterns(memory_insights),
            "agent_improvements": self._suggest_agent_improvements(feedback_summary),
            "prompt_optimization": self._suggest_prompt_optimization(memory_insights),
            "next_agent_types": self._identify_emerging_agents(memory_insights),
            "priority_actions": self._prioritize_actions(
                memory_insights, feedback_summary
            ),
        }

        # Save opportunities
        with open(self.insights_dir / "learning_opportunities.json", "w") as f:
            json.dump(opportunities, f, indent=2)

        return opportunities

    def _analyze_broadcast_patterns(self, insights: Dict) -> Dict[str, Any]:
        """Analyze patterns in broadcasts"""
        return {
            "high_performing_topics": insights.get("high_performing_topics", []),
            "low_performing_topics": insights.get("low_performing_topics", []),
            "agent_patterns": insights.get("agent_patterns", {}),
            "recommendation": (
                insights.get("recommendations", [])[0]
                if insights.get("recommendations")
                else "Collect more data"
            ),
        }

    def _suggest_agent_improvements(self, feedback_summary: Dict) -> List[Dict]:
        """Suggest improvements to agents based on feedback"""
        improvements = []

        for agent_name, summary in feedback_summary.get("agent_summaries", {}).items():
            if summary.get("total_feedback", 0) >= 3:
                avg_score = summary.get("average_quality_score", 0)

                improvement = {
                    "agent": agent_name,
                    "current_score": avg_score,
                    "improvement_needed": avg_score < 7,
                    "focus_areas": summary.get("top_improvement_areas", []),
                    "leverage_strengths": summary.get("top_strengths", []),
                }
                improvements.append(improvement)

        return improvements

    def _suggest_prompt_optimization(self, insights: Dict) -> Dict[str, Any]:
        """Suggest prompt refinements based on performance"""

        high_performers = self.memory.get_high_performers(5)

        prompts_to_optimize = {
            "MarketAnalystAgent": {
                "current_focus": "market analysis",
                "optimization": "Focus on emotion and sentiment, not just facts",
                "example_success": (
                    high_performers[0]["topic"] if high_performers else None
                ),
            },
            "NewsScriptAgent": {
                "current_focus": "professional scripts",
                "optimization": "Add more narrative tension and pacing variation",
                "word_count_optimal": insights.get("agent_patterns", {}).get(
                    "script_length_range", (50, 150)
                ),
            },
            "AnchorDirectorAgent": {
                "current_focus": "technical directions",
                "optimization": "Add emotional cues and audience connection moments",
            },
        }

        return prompts_to_optimize

    def _identify_emerging_agents(self, insights: Dict) -> List[Dict]:
        """Identify new agent types that should be created"""

        emerging = []

        if insights.get("broadcasts", 0) > 10:
            emerging.append(
                {
                    "name": "SentimentAnalystAgent",
                    "purpose": "Gauge market sentiment beyond facts",
                    "reason": "High performers show emotional engagement",
                    "readiness": "Ready to prototype",
                }
            )

        if insights.get("broadcasts", 0) > 20:
            emerging.append(
                {
                    "name": "PredictionAgent",
                    "purpose": "Predict which stories will trend",
                    "reason": "Pattern recognition emerging from data",
                    "readiness": "Sufficient data collected",
                }
            )

        if insights.get("broadcasts", 0) > 30:
            emerging.append(
                {
                    "name": "RetentionOptimizer",
                    "purpose": "Keep viewers engaged throughout broadcast",
                    "reason": "Watch time patterns visible",
                    "readiness": "Ready to implement",
                }
            )

        return emerging

    def _prioritize_actions(
        self, memory_insights: Dict, feedback_summary: Dict
    ) -> List[str]:
        """Prioritize next actions for Mind"""

        actions = []
        total_broadcasts = memory_insights.get("total_broadcasts", 0)

        if total_broadcasts < 5:
            actions.append(
                "Collect more broadcast data (need >5 to establish patterns)"
            )
        elif total_broadcasts < 20:
            actions.append("Fine-tune agent prompts based on current feedback")
            actions.append("Identify top performing topic patterns")
        elif total_broadcasts < 50:
            actions.append("Prototype new agent types (SentimentAnalyst, Predictor)")
            actions.append("Optimize prompt formulations")
            actions.append("Create continuous improvement loop")
        else:
            actions.append("Deploy new agent types")
            actions.append("Implement advanced learning mechanisms")
            actions.append("Build cross-product learning (apply to other products)")

        actions.append("Monitor feedback continuously")
        return actions

    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive learning report"""

        report = {
            "timestamp": datetime.now().isoformat(),
            "learning_opportunities": self.analyze_learning_opportunity(),
            "broadcast_memory": self.memory.get_learning_summary(),
            "feedback_summary": self.feedback.get_all_feedback_summary(),
            "readiness_assessment": self._assess_readiness(),
        }

        # Save report
        with open(self.insights_dir / "learning_report.json", "w") as f:
            json.dump(report, f, indent=2)

        return report

    def _assess_readiness(self) -> Dict[str, Any]:
        """Assess Mind's readiness for next evolution phase"""

        memory_insights = self.memory.extract_insights()
        total_broadcasts = memory_insights.get("total_broadcasts", 0)

        return {
            "phase": self._get_evolution_phase(total_broadcasts),
            "data_collected": total_broadcasts,
            "ready_for_optimization": total_broadcasts >= 5,
            "ready_for_new_agents": total_broadcasts >= 20,
            "ready_for_autonomy": total_broadcasts >= 50,
            "next_milestone": (
                f"{50 - total_broadcasts} more broadcasts"
                if total_broadcasts < 50
                else "Advanced autonomy"
            ),
        }

    def _get_evolution_phase(self, broadcasts: int) -> str:
        """Determine Mind's evolution phase"""
        if broadcasts < 5:
            return "Data Collection"
        elif broadcasts < 20:
            return "Pattern Recognition"
        elif broadcasts < 50:
            return "Agent Emergence"
        else:
            return "Advanced Learning"
