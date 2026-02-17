class FraudSignal:
    def __init__(
        self,
        source,              # text | voice | web | conversation | system
        signal_type,         # intent | impersonation | manipulation | power_request | anomaly
        value,               # semantic meaning of the signal
        confidence=0.0,      # 0.0 – 1.0
        metadata=None        # optional extra info
    ):
        self.source = source
        self.signal_type = signal_type
        self.value = value
        self.confidence = confidence
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "source": self.source,
            "signal_type": self.signal_type,
            "value": self.value,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }
