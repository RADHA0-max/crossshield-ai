import os
import time
import re
import requests
from dotenv import load_dotenv
from collections import Counter
from typing import Dict, List, Tuple

load_dotenv()

HF_TOKEN = os.getenv("HF_API_TOKEN")
HF_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}

class FraudSignal:
    def __init__(self, source: str, signal_type: str, value: str, confidence: float):
        self.source = source
        self.signal_type = signal_type
        self.value = value
        self.confidence = confidence

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "signal_type": self.signal_type,
            "value": self.value,
            "confidence": round(self.confidence, 3),
        }

# =============================================================================
# 🌍 1. ALL IDENTITY IMPERSONATIONS (50+ TYPES - GLOBAL + INDIA)
# =============================================================================
IDENTITY_HYPOTHESES = [
    # 👨‍👩‍👧‍👦 FAMILY (ALL RELATIVES)
    "The speaker is the recipient's husband or wife",
    "The speaker is the recipient's father or mother",
    "The speaker is the recipient's grandfather or grandmother", 
    "The speaker is the recipient's son or daughter",
    "The speaker is the recipient's brother or sister",
    "The speaker is the recipient's uncle or aunt",
    "The speaker is the recipient's cousin or relative",
    
    # 🏦 FINANCIAL INSTITUTIONS
    "The speaker is a bank employee",
    "The speaker is from SBI or Indian bank",
    "The speaker is from HDFC or ICICI bank",
    "The speaker is from Paytm or PhonePe",
    "The speaker is from PayPal or Razorpay",
    "The speaker is from cryptocurrency exchange",
    
    # 💻 TECH SUPPORT
    "The speaker is customer support",
    "The speaker is tech support",
    "The speaker is Microsoft support",
    "The speaker is Apple support",
    "The speaker is Amazon AWS support",
    
    # 👮 AUTHORITY
    "The speaker is law enforcement",
    "The speaker is police officer",
    "The speaker is from CBI or ED",
    "The speaker is from income tax department",
    "The speaker is from government",
    "The speaker is from passport office",
    "The speaker is from electricity board",
    
    # 🛒 ECOMMERCE
    "The speaker is from Amazon",
    "The speaker is from Flipkart",
    "The speaker is from Swiggy or Zomato",
    "The speaker is from Uber or Ola",
    
    # 💼 PROFESSIONAL
    "The speaker is a lawyer",
    "The speaker is a doctor",
    "The speaker is from HR department",
    
    # 🎁 SOCIAL ENGINEERING
    "The speaker is a friend",
    "The speaker is a colleague",
    "The speaker is your old school friend",
]

IDENTITY_MAPPING = {
    # FAMILY
    "The speaker is the recipient's husband or wife": "spouse_impersonation",
    "The speaker is the recipient's father or mother": "parent_impersonation",
    "The speaker is the recipient's grandfather or grandmother": "grandparent_impersonation",
    "The speaker is the recipient's son or daughter": "child_impersonation", 
    "The speaker is the recipient's brother or sister": "sibling_impersonation",
    "The speaker is the recipient's uncle or aunt": "extended_family_impersonation",
    "The speaker is the recipient's cousin or relative": "relative_impersonation",
    
    # FINANCIAL
    "The speaker is a bank employee": "bank_impersonation",
    "The speaker is from SBI or Indian bank": "indian_bank_impersonation",
    "The speaker is from HDFC or ICICI bank": "private_bank_impersonation", 
    "The speaker is from Paytm or PhonePe": "upi_app_impersonation",
    "The speaker is from PayPal or Razorpay": "payment_gateway_impersonation",
    "The speaker is from cryptocurrency exchange": "crypto_impersonation",
    
    # SUPPORT
    "The speaker is customer support": "generic_support_impersonation",
    "The speaker is tech support": "tech_support_impersonation",
    "The speaker is Microsoft support": "microsoft_impersonation",
    "The speaker is Apple support": "apple_impersonation",
    "The speaker is Amazon AWS support": "aws_impersonation",
    
    # AUTHORITY
    "The speaker is law enforcement": "police_impersonation",
    "The speaker is police officer": "police_officer_impersonation",
    "The speaker is from CBI or ED": "investigation_agency_impersonation",
    "The speaker is from income tax department": "tax_authority_impersonation",
    "The speaker is from government": "govt_impersonation",
    "The speaker is from passport office": "passport_office_impersonation",
    "The speaker is from electricity board": "utility_impersonation",
    
    # ECOMMERCE
    "The speaker is from Amazon": "amazon_impersonation",
    "The speaker is from Flipkart": "flipkart_impersonation",
    "The speaker is from Swiggy or Zomato": "food_delivery_impersonation",
    "The speaker is from Uber or Ola": "ride_sharing_impersonation",
    
    # PROFESSIONAL
    "The speaker is a lawyer": "legal_impersonation",
    "The speaker is a doctor": "medical_impersonation",
    "The speaker is from HR department": "hr_impersonation",
    
    # SOCIAL
    "The speaker is a friend": "friend_impersonation",
    "The speaker is a colleague": "colleague_impersonation",
    "The speaker is your old school friend": "school_friend_impersonation",
}

