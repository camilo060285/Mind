"""YouTube Learning - Extract transcripts and learn from videos"""

import re
from typing import Optional


class YouTubeTextLearner:
    """Extract and learn from YouTube video transcripts"""

    def learn_from_url(self, url: str) -> dict:
        """
        Extract transcript from YouTube video and generate knowledge

        Args:
            url: YouTube video URL

        Returns:
            dict with 'summary' and 'concepts' keys
        """
        try:
            from youtube_transcript_api import YouTubeTranscriptApi

            # Extract video ID from URL
            video_id = self._extract_video_id(url)

            if not video_id:
                raise ValueError("Invalid YouTube URL")

            # Get transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            transcript_text = " ".join([item["text"] for item in transcript])

            # Generate summary and concepts
            summary = self._generate_summary(transcript_text)
            concepts = self._extract_concepts(transcript_text)

            return {"summary": summary, "concepts": concepts, "video_id": video_id}

        except ImportError:
            return {
                "error": "youtube-transcript-api not installed",
                "install": "pip install youtube-transcript-api",
            }
        except Exception as e:
            return {"error": str(e)}

    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r"(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})",
            r"(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def _generate_summary(self, text: str, max_lines: int = 3) -> str:
        """Generate summary from transcript text"""
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return "No content to summarize"

        # Simple extractive summary: first few sentences
        summary_sentences = sentences[:max_lines]
        return ". ".join(summary_sentences) + "."

    def _extract_concepts(self, text: str) -> str:
        """Extract key concepts from transcript"""
        # Simple keyword extraction: find capitalized words
        words = text.split()
        concepts = []

        for word in words:
            if word[0].isupper() and len(word) > 3 and word not in concepts:
                concepts.append(word.rstrip(".,!?"))
                if len(concepts) >= 10:
                    break

        return ", ".join(concepts) if concepts else "No concepts extracted"
