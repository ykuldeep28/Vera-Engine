import re
from typing import Any, Dict, List, Optional

CATEGORY_DEFAULTS = {
    "dentists": {
        "salutation": "Dr. {first_name}",
        "register": "peer_clinical",
        "taboos": ["guaranteed", "100% safe", "completely cure", "miracle", "best in city"]
    },
    "gyms": {
        "salutation": "{first_name}",
        "register": "coach_to_member",
        "taboos": ["guaranteed weight loss", "shred in 7 days", "miracle transformation"]
    },
    "pharmacies": {
        "salutation": "{first_name}",
        "register": "neighbourhood_pharmacist",
        "taboos": ["miracle cure", "guaranteed result", "100% safe"]
    },
    "restaurants": {
        "salutation": "{first_name}",
        "register": "fellow_operator",
        "taboos": ["best food in city", "guaranteed packed house", "miracle marketing"]
    },
    "salons": {
        "salutation": "{first_name}",
        "register": "approachable_expert",
        "taboos": ["guaranteed glow", "permanent results", "instant transformation"]
    }
}

def clean_urls_and_taboos(text: str, category_slug: Optional[str] = None) -> str:
    """Strip any URLs or taboo hype phrases to protect quality score."""
    # 1. Remove URLs (strict rule from testing brief - penalty -3 per URL)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'www\.\S+', '', text)
    
    # 2. Taboo phrase filter
    taboos = []
    if category_slug and category_slug in CATEGORY_DEFAULTS:
        taboos = CATEGORY_DEFAULTS[category_slug]["taboos"]
    
    for taboo in taboos:
        pattern = re.compile(re.escape(taboo), re.IGNORECASE)
        text = pattern.sub('', text)

    # Clean double spaces
    text = re.sub(r' +', ' ', text).strip()
    return text