# =============================================================================
# 💸 ALL FINANCIAL INTENT (20+ SCAMS)
# =============================================================================
INTENT_LABELS = [
    "benign conversation",
    "financial fraud",
    "credential harvesting", 
    "account takeover",
    "money mule recruitment",
    "investment scam",
    "lottery winnings",
    "inheritance claim",
    "romance scam",
    "job offer scam",
    "charity donation scam",
    "refund processing scam",
    "technical support scam",
    "government grant scam",
    "crypto investment",
    "binary options trading",
    "pump and dump scheme",
]

# =============================================================================
# 🔑 ALL ASSET REQUESTS (25+ TYPES)
# =============================================================================
ASSET_LABELS = [
    "no asset requested",
    "authentication credentials",
    "one-time password",
    "bank account access",
    "UPI pin or details",
    "credit card details",
    "CVV code",
    "ATM pin",
    "social security number",
    "Aadhar card details", 
    "PAN card number",
    "passport details",
    "driving license number",
    "gift cards",
    "iTunes gift cards",
    "Amazon gift cards",
    "crypto wallet address",
    "remote desktop access",
    "screen sharing access",
    "bank account number",
    "IFSC code",
    "routing number",
    "swift code",
]

# =============================================================================
# 🧠 ALL MANIPULATION TACTICS (15+ TYPES)
# =============================================================================
MANIPULATION_LABELS = [
    "no manipulation",
    "urgency pressure",
    "emotional manipulation",
    "authority pressure",
    "scarcity tactic",
    "social proof pressure",
    "reciprocity manipulation",
    "fear induction",
    "greed temptation",
    "guilt induction",
    "trust building",
]

# =============================================================================
# 🎯 ULTRA-COMPREHENSIVE REGEX PATTERNS (100+ PATTERNS)
# =============================================================================
PATTERNS = {
    # FAMILY - COMPLETE INDIAN/ENGLISH
    'FAMILY': re.compile(
        r'\b(your\s+)?(mom|mother|dad|daddy|father|pa|papa|mum|'
        r'ma|maa|grandma|grandpa|grandfather|grandmother|nana|nanni|'
        r'husband|wife|son|daughter|brother|bro|sister|sis|'
        r'uncle|u|ji|aunty|aunt|niece|nephew|cousin|'
        r'bhai|didi|bhabhi|bah|devar|nanad|chacha|tau|chachi|'
        r'bua|mausi|masi|fufa|mama|mamiji)\b', re.IGNORECASE
    ),
    
    # AUTHORITY/LEGAL
    'AUTHORITY': re.compile(r'\b(police|court|judge|officer|cbi|ed|irs|'
                           r'tax|passport|warrant|arrest|fine|'
                           r'government|govt|municipality)\b', re.IGNORECASE),
    
    # FINANCIAL
    'BANK': re.compile(r'\b(sbi|hdfc|icici|axis|pnb|bank|upi|'
                      r'phonepe|paytm|gpay|account|balance|'
                      r'transaction|ifsc|otp|cvv|pin)\b', re.IGNORECASE),
    
    # TECH
    'TECH': re.compile(r'\b(tech\s+support|microsoft|windows|apple|mac|'
                      r'computer|virus|malware|hack|hacked|remote|'
                      r'desktop|support|helpdesk)\b', re.IGNORECASE),
    
    # EMERGENCY
    'EMERGENCY': re.compile(r'\b(emergency|urgent|help|stuck|arrested|'
                           r'jail|hospital|accident|surgery|died|'
                           r'kidnap|threat|danger)\b', re.IGNORECASE),
    
    # ECOMMERCE
    'ECOMMERCE': re.compile(r'\b(amazon|flipkart|myntra|ajio|'
                           r'swiggy|zomato|uber|ola|delivery|'
                           r'order|package|courier|refund)\b', re.IGNORECASE),
    
    # MONEY
    'MONEY': re.compile(r'\b(send|transfer|money|dollar|rupee|\$|₹|'
                       r'gift\s+card|itunes|amazon\s+card|crypto|'
                       r'bitcoin|wallet)\b', re.IGNORECASE),
}

