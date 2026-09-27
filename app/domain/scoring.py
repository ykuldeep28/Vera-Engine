from typing import Any, Dict, Optional

class ActionScorer:
    @staticmethod
    def score_candidate(
        candidate: Dict[str, Any],
        merchant_ctx: Optional[Dict[str, Any]],
        category_ctx: Optional[Dict[str, Any]],
        trigger_ctx: Dict[str, Any],
        customer_ctx: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate a composite quality score (0.0 to 1.0) for a candidate action.
        """
        score = 0.5  # Base score

        # 1. Trigger Urgency Weight (1-5 mapped to 0.0 - 0.2)
        urgency = trigger_ctx.get("urgency", 2)
        score += (urgency / 5.0) * 0.2

        # 2. Specificity / Facts check (0.0 to 0.2)
        params = candidate.get("template_params", [])
        has_numbers = any(any(c.isdigit() for c in str(p)) for p in params)
        if has_numbers:
            score += 0.2

        # 3. Merchant Fit & Personalization (0.0 to 0.2)
        if merchant_ctx:
            owner = merchant_ctx.get("identity", {}).get("owner_first_name")
            if owner and owner in candidate.get("body", ""):
                score += 0.1
            signals = merchant_ctx.get("signals", [])
            if len(signals) > 0:
                score += 0.1

        # 4. Customer Personalization (0.0 to 0.2)
        if customer_ctx:
            cust_name = customer_ctx.get("identity", {}).get("name")
            if cust_name and cust_name in candidate.get("body", ""):
                score += 0.2

        return min(1.0, round(score, 2))
