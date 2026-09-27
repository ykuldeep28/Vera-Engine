from typing import Any, Dict, List
from app.store.context_store import ContextStore
from app.store.suppression_store import SuppressionStore
from app.store.conversation_store import ConversationStore
from app.domain.suppression_rules import SuppressionGate
from app.domain.scoring import ActionScorer
from app.engine.composer import MessageComposer

class DecisionEngine:
    @staticmethod
    def process_tick(available_triggers: List[str]) -> List[Dict[str, Any]]:
        actions = []
        for trg_id in available_triggers:
            # 1. Fetch trigger context
            trigger_ctx = ContextStore.get_context("trigger", trg_id)
            if not trigger_ctx:
                continue

            merchant_id = trigger_ctx.get("merchant_id")
            customer_id = trigger_ctx.get("customer_id")
            suppression_key = trigger_ctx.get("suppression_key", f"{trg_id}:{merchant_id}")

            # 2. Fetch merchant context
            merchant_ctx = ContextStore.get_context("merchant", merchant_id) if merchant_id else None
            category_slug = merchant_ctx.get("category_slug") if merchant_ctx else None

            # 3. Fetch category context
            category_ctx = ContextStore.get_context("category", category_slug) if category_slug else None

            # 4. Fetch customer context if present
            customer_ctx = ContextStore.get_context("customer", customer_id) if customer_id else None

            # 5. Check Suppression Gate
            is_suppressed, reason = SuppressionGate.check_suppression(
                suppression_key=suppression_key,
                merchant_id=merchant_id or "m_unknown",
                customer_ctx=customer_ctx
            )
            if is_suppressed:
                continue

            # 6. Compose Action
            action_item = MessageComposer.compose_action(
                trigger_ctx=trigger_ctx,
                merchant_ctx=merchant_ctx,
                category_ctx=category_ctx,
                customer_ctx=customer_ctx
            )
            if not action_item:
                continue

            # 7. Score Action Candidate
            quality_score = ActionScorer.score_candidate(
                candidate=action_item,
                merchant_ctx=merchant_ctx,
                category_ctx=category_ctx,
                trigger_ctx=trigger_ctx,
                customer_ctx=customer_ctx
            )
            if quality_score < 0.4:
                # Score floor filter: drop low quality candidates
                continue

            # 8. Record Send in Suppression & Conversation Store
            SuppressionStore.record_send(
                suppression_key=suppression_key,
                merchant_id=merchant_id or "m_unknown",
                trigger_type=trigger_ctx.get("kind", "trigger")
            )

            ConversationStore.create_or_update_conversation(
                conversation_id=action_item["conversation_id"],
                merchant_id=merchant_id or "m_unknown",
                customer_id=customer_id,
                suppression_key=suppression_key,
                state="proposed",
                last_action_type=trigger_ctx.get("kind")
            )
            ConversationStore.add_message(
                conversation_id=action_item["conversation_id"],
                direction="out",
                text=action_item["body"]
            )

            actions.append(action_item)

        return actions