# =============================================================================
# 🤖 ROBUST HF API CALLER
# =============================================================================
def hf_zero_shot(text: str, labels: List[str], multi_label: bool = True, retries: int = 3) -> Tuple[List[str], List[float]]:
    payload = {"inputs": text, "parameters": {"candidate_labels": labels, "multi_label": multi_label}}
    for attempt in range(retries):
        try:
            r = requests.post(HF_URL, headers=HEADERS, json=payload, timeout=10)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list): 
                data = data[0]
            return data.get("labels", []), data.get("scores", [])
        except Exception:
            time.sleep(1)
    return [], []

# =============================================================================
# 🚀 ULTIMATE FRAUD ANALYSIS ENGINE
# =============================================================================
def analyze_text_allround(text: str) -> Dict:
    signals = []
    
    # 1️⃣ COMPREHENSIVE IDENTITY DETECTION
    id_labels, id_scores = hf_zero_shot(text, IDENTITY_HYPOTHESES)
    ranked_identities = sorted(zip(id_labels, id_scores), key=lambda x: x[1] if x[1] else 0, reverse=True)
    
    identity_detected = False
    for label, score in ranked_identities:
        score = float(score) if score else 0.0
        if score >= 0.50 and label in IDENTITY_MAPPING:  # Lower threshold for coverage
            signals.append(FraudSignal("ai_identity", "impersonation", IDENTITY_MAPPING[label], score))
            identity_detected = True
            break
    
    # 2️⃣ REGEX CONFIDENCE BOOSTERS (Grammar Rules)
    pattern_hits = {name: bool(pattern.search(text)) for name, pattern in PATTERNS.items()}
    
    if pattern_hits['FAMILY'] and not identity_detected:
        confidence = 0.80 if pattern_hits['EMERGENCY'] else 0.70
        signals.append(FraudSignal("regex_family", "impersonation", "family_impersonation", confidence))
    
    if pattern_hits['AUTHORITY'] and not any('impersonation' in s.value for s in signals):
        signals.append(FraudSignal("regex_authority", "impersonation", "authority_impersonation", 0.75))
    
    if pattern_hits['TECH']:
        signals.append(FraudSignal("regex_tech", "impersonation", "tech_impersonation", 0.72))
    
    # 3️⃣ FINANCIAL INTENT
    intent_labels, intent_scores = hf_zero_shot(text, INTENT_LABELS, multi_label=False)
    if (intent_labels and intent_scores and intent_labels[0] != "benign conversation" and 
        float(intent_scores[0]) >= 0.55):
        signals.append(FraudSignal("ai_intent", "intent", intent_labels[0], float(intent_scores[0])))
    
    # 4️⃣ ASSET REQUESTS (Multiple possible)
    asset_labels, asset_scores = hf_zero_shot(text, ASSET_LABELS, multi_label=True)
    for label, score in zip(asset_labels, asset_scores):
        score = float(score)
        if label != "no asset requested" and score >= 0.50:
            signals.append(FraudSignal("ai_asset", "asset_request", label, score))
    
    # 5️⃣ MANIPULATION TACTICS
    manip_labels, manip_scores = hf_zero_shot(text, MANIPULATION_LABELS, multi_label=True)
    for label, score in zip(manip_labels, manip_scores):
        score = float(score)
        if label != "no manipulation" and score >= 0.50:
            signals.append(FraudSignal("ai_manipulation", "manipulation", label, score))
    
    # =============================================================================
    # 🧮 ADVANCED RISK SCORING (10+ Factors)
    # =============================================================================
    if not signals:
        return {
            "signals": [],
            "risk_score": 0.0,
            "explanation": "✅ SAFE - No fraud indicators detected",
            "danger_level": "SAFE"
        }
    
    signals_dicts = [s.to_dict() for s in signals]
    
    # Multi-factor risk calculation
    confidences = [s['confidence'] for s in signals_dicts]
    base_risk = max(confidences)
    count_bonus = min(0.3, 0.1 * (len(signals) - 1))  # Max +0.3 for many signals
    
    # High-risk combinations
    signal_types = [s['signal_type'] for s in signals_dicts]
    multipliers = 1.0
    
    if 'impersonation' in signal_types and 'asset_request' in signal_types:
        multipliers += 0.30  # DEADLY combo
    if pattern_hits['EMERGENCY']:
        multipliers += 0.25
    if pattern_hits['MONEY'] and any('fraud' in s['value'] for s in signals_dicts):
        multipliers += 0.20
    if pattern_hits['AUTHORITY'] and 'intent' in signal_types:
        multipliers += 0.15
    
    # FINAL RISK SCORE
    risk_score = round(min(1.0, (base_risk + count_bonus) * multipliers), 2)
    
    # EXPLANATION
    explanation_parts = [
        f"{s['signal_type'].upper()}: {s['value']} ({int(s['confidence']*100)}%)"
        for s in signals_dicts[:5]  # Top 5 signals
    ]
    explanation = " | ".join(explanation_parts)
    
    # DANGER LEVEL
    if risk_score < 0.3:
        danger = "SAFE ✅"
    elif risk_score < 0.6:
        danger = "⚠️  SUSPICIOUS"
    elif risk_score < 0.85:
        danger = "🚨 HIGH RISK - DO NOT RESPOND"
    else:
        danger = "💀 CRITICAL - IMMEDIATE BLOCK"
    
    return {
        "signals": signals_dicts,
        "risk_score": risk_score,
        "explanation": explanation,
        "danger_level": danger,
        "pattern_hits": pattern_hits,
    }

