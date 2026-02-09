import spacy
from .base_agent import BaseAgent


class GoalInterpreterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="goal_interpreter_agent",
            description="Understands Cristian's intentions and converts them into structured goals.",
        )
        self.nlp = None  # Lazy load on first use

    def _ensure_nlp_loaded(self):
        """Lazy load the spacy model on first use."""
        if self.nlp is None:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                self.logger.warning(
                    "Spacy model 'en_core_web_sm' not found. "
                    "Install it with: python -m spacy download en_core_web_sm"
                )
                # Fall back to a basic tokenizer with sentencizer
                self.nlp = spacy.blank("en")
                if "sentencizer" not in self.nlp.pipe_names:
                    self.nlp.add_pipe("sentencizer")

    def run(self, raw_input: str) -> dict:
        self._ensure_nlp_loaded()
        doc = self.nlp(raw_input)

        # Naive intent: first verb lemma
        intent = None
        for token in doc:
            if token.pos_ == "VERB":
                intent = token.lemma_
                break

        # Naive constraints: sentences containing words like "privacy", "local", "time"
        constraint_keywords = ["privacy", "local", "time", "energy", "budget"]
        constraints = [
            sent.text.strip()
            for sent in doc.sents
            if any(k in sent.text.lower() for k in constraint_keywords)
        ]

        structured_goal = {
            "raw_text": raw_input,
            "intent": intent,
            "constraints": constraints,
            "priority": "normal",
            "emotional_tone": doc.sentiment if hasattr(doc, "sentiment") else None,
        }

        self.log(f"Interpreted goal: {structured_goal}")
        return structured_goal
