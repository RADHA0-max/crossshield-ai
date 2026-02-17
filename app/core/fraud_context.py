class FraudContext:
    def __init__(self):
        # Intent
        self.primary_intent = None
        self.intent_confidence = 0.0

        # Manipulation / social engineering
        self.psychological_tactics = []
        self.psychological_intensity = "low"

        # Impersonation
        self.claimed_identity = None
        self.impersonation_risk = "low"

        # Requested assets (OTP, password, money, etc.)
        self.requested_assets = []
        self.power_severity = "low"

        # AI / system abuse
        self.prompt_attack = False
        self.attack_type = None

    def to_dict(self):
        return {
            "primary_intent": self.primary_intent,
            "intent_confidence": self.intent_confidence,
            "psychological_tactics": self.psychological_tactics,
            "psychological_intensity": self.psychological_intensity,
            "claimed_identity": self.claimed_identity,
            "impersonation_risk": self.impersonation_risk,
            "requested_assets": self.requested_assets,
            "power_severity": self.power_severity,
            "prompt_attack": self.prompt_attack,
            "attack_type": self.attack_type,
        }

