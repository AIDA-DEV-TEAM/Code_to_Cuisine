"""
Ideation Agent — Executive Chef.
Generates 4-5 distinct dish options using international cuisine-authentic
computational gastronomy, strictly constrained to the user's ingredient list.
"""

import json
from typing import Any, Dict

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app_config import LLM_IDEATION_TEMPERATURE, LLM_MODEL_NAME, NUM_DISH_OPTIONS, CHALLENGE_TIMELINE_MINUTES
from src.utils.flavor_science import get_pairing_mode, build_flavor_prompt_instruction


class IdeationAgent:
    """Executive Chef agent — generates creative, cuisine-authentic dish options."""

    def __init__(self, groq_api_key: str, model_name: str = LLM_MODEL_NAME):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=LLM_IDEATION_TEMPERATURE,
            api_key=groq_api_key,
            max_tokens=6000,
        )

    def _build_substitution_block(self, ingredients: list) -> str:
        """Build prompt instructions for substituting missing basics."""
        ing_lower = {i.lower() for i in ingredients}

        missing_basics = []
        has_salt = any("salt" in i for i in ing_lower)
        has_sugar = any("sugar" in i or "honey" in i or "jaggery" in i or "maple" in i or "molasses" in i for i in ing_lower)
        has_oil = any("oil" in i or "butter" in i or "ghee" in i or "fat" in i or "lard" in i for i in ing_lower)
        has_water = any("water" in i or "stock" in i or "broth" in i or "milk" in i for i in ing_lower)
        has_acid = any("lemon" in i or "lime" in i or "vinegar" in i or "tamarind" in i or "tomato" in i for i in ing_lower)

        blocks = []
        if not has_salt:
            blocks.append("⚠️ No salt present — use soy sauce, fish sauce, miso, or naturally salty ingredients for seasoning.")
        if not has_sugar:
            blocks.append("⚠️ No sugar/honey present — extract sweetness from ripe fruit (banana, mango, apple), root vegetables (carrot, sweet potato), or caramelised onion.")
        if not has_oil:
            blocks.append("⚠️ No oil/fat present — dry-roast, steam, or use moisture from vegetables; render fat from meat if available.")
        if not has_water:
            blocks.append("⚠️ No liquid present — extract moisture from vegetables (tomato, courgette) or use juice from fruits.")
        if not has_acid:
            blocks.append("⚠️ No acid present — use fermented ingredients, pickling-style preparation, or rely on natural fruit acidity.")

        if blocks:
            return (
                "\n## ⚠️ Missing Basics — Substitution Required\n"
                "The user does NOT have some common ingredients. You MUST innovate:\n"
                + "\n".join(blocks)
                + "\n\nFor EVERY dish option, explicitly note what substitutions are being made and why.\n"
            )
        return ""

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Ideation Agent and return updated state."""
        ingredients = state.get("ingredients", [])
        cuisine = state.get("cuisine_preference", "Italian")
        skill = state.get("skill_level", "Intermediate")
        dietary = state.get("dietary_restrictions", [])
        appliances = state.get("available_appliances", ["Stovetop / Gas hob"])

        # Flavor pairing
        pairing_mode = get_pairing_mode(cuisine)
        flavor_instruction = build_flavor_prompt_instruction(pairing_mode, cuisine, ingredients)

        # Substitution block for missing basics
        substitution_block = self._build_substitution_block(ingredients)

        # Chef Checkpoint 1 inputs
        chef_notes = state.get("chef_pre_notes", "").strip()
        priority_ings = state.get("chef_pre_priority_ingredients", [])
        techniques = state.get("chef_pre_techniques", [])
        chef_context = state.get("chef_pre_context", "")

        chef_guidance_block = ""
        if any([chef_notes, priority_ings, techniques, chef_context]):
            chef_guidance_block = "\n## Head Chef Guidance\n"
            if chef_context:
                chef_guidance_block += f"- **Occasion / Context**: {chef_context}\n"
            if priority_ings:
                chef_guidance_block += f"- **Priority Ingredients** (must feature prominently): {', '.join(priority_ings)}\n"
            if techniques:
                chef_guidance_block += f"- **Requested Techniques**: {', '.join(techniques)}\n"
            if chef_notes:
                chef_guidance_block += f"- **Chef's Personal Notes**: {chef_notes}\n"

        # Hallucination correction feedback
        hallucinated = state.get("hallucinated_ingredients", [])
        validation_attempts = state.get("validation_attempts", 0)
        correction_block = ""
        if hallucinated:
            correction_block = (
                f"\n## ⚠️ CORRECTION REQUIRED (Attempt {validation_attempts})\n"
                f"These ingredients were NOT in the user's list and MUST be removed: "
                f"{', '.join(hallucinated)}. Substitute with available ingredients only.\n"
            )

        system_prompt = f"""You are a world-class executive chef. Generate exactly {NUM_DISH_OPTIONS} distinct, creative dish options.

