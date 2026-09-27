import re
from typing import Tuple

AUTO_REPLY_PATTERNS = [
    r"thank you for contacting",
    r"our team will respond shortly",
    r"we will get back to you",
    r"automatic reply",
    r"auto-reply",
    r"out of office",
    r"thanks for reaching out"
]

HOSTILE_STOP_PATTERNS = [
    r"stop messaging",
    r"not interested",
    r"useless spam",
    r"bothering me",
    r"dont message",
    r"don't message",
    r"unsubscribe",
    r"stop"
]

AFFIRMATIVE_PATTERNS = [
    r"yes",
    r"ok",
    r"okay",
    r"sure",
    r"let's do it",
    r"lets do it",
    r"send abstract",
    r"draft",
    r"confirm",
    r"proceed",
    r"sounds good",
    r"go ahead",
    r"send please",
    r"please send"
]

OUT_OF_SCOPE_PATTERNS = [
    r"\bgst\b",
    r"tax filing",
    r"accounting",
    r"ca filing",
    r"income tax"
]

class IntentClassifier:
    @staticmethod
    def classify(text: str) -> Tuple[str, float]:
        """
        Classifies incoming merchant/customer reply text.
        Returns (intent: str, confidence: float)
        """
        lower = text.lower().strip()

        # 1. Auto-reply detection
        for pat in AUTO_REPLY_PATTERNS:
            if re.search(pat, lower):
                return "auto_reply", 0.95

        # 2. Hostile / Stop opt-out
        for pat in HOSTILE_STOP_PATTERNS:
            if re.search(pat, lower):
                return "stop", 0.95

        # 3. Out of scope ask
        for pat in OUT_OF_SCOPE_PATTERNS:
            if re.search(pat, lower):
                return "out_of_scope", 0.90

        # 4. Affirmative commitment
        for pat in AFFIRMATIVE_PATTERNS:
            if re.search(pat, lower):
                return "affirmative", 0.90

        # 5. Questions / Objections
        if "?" in lower or any(w in lower for w in ["how", "what", "why", "when", "cost", "price"]):
            return "question", 0.80

        # 6. Default fallback
        return "unclear", 0.50
