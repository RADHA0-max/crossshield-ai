from collections import deque, Counter
from typing import List, Dict


class ConversationEngine:
    """
    Conversation-level fraud escalation engine.
    Works ONLY on signals produced by text moderation.
    """

    def __init__(self, window_size: int = 6):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)

    # --------------------------------------------------
    # Ingest signals from ONE message
    # --------------------------------------------------
    def ingest(self, message_signals: List[Dict]):
        """
        message_signals: list of dicts like
        {
            "signal_type": "...",
            "value": "...",
            "confidence": 0.75
        }
        """
        if not message_signals:
            return

        for s in message_signals:
            self.history.append(s)

    # --------------------------------------------------
    # Analyze entire conversation window
    # --------------------------------------------------
    def analyze(self) -> Dict:
        if len(self.history) < 2:
            return {
                "conversation_risk": 0.0,
                "danger_level": "SAFE",
                "flags": [],
                "signal_count": len(self.history),
            }

        types = [s["signal_type"] for s in self.history]
        values = [s["value"] for s in self.history]
        confidences = [s["confidence"] for s in self.history]

        type_count = Counter(types)
        value_count = Counter(values)

        risk = 0.0
        flags = []

        # 1️⃣ Repeated impersonation
        if type_count.get("impersonation", 0) >= 2:
            flags.append("repeated impersonation")
            risk += 0.30

        # 2️⃣ Identity → Asset progression (order matters)
        if "impersonation" in types and "asset_request" in types:
            if types.index("impersonation") < types.index("asset_request"):
                flags.append("identity followed by asset request")
                risk += 0.40

        # 3️⃣ Escalating manipulation
        if type_count.get("manipulation", 0) >= 2:
            flags.append("escalating psychological pressure")
            risk += 0.25

        # 4️⃣ Persistent role reinforcement
        if value_count and value_count.most_common(1)[0][1] >= 3:
            flags.append("persistent identity reinforcement")
            risk += 0.20

        # 5️⃣ High average confidence
        avg_conf = sum(confidences) / len(confidences)
        if avg_conf >= 0.75:
            flags.append("sustained high-confidence signals")
            risk += 0.20

        # --------------------------------------------------
        # Final score & danger level
        # --------------------------------------------------
        risk_score = round(min(1.0, risk), 2)

        if risk_score < 0.3:
            level = "SAFE"
        elif risk_score < 0.6:
            level = "SUSPICIOUS"
        elif risk_score < 0.85:
            level = "HIGH_RISK"
        else:
            level = "CRITICAL"

        return {
            "conversation_risk": risk_score,
            "danger_level": level,
            "flags": flags,
            "signal_count": len(self.history),
        }


# --------------------------------------------------
# Local sanity test (optional)
# --------------------------------------------------
if __name__ == "__main__":
    engine = ConversationEngine()

    engine.ingest([
        {"signal_type": "impersonation", "value": "family_impersonation", "confidence": 0.7}
    ])
    engine.ingest([
        {"signal_type": "manipulation", "value": "urgency", "confidence": 0.8}
    ])
    engine.ingest([
        {"signal_type": "asset_request", "value": "money", "confidence": 0.9}
    ])

    print(engine.analyze())
