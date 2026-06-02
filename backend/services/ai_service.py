from groq import Groq
from backend.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def categorize_merchant(merchant_name: str, upi_id: str, vaults: list) -> dict:
    if not merchant_name and not upi_id:
        return {
            "suggested_vaults": [],
            "category": None,
            "reason": None,
            "confidence": "low",
            "suggestion": None,
            "is_violation": False
        }

    vault_list = "\n".join([
        f"- {v.name} (description: {v.description or 'no description'})"
        for v in vaults
        if v.name != "Penalty Pool"
    ])

    merchant_info = []
    if merchant_name:
        merchant_info.append(f"Merchant name: {merchant_name}")
    if upi_id:
        merchant_info.append(f"UPI ID: {upi_id}")

    prompt = f"""You are a financial assistant helping categorize a payment into budget vaults.

Payment details:
{chr(10).join(merchant_info)}

Available vaults:
{vault_list}

Instructions:
- Look at the merchant and decide what TYPE of purchase this is
- Then check if any vault ACTUALLY matches that purchase type
- If no vault matches, say NONE and explain what type of vault would be appropriate
- Only suggest a vault if it genuinely matches — don't force a match
- Mark confidence LOW if the merchant name is ambiguous or unclear

Examples:
- "Dominos Pizza" with Food vault → suggest Food, HIGH confidence
- "Croma Electronics" with only Food/Medical vaults → NONE, LOW confidence, suggest creating Electronics vault
- "apollo@hdfc" with Medical vault → suggest Medical, HIGH confidence
- "apple@icici" → LOW confidence, ambiguous

Reply in this exact format:
VAULTS: <vault name 1>, <vault name 2> (or NONE if no vault matches)
CATEGORY: <single category word>
REASON: <one short sentence>
CONFIDENCE: <HIGH or LOW>
SUGGESTION: <if NONE, suggest what type of vault to create, otherwise leave blank>"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.1
        )

        text = response.choices[0].message.content.strip()
        print(f"AI RESPONSE: {text}")
        lines = text.split('\n')

        vault_names = [v.name for v in vaults if v.name != "Penalty Pool"]

        result = {
            "suggested_vaults": [],
            "category": None,
            "reason": None,
            "confidence": "high",
            "suggestion": None,
            "is_violation": False
        }

        for line in lines:
            if line.startswith("VAULTS:"):
                raw = line.replace("VAULTS:", "").strip()
                if raw != "NONE":
                    suggestions = [s.strip() for s in raw.split(',')]
                    for suggestion in suggestions:
                        matched = next(
                            (v for v in vault_names
                             if v.lower() == suggestion.lower()),
                            None
                        )
                        if matched and matched not in result["suggested_vaults"]:
                            result["suggested_vaults"].append(matched)

            elif line.startswith("CATEGORY:"):
                result["category"] = line.replace("CATEGORY:", "").strip().lower()

            elif line.startswith("REASON:"):
                result["reason"] = line.replace("REASON:", "").strip()

            elif line.startswith("CONFIDENCE:"):
                val = line.replace("CONFIDENCE:", "").strip().upper()
                result["confidence"] = val

            elif line.startswith("IS_VIOLATION:"):
                val = line.replace("IS_VIOLATION:", "").strip().upper()
                result["is_violation"] = val == "YES"

            elif line.startswith("SUGGESTION:"):
                val = line.replace("SUGGESTION:", "").strip()
                if val:
                    result["suggestion"] = val

        return result

    except Exception as e:
        print(f"AI categorization error: {e}")
        return {
            "suggested_vaults": [],
            "category": None,
            "reason": None,
            "confidence": "low",
            "suggestion": None,
            "is_violation": False
        }