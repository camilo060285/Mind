"""Lightweight broadcast pipeline for NewscastStudio."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mind.cognition import get_default_llm


class NewscastBroadcastPipeline:
    """Create and manage simple news broadcasts."""

    def __init__(self, llm: Optional[Any] = None, broadcasts_dir: Optional[Path] = None):
        self.llm = llm or get_default_llm()
        default_dir = Path.home() / ".mind" / "newscast_studio" / "broadcasts"
        self.broadcasts_dir = Path(broadcasts_dir or default_dir)
        self.broadcasts_dir.mkdir(parents=True, exist_ok=True)

    def create_broadcast(
        self,
        topic: str,
        context: str = "",
        duration: int = 60,
        tone: str = "professional",
    ) -> Dict[str, Any]:
        """Create a broadcast with analysis and script stages."""
        broadcast_id = self._generate_broadcast_id(topic)
        broadcast_path = self.broadcasts_dir / broadcast_id
        broadcast_path.mkdir(parents=True, exist_ok=True)

        analysis_prompt = (
            "Analyze this market topic for a professional broadcast. "
            "Provide a short hook, 3 key points, and why it matters.\n\n"
            f"Topic: {topic}\n"
            f"Context: {context}\n"
            f"Tone: {tone}\n"
        )
        analysis = self.llm.generate(analysis_prompt, n_predict=500)

        word_count = int((duration / 60) * 150)
        script_prompt = (
            f"Write a {word_count}-word broadcast script ({duration}s). "
            "Structure: intro, body, outlook, sign-off.\n\n"
            f"Topic: {topic}\n"
            f"Analysis: {analysis}\n"
            f"Tone: {tone}\n"
        )
        script = self.llm.generate(script_prompt, n_predict=700)

        broadcast = {
            "id": broadcast_id,
            "title": topic,
            "context": context,
            "created_at": datetime.now().isoformat(),
            "duration_seconds": duration,
            "status": "approved",
            "analysis": analysis,
            "script": script,
        }

        broadcast_file = broadcast_path / "broadcast.json"
        with open(broadcast_file, "w") as f:
            json.dump(broadcast, f, indent=2)

        return {
            "status": "success",
            "broadcast_id": broadcast_id,
            "broadcast_path": str(broadcast_path),
        }

    def list_broadcasts(self) -> List[Dict[str, Any]]:
        """List recent broadcasts."""
        broadcasts = []
        for broadcast_dir in sorted(self.broadcasts_dir.iterdir(), reverse=True):
            if broadcast_dir.is_dir():
                broadcast_file = broadcast_dir / "broadcast.json"
                if broadcast_file.exists():
                    with open(broadcast_file, "r") as f:
                        data = json.load(f)
                        broadcasts.append(
                            {
                                "id": data.get("id"),
                                "title": data.get("title"),
                                "created_at": data.get("created_at"),
                                "status": data.get("status"),
                            }
                        )
        return broadcasts

    def get_broadcast(self, broadcast_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a broadcast by ID."""
        broadcast_file = self.broadcasts_dir / broadcast_id / "broadcast.json"
        if broadcast_file.exists():
            with open(broadcast_file, "r") as f:
                return json.load(f)
        return None

    def _generate_broadcast_id(self, topic: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = topic[:30].lower().replace(" ", "_")
        return f"broadcast_{timestamp}_{topic_slug}"
