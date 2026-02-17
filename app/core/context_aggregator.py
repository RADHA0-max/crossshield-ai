from core.fraud_context import FraudContext


class FraudContextAggregator:
    def __init__(self):
        self.context = FraudContext()

    def ingest_signal(self, signal):
        """
        Update FraudContext using a single FraudSignal.
        This function is deterministic and model-agnostic.
        """

        # Intent signals
        if signal.signal_type == "intent":
            if signal.confidence > self.context.intent_confidence:
                self.context.primary_intent = signal.value
                self.context.intent_confidence = signal.confidence

        # Impersonation signals
        if signal.signal_type == "impersonation":
            self.context.claimed_identity = signal.value
            if signal.confidence > 0.7:
                self.context.impersonation_risk = "high"
            elif signal.confidence > 0.4:
                self.context.impersonation_risk = "medium"

        # Power / asset request signals
        if signal.signal_type == "power_request":
            if signal.value not in self.context.requested_assets:
                self.context.requested_assets.append(signal.value)
            self.context.power_severity = "high"

        # Psychological manipulation
        if signal.signal_type == "manipulation":
            if signal.value not in self.context.psychological_tactics:
                self.context.psychological_tactics.append(signal.value)
            self.context.psychological_intensity = "high"

        # AI / system abuse
        if signal.signal_type == "system_abuse":
            self.context.prompt_attack = True
            self.context.attack_type = signal.value

    def get_context(self):
        return self.context.to_dict()
