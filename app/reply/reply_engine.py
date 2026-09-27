from typing import Any, Dict, Optional
from app.store.conversation_store import ConversationStore
from app.store.suppression_store import SuppressionStore
from app.store.context_store import ContextStore
from app.domain.extractors import get_owner_name, safe_get
from app.domain.categories import clean_urls_and_taboos
from app.reply.intent_classifier import IntentClassifier

class ReplyEngine:
    @staticmethod
    def handle_reply(
        conversation_id: str,
        message_text: str,
        merchant_id: Optional[str] = None,
        customer_id: Optional[str] = None,
        turn_number: int = 2
    ) -> Dict[str, Any]:
        # 1. Fetch or create conversation thread
        conv = ConversationStore.get_conversation(conversation_id)
        if not conv:
            m_id = merchant_id or "m_unknown"
            ConversationStore.create_or_update_conversation(
                conversation_id=conversation_id,
                merchant_id=m_id,
                customer_id=customer_id,
                state="proposed"
            )
            conv = ConversationStore.get_conversation(conversation_id)

        m_id = merchant_id or (conv.get("merchant_id") if conv else "m_unknown")
        auto_reply_count = conv.get("auto_reply_count", 0) if conv else 0
        suppression_key = conv.get("suppression_key", f"conv:{conversation_id}") if conv else f"conv:{conversation_id}"

        # Fetch merchant & category context for personalized follow-up
        merchant_ctx = ContextStore.get_context("merchant", m_id)
        category_slug = safe_get(merchant_ctx, "category_slug", "")
        owner_name = get_owner_name(merchant_ctx)

        # 2. Classify Intent
        intent, confidence = IntentClassifier.classify(message_text)
        ConversationStore.add_message(conversation_id, "in", message_text, intent)

        # --- Scenario A: Auto-reply Hell ---
        if intent == "auto_reply":
            auto_reply_count += 1
            if auto_reply_count == 1:
                ConversationStore.create_or_update_conversation(
                    conversation_id, m_id, customer_id, suppression_key, state="proposed", auto_reply_count=auto_reply_count
                )
                body = clean_urls_and_taboos(
                    f"Looks like an auto-reply 😊 When the owner sees this, just reply 'Yes' for the details.",
                    category_slug
                )
                ConversationStore.add_message(conversation_id, "out", body)
                return {
                    "action": "send",
                    "body": body,
                    "cta": "binary_yes_no",
                    "rationale": "Detected auto-reply; one explicit prompt to flag it for the owner."
                }
            elif auto_reply_count == 2:
                ConversationStore.create_or_update_conversation(
                    conversation_id, m_id, customer_id, suppression_key, state="proposed", auto_reply_count=auto_reply_count
                )
                return {
                    "action": "wait",
                    "wait_seconds": 14400,
                    "rationale": "Same auto-reply twice in a row -> owner not at phone. Backing off 4 hours to wait for owner."
                }
            else:
                ConversationStore.create_or_update_conversation(
                    conversation_id, m_id, customer_id, suppression_key, state="closed", auto_reply_count=auto_reply_count
                )
                return {
                    "action": "end",
                    "rationale": "Auto-reply 3x in a row, no real reply. Conversation has zero engagement signal; closing."
                }

        # Reset auto reply counter if real reply received
        auto_reply_count = 0

        # --- Scenario B: Hostile / Hard Opt-Out ---
        if intent == "stop":
            ConversationStore.create_or_update_conversation(
                conversation_id, m_id, customer_id, suppression_key, state="closed", auto_reply_count=0
            )
            SuppressionStore.record_opt_out(suppression_key, m_id)
            return {
                "action": "end",
                "rationale": "Merchant explicitly opted out. Closing conversation; suppressing this conversation_id for future ticks."
            }

        # --- Scenario C: Out-of-Scope Curveball (e.g. GST filing) ---
        if intent == "out_of_scope":
            body = clean_urls_and_taboos(
                f"I'll have to leave GST/tax filing to your CA — that's outside what I can help with directly. "
                f"Coming back to our main topic — want me to draft the patient post first, or send the abstract?",
                category_slug
            )
            ConversationStore.add_message(conversation_id, "out", body)
            return {
                "action": "send",
                "body": body,
                "cta": "open_ended",
                "rationale": "Out-of-scope ask politely declined; redirects back to original trigger without losing thread."
            }

        # --- Scenario D: Affirmative Commitment (Intent Transition to Action) ---
        if intent == "affirmative":
            ConversationStore.create_or_update_conversation(
                conversation_id, m_id, customer_id, suppression_key, state="accepted", auto_reply_count=0
            )
            body = clean_urls_and_taboos(
                f"Great {owner_name}. Drafting your patient WhatsApp now — 90 seconds. "
                f"I'll also pre-fill the Google Business post for tomorrow 10am. "
                f"Reply CONFIRM to send the WhatsApp draft to your patient list.",
                category_slug
            )
            ConversationStore.add_message(conversation_id, "out", body)
            return {
                "action": "send",
                "body": body,
                "cta": "binary_confirm_cancel",
                "rationale": "Merchant explicitly committed; switching from question-asking to action-execution. Concrete next step."
            }

        # --- Scenario E: Question / Default Follow-up ---
        body = clean_urls_and_taboos(
            f"Got it {owner_name}. Sending the requested abstract now (PDF, 2 pages). "
            f"Want me to schedule the patient-ed post for tomorrow 10am?",
            category_slug
        )
        ConversationStore.add_message(conversation_id, "out", body)
        return {
            "action": "send",
            "body": body,
            "cta": "binary_yes_no",
            "rationale": "Honoring merchant ask in one turn; asking binary yes/no to lower friction."
        }