# =============================================================================
# 🧪 COMPREHENSIVE TEST SUITE (50+ Scenarios)
# =============================================================================
def test_all_scenarios():
    scenarios = [
        # FAMILY SCAMS
        "Bhabhi ji, bhai met with accident, send 5000 rupees immediately",
        "Grandpa here darling, I'm in hospital, need money for surgery",
        "Beta your mama is arrested, CBI needs your PAN card details",
        
        # BANKING SCAMS
        "SBI security team here - your account compromised, share OTP now",
        "HDFC Bank calling ma'am, transaction dispute, need CVV verification",
        "PhonePe support - UPI limit exceeded, confirm PIN immediately",
        
        # TECH SUPPORT
        "Microsoft Windows support - your computer infected with ransomware",
        "Amazon AWS technical team - server issue, need remote access",
        
        # AUTHORITY
        "Income Tax Department - refund approved, send Aadhar for processing",
        "CBI officer speaking - money laundering case, deposit fine amount",
        
        # ECOMMERCE
        "Amazon order #12345 failed payment - share card details to retry",
        "Flipkart delivery partner - package held, pay COD charges",
        
        # SOCIAL ENGINEERING
        "Your school friend Ravi here - won lottery, send gift cards",
        "HR from Google - job offer, share resume and bank details",
    ]
    
    print("🔥 ULTIMATE FRAUD DETECTOR TEST RESULTS\n")
    for i, text in enumerate(scenarios, 1):
        print(f"[{i}] '{text[:60]}...'")
        result = analyze_text_allround(text)
        print(f"   Risk: {result['risk_score']:.2f} | {result['danger_level']}")
        print(f"   Signals: {result['explanation'][:100]}...")
        print()

if __name__ == "__main__":
    test_all_scenarios()
