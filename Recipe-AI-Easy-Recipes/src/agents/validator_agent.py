"""
Constraint Validator Agent — Sous-Chef.
Validates that AI-generated options only use ingredients from the user's list.
"""

import json
from typing import Any, Dict

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app_config import LLM_PRECISE_TEMPERATURE, LLM_MODEL_NAME, WORKFLOW_MAX_VALIDATION_RETRIES
from src.utils.pantry_validator import validate_ingredients, format_hallucination_report


class ConstraintValidatorAgent:
    """Sous-Chef agent — validates ingredient adherence to the user's list."""

    def __init__(self, groq_api_key: str, model_name: str = LLM_MODEL_NAME):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=LLM_PRECISE_TEMPERATURE,
            api_key=groq_api_key,
            max_tokens=2000,
        )

    def _extract_all_ingredients(self, dish_options: list) -> list:
        """Extract all ingredient mentions from dish options."""
        ingredients = []
        for option in dish_options:
            ingredients.extend(option.get("primary_ingredients", []))
        return list(set(ingredients))

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that recipe ingredients stay within user's ingredient list."""
        dish_options = state.get("dish_options", [])
        user_ingredients = state.get("ingredients", [])
        validation_attempts = state.get("validation_attempts", 0)
        existing_log = state.get("agent_log", [])

        if not dish_options:
            return {
                **state,
                "processing_step": "validation_failed",
                "agent_log": existing_log + ["⚠️ Validator: No dish options to validate."],
                "hallucinated_ingredients": [],
                "validation_attempts": validation_attempts + 1,
            }

        all_ai_ingredients = self._extract_all_ingredients(dish_options)
        valid, hallucinated = validate_ingredients(all_ai_ingredients, user_ingredients)

        log_entry = (
            f"✅ **Constraint Validator** — Checked {len(all_ai_ingredients)} ingredient mentions. "
            f"Valid: {len(valid)}, Out-of-scope: {len(hallucinated)}."
        )

        if hallucinated and validation_attempts < WORKFLOW_MAX_VALIDATION_RETRIES:
            report = format_hallucination_report(hallucinated, user_ingredients)
            return {
                **state,
                "hallucinated_ingredients": hallucinated,
                "validation_attempts": validation_attempts + 1,
                "processing_step": "validation_failed",
                "agent_log": existing_log + [
                    log_entry,
                    f"🔄 Re-sending to Ideation (attempt {validation_attempts + 1}/{WORKFLOW_MAX_VALIDATION_RETRIES}): {report}"
                ],
            }

        # Max retries or all valid
        log_note = (
            f"⚠️ Proceeding with flags after {WORKFLOW_MAX_VALIDATION_RETRIES} retries. Out-of-scope: {', '.join(hallucinated)}"
            if hallucinated
            else "✅ All ingredients validated against user's list."
        )

        return {
            **state,
            "hallucinated_ingredients": hallucinated,
            "validation_attempts": validation_attempts + 1,
            "processing_step": "validation_passed",
            "agent_log": existing_log + [log_entry, log_note],
        }
