from typing import Any, Dict, Optional, Tuple
from app.store.suppression_store import SuppressionStore

class SuppressionGate:
    @staticmethod
    def check_suppression(
        suppression_key: str,
        merchant_id: str,
        customer_ctx: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Returns (is_suppressed: bool, reason: str | None)
        """
        # 1. Consent check for customer-scoped sends
        if customer_ctx:
            prefs = customer_ctx.get("preferences", {})
            opt_in = prefs.get("reminder_opt_in", True)
            if opt_in is False:
                return True, "customer_opted_out"
            
            consent_scope = customer_ctx.get("consent", {}).get("scope", [])
            # If explicit opt-in scope exists and is empty
            if isinstance(consent_scope, list) and len(consent_scope) == 0 and customer_ctx.get("consent", {}).get("opted_in_at") is None:
                return True, "no_customer_consent"

        # 2. Key suppression log lookup
        if not suppression_key:
            return False, None

        entry = SuppressionStore.get_suppression_entry(suppression_key)
        if not entry:
            return False, None

        # Hard opt-out flag
        if entry.get("opted_out") == 1:
            return True, "hard_opt_out"

        # Repeated decline threshold
        if entry.get("decline_count", 0) >= 2:
            return True, "prior_declines_threshold"

        # Recent send check
        if entry.get("last_sent_at"):
            return True, "suppressed_recent_send"

        return False, None
