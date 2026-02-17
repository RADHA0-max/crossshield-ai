import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HF_API_TOKEN")

headers = {
    "Authorization": f"Bearer {token}"
}

url = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"



payload = {

    "inputs": "This message claims to be from a bank and asks for urgent verification.",
    "parameters": {
        "candidate_labels": [
            "bank impersonation",
            "credential theft",
            "urgent manipulation",
            "benign message"
        ]
    }
}



response = requests.post(url, headers=headers, json=payload)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text[:300])
