from groq import Groq
from backend.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def categorize_merchant(merchant_name: str, upi_id: str, vaults: list) -> dict:
    if not merchant_name and not upi_id:
        return {"suggested_vaults": [], "category": None, "reason": None}

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

Based on the merchant details, suggest the most appropriate vault(s) for this payment.
If multiple vaults could work, list up to 3 ranked by relevance.
Also suggest a category for this payment.

Reply in this exact format:
VAULTS: <vault name 1>, <vault name 2>, <vault name 3> (or NONE if no match)
CATEGORY: <single category word like food/rent/shopping/medical/travel/entertainment>
REASON: <one short sentence explaining why>
IS_VIOLATION: <YES or NO — yes if the payment clearly doesn't belong in any available vault>"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
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

            elif line.startswith("IS_VIOLATION:"):
                val = line.replace("IS_VIOLATION:", "").strip().upper()
                result["is_violation"] = val == "YES"

        return result

    except Exception as e:
        print(f"AI categorization error: {e}")
        return {"suggested_vaults": [], "category": None, "reason": None, "is_violation": False}