ABSOLUTE CONSTRAINTS — NEVER VIOLATE:
1. USE ONLY the exact ingredients the user has listed. ZERO additional ingredients.
2. If a typical basic (salt, oil, sugar, water) is NOT in the list, you MUST substitute it from available ingredients — do NOT assume it exists.
3. Each dish MUST be achievable within {CHALLENGE_TIMELINE_MINUTES} minutes total cook + prep time.
4. All {NUM_DISH_OPTIONS} options must be meaningfully different from each other.
5. The cuisine style is {cuisine} — every dish must taste authentically {cuisine}. Apply the correct techniques, flavour profile, and plating conventions of {cuisine} cuisine.
6. Respect all dietary restrictions strictly.

{flavor_instruction}
{substitution_block}
{chef_guidance_block}
{correction_block}

Return ONLY valid JSON:
{{
  "flavor_pairing_mode": "{pairing_mode}",
  "flavor_rationale": "<2-3 sentence scientific explanation citing specific flavor molecules>",
  "dish_options": [
    {{
      "option_number": 1,
      "dish_name": "<Authentic {cuisine}-style name>",
      "emoji": "<single emoji>",
      "flavor_profile_summary": "<3-sentence description of taste, aroma, and texture>",
      "key_techniques": ["<technique1>", "<technique2>"],
      "innovation_highlight": "<what is genuinely creative about this dish>",
      "difficulty": "<Beginner|Intermediate|Advanced>",
      "estimated_time_minutes": <number under {CHALLENGE_TIMELINE_MINUTES}>,
      "primary_ingredients": ["<exactly from user list>"],
      "substitutions_made": ["<e.g. banana used instead of sugar for sweetness>"]
    }}
  ]
}}"""

        user_prompt = f"""User's available ingredients: {', '.join(ingredients)}
Target cuisine: {cuisine}
Skill level: {skill}
Dietary restrictions: {', '.join(dietary) if dietary else 'None'}
Available appliances: {', '.join(appliances)}

Generate {NUM_DISH_OPTIONS} creative {cuisine} dish options using ONLY these exact ingredients."""

        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
            response = self.llm.invoke(messages)
            content = response.content
            if isinstance(content, list):
                content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
            content = content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip().rstrip("```").strip()

            result = json.loads(content)
            existing_log = state.get("agent_log", [])

            log_entry = (
                f"🧠 **Ideation Agent** — Generated {len(result.get('dish_options', []))} "
                f"{cuisine} dish options using **{pairing_mode.title()} flavor mode**. "
                f"Time limit: {CHALLENGE_TIMELINE_MINUTES} min."
            )

            return {
                **state,
                "flavor_pairing_mode": result.get("flavor_pairing_mode", pairing_mode),
                "flavor_rationale": result.get("flavor_rationale", ""),
                "dish_options": result.get("dish_options", []),
                "processing_step": "ideation_complete",
                "agent_log": existing_log + [log_entry],
                "error_message": "",
            }

        except Exception as e:
            existing_log = state.get("agent_log", [])
            return {
                **state,
                "processing_step": "ideation_error",
                "agent_log": existing_log + [f"❌ Ideation Agent error: {e}"],
                "error_message": str(e),
                "dish_options": [],
            }
