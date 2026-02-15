"""Lightweight broadcast pipeline for NewscastStudio."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from mind.cognition import get_default_llm


logger = logging.getLogger("NewscastBroadcastPipeline")


class BroadcastStatus(str, Enum):
    """Broadcast lifecycle states."""
    INIT = "init"
    ANALYZING = "analyzing"
    SCRIPTING = "scripting"
    APPROVED = "approved"
    FAILED = "failed"


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
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Create a broadcast with analysis and script stages, with error recovery."""
        broadcast_id = self._generate_broadcast_id(topic)
        broadcast_path = self.broadcasts_dir / broadcast_id
        broadcast_path.mkdir(parents=True, exist_ok=True)

        try:
            # Stage 1: Analysis with retry
            logger.info(f"[{broadcast_id}] Stage 1: Analyzing topic '{topic}'")
            analysis = self._run_with_retry(
                stage="analysis",
                broadcast_id=broadcast_id,
                broadcast_path=broadcast_path,
                fn=lambda: self._analyze(topic, context, tone),
                max_retries=max_retries,
            )

            if not analysis:
                return {"status": "failed", "error": "Analysis stage failed after retries"}

            # Stage 2: Script writing with retry
            logger.info(f"[{broadcast_id}] Stage 2: Writing script")
            word_count = int((duration / 60) * 150)
            script = self._run_with_retry(
                stage="scripting",
                broadcast_id=broadcast_id,
                broadcast_path=broadcast_path,
                fn=lambda: self._generate_script(topic, analysis, duration, tone),
                max_retries=max_retries,
            )

            if not script:
                return {"status": "failed", "error": "Script stage failed after retries"}

            # Save final broadcast
            broadcast = {
                "id": broadcast_id,
                "title": topic,
                "context": context,
                "created_at": datetime.now().isoformat(),
                "duration_seconds": duration,
                "status": BroadcastStatus.APPROVED.value,
                "analysis": analysis,
                "script": script,
            }

            broadcast_file = broadcast_path / "broadcast.json"
            with open(broadcast_file, "w") as f:
                json.dump(broadcast, f, indent=2)

            logger.info(f"[{broadcast_id}] Broadcast created successfully")
            return {
                "status": "success",
                "broadcast_id": broadcast_id,
                "broadcast_path": str(broadcast_path),
            }

        except Exception as e:
            logger.error(f"[{broadcast_id}] Broadcast creation failed: {e}")
            return {"status": "failed", "error": str(e), "broadcast_id": broadcast_id}

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

    def _analyze(self, topic: str, context: str, tone: str) -> str:
        """Perform market analysis for topic."""
        prompt = (
            "Analyze this market topic for a professional broadcast. "
            "Provide a short hook, 3 key points, and why it matters.\n\n"
            f"Topic: {topic}\n"
            f"Context: {context}\n"
            f"Tone: {tone}\n"
        )
        return self.llm.generate(prompt, n_predict=500)

    def _generate_script(self, topic: str, analysis: str, duration: int, tone: str) -> str:
        """Generate broadcast script from analysis."""
        word_count = int((duration / 60) * 150)
        prompt = (
            f"Write a {word_count}-word broadcast script ({duration}s). "
            "Structure: intro, body, outlook, sign-off.\n\n"
            f"Topic: {topic}\n"
            f"Analysis: {analysis}\n"
            f"Tone: {tone}\n"
        )
        return self.llm.generate(prompt, n_predict=700)

    def _run_with_retry(
        self,
        stage: str,
        broadcast_id: str,
        broadcast_path: Path,
        fn: callable,
        max_retries: int = 2,
    ) -> Optional[str]:
        """Run a stage with retry logic and persistence."""
        for attempt in range(1, max_retries + 1):
            try:
                result = fn()
                if not result or not result.strip():
                    logger.warning(f"[{broadcast_id}] {stage} attempt {attempt} returned empty result")
                    continue
                logger.info(f"[{broadcast_id}] {stage} succeeded on attempt {attempt}")
                return result
            except Exception as e:
                logger.warning(f"[{broadcast_id}] {stage} attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    logger.error(f"[{broadcast_id}] {stage} failed after {max_retries} attempts")
                    return None
        return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = topic[:30].lower().replace(" ", "_")
        return f"broadcast_{timestamp}_{topic_slug}"
