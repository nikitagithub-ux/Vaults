from groq import Groq
from backend.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

def categorize_merchant(merchant_name: str, upi_id: str, vaults: list) -> dict:
    if not merchant_name and not upi_id:
        return {"suggested_vault": None, "category": None, "confidence": "low"}

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

    prompt = f"""You are a financial assistant helping categorize a payment into the correct budget vault.

Payment details:
{chr(10).join(merchant_info)}

Available vaults:
{vault_list}

Based on the merchant details, which vault is most appropriate for this payment?
Also suggest a category for this payment (like food, rent, shopping, medical, travel, entertainment, utilities etc).

Reply in this exact format:
VAULT: <vault name or NONE if no match>
CATEGORY: <category word>
REASON: <one short sentence>"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.1
        )

        text = response.choices[0].message.content.strip()
        print(f"AI RESPONSE: {text}")
        lines = text.split('\n')

        result = {
            "suggested_vault": None,
            "category": None,
            "reason": None,
            "confidence": "high"
        }

        vault_names = [v.name for v in vaults if v.name != "Penalty Pool"]

        for line in lines:
            if line.startswith("VAULT:"):
                vault_name = line.replace("VAULT:", "").strip()
                if vault_name != "NONE":
                    matched = next(
                        (v for v in vault_names if v.lower() == vault_name.lower()),
                        None
                    )
                    result["suggested_vault"] = matched or vault_name
            elif line.startswith("CATEGORY:"):
                result["category"] = line.replace("CATEGORY:", "").strip().lower()
            elif line.startswith("REASON:"):
                result["reason"] = line.replace("REASON:", "").strip()

        return result

    except Exception as e:
        print(f"AI categorization error: {e}")
        return {"suggested_vault": None, "category": None, "confidence": "low"}