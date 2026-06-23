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

    prompt = f"""You are an advanced financial intelligence assistant. Your job is to analyze a transaction merchant or UPI ID, deduce the underlying business type, and map it semantically to the user's custom budget vaults.

Payment details:
{chr(10).join(merchant_info)}

Available vaults:
{vault_list}

Instructions for Deciphering & Mapping:
1. **Analyze the UPI Handle/Merchant Name:** Extract core brand names. Ignore banking suffixes (like @icici, @hdfc, @okaxis) unless the prefix itself is blank. 
2. **Deduce Business Domain:** Determine what the merchant sells (e.g., "Lenskart" -> Eyewear/Opticals; "Apollo" -> Pharmacy/Healthcare; "Croma" -> Electronics).
3. **Semantic Mapping to Custom Vaults:** Look at the user's available vaults. Users name things uniquely. Map the business domain to the *closest semantic concept*, even if the wording is unconventional (e.g., Healthcare maps perfectly to a vault named "Medicine", "Medical", or "Dieseas". Eyewear maps to "Shopping", "Glasses", or "Eye").
4. **Handle Ambiguity Intelligently:** 
   - If a merchant is dual-nature (e.g., "Apple" could be digital services, electronics, or groceries), look at the available vaults for clues. If the user only has a "Gadgets" vault, lean towards electronics. If they have both "Food" and "Tech", flag confidence as LOW but pick the most statistically likely one or offer both if they tie.
   - If the merchant name is completely generic or unrecognizable, mark confidence as LOW.

Examples of Semantic Mapping:
- Merchant: apollo@icici | Vaults: [Food, Savings, Dieseas] → Suggest: "Dieseas" (High confidence - Apollo is a known medical/pharmacy chain).
- Merchant: lenskart@oksbi | Vaults: [Rent, Eye, Investments] → Suggest: "Eye" (High confidence - Lenskart sells glasses/eyewear).
- Merchant: apple@hdfc | Vaults: [Groceries, Tech, Transport] → Suggest: "Tech" (Low confidence - Ambiguous brand, but "Tech" fits Apple Inc. products).
- Merchant: croma@icici | Vaults: [Food, Medical] → Suggest: NONE (Low confidence - Croma is electronics, no matching vault exists).

Reply in this exact format:
VAULTS: <vault name 1>, <vault name 2> (or NONE if no vault matches)
CATEGORY: <single category word>
REASON: <one short sentence explaining the semantic deduction>
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