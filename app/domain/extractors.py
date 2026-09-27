from typing import Any, Dict, List, Optional

def safe_get(data: Optional[Dict[str, Any]], key_path: str, default: Any = None) -> Any:
    """Safely extract nested keys from a dict (e.g. 'identity.owner_first_name')."""
    if not data or not isinstance(data, dict):
        return default
    keys = key_path.split(".")
    curr = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return default
    return curr

def get_merchant_name(merchant_ctx: Optional[Dict[str, Any]]) -> str:
    return safe_get(merchant_ctx, "identity.name", "the business")

def get_owner_name(merchant_ctx: Optional[Dict[str, Any]]) -> str:
    owner = safe_get(merchant_ctx, "identity.owner_first_name")
    if owner and owner.strip():
        return owner.strip()
    # Fallback to business name or generic
    biz_name = get_merchant_name(merchant_ctx)
    if "Dr." in biz_name or "Doctor" in biz_name:
        parts = biz_name.split()
        for p in parts:
            if p.startswith("Dr.") or p.startswith("Dr"):
                return p
    return "there"

def get_active_offers(merchant_ctx: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    offers = safe_get(merchant_ctx, "offers", [])
    if isinstance(offers, list):
        return [o for o in offers if isinstance(o, dict) and o.get("status") == "active"]
    return []

def get_digest_item(category_ctx: Optional[Dict[str, Any]], item_id: str) -> Optional[Dict[str, Any]]:
    digest = safe_get(category_ctx, "digest", [])
    if isinstance(digest, list):
        for item in digest:
            if isinstance(item, dict) and item.get("id") == item_id:
                return item
    return None
