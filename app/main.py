from services.text_adapter_allround import analyze_text_allround
from conversation.conversation_engine import ConversationEngine


def main():
    conversation_engine = ConversationEngine()

    print("\n=== CROSSSHIELD AI : REAL-TIME FRAUD DETECTION ===")
    print("Type messages one by one. Type 'exit' to stop.\n")

    while True:
        message = input("> ")
        if message.lower() == "exit":
            break

        # --------------------------------------------------
        # 1️⃣ Run text moderation
        # --------------------------------------------------
        result = analyze_text_allround(message)

        # Normalize output (VERY IMPORTANT)
        if isinstance(result, dict):
            message_signals = result.get("signals", [])
            message_risk = float(result.get("risk_score", 0.0))
        else:
            # result is List[FraudSignal] or List[dict]
            message_signals = result
            message_risk = 0.0

        # Convert signals → dicts
        dict_signals = []
        for s in message_signals:
            if hasattr(s, "to_dict"):
                dict_signals.append(s.to_dict())
            else:
                dict_signals.append(s)

        # --------------------------------------------------
        # 2️⃣ Conversation-level analysis
        # --------------------------------------------------
        conversation_engine.ingest(dict_signals)
        conversation_result = conversation_engine.analyze()

        # --------------------------------------------------
        # 3️⃣ DISPLAY MESSAGE-LEVEL OUTPUT
        # --------------------------------------------------
        print("\n--- MESSAGE ANALYSIS ---")
        print(f"Message Risk: {message_risk:.2f}")

        if dict_signals:
            print("Message Signals:")
            for s in dict_signals:
                print(
                    f"  • {s['signal_type']} → {s['value']} "
                    f"({int(s['confidence'] * 100)}%)"
                )
        else:
            print("• No fraud signals detected ✅")

        # --------------------------------------------------
        # 4️⃣ DISPLAY CONVERSATION-LEVEL OUTPUT
        # --------------------------------------------------
        print("\n--- CONVERSATION ANALYSIS ---")
        print(f"Conversation Risk: {conversation_result['conversation_risk']:.2f}")
        print(f"Danger Level: {conversation_result['danger_level']}")

        if conversation_result["flags"]:
            print("Flags:")
            for f in conversation_result["flags"]:
                print(f"  - {f}")

        # --------------------------------------------------
        # 5️⃣ FINAL DECISION (AUTHORITATIVE)
        # --------------------------------------------------
        final_risk = max(message_risk, conversation_result["conversation_risk"])

        if final_risk >= 0.7:
            recommendation = "🚫 BLOCK"
        elif final_risk >= 0.4:
            recommendation = "⚠️  WARN"
        else:
            recommendation = "✅ ALLOW"

        print(f"\n🎯 FINAL RECOMMENDATION: {recommendation}")
        print(f"Final Risk Score: {final_risk:.2f}")

        print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
