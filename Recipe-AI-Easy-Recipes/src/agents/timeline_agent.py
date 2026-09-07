"""
Timeline & Sequence Agent — Temporal Manager.
Generates a 90-minute parallel kitchen execution plan,
incorporating chef post-selection refinements from Checkpoint 2.
"""

import json
from typing import Any, Dict

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app_config import LLM_DEFAULT_TEMPERATURE, LLM_MODEL_NAME, CHALLENGE_TIMELINE_MINUTES


class TimelineSequenceAgent:
    """Temporal Manager agent — builds the 60-minute kitchen execution plan."""

    def __init__(self, groq_api_key: str, model_name: str = LLM_MODEL_NAME):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=LLM_DEFAULT_TEMPERATURE,
            api_key=groq_api_key,
            max_tokens=5000,
        )

    def _get_selected_option(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get the chef-selected dish option."""
        dish_options = state.get("dish_options", [])
        idx = state.get("selected_dish_index", 0)
        if dish_options and 0 <= idx < len(dish_options):
            return dish_options[idx]
        return dish_options[0] if dish_options else {}

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Timeline Agent and return updated state."""
        selected = self._get_selected_option(state)
        ingredients = state.get("ingredients", [])
        appliances = state.get("available_appliances", ["Stovetop"])
        skill = state.get("skill_level", "Intermediate")
        dietary = state.get("dietary_restrictions", [])

        # Incorporate Checkpoint 2 chef refinements
        chef_post_notes = state.get("chef_post_notes", "").strip()
        removals = state.get("chef_post_removals", [])
        swaps = state.get("chef_post_swaps", {})

        refinement_block = ""
        if any([chef_post_notes, removals, swaps]):
            refinement_block = "\n## Chef Refinements Applied\n"
            if removals:
                refinement_block += f"- **Remove these ingredients**: {', '.join(removals)}\n"
            if swaps:
                for old, new in swaps.items():
                    refinement_block += f"- **Swap**: {old} → {new}\n"
            if chef_post_notes:
                refinement_block += f"- **Chef's additional notes**: {chef_post_notes}\n"

        system_prompt = f"""You are a precision kitchen manager. Given a selected dish concept, create a strict {CHALLENGE_TIMELINE_MINUTES}-minute parallel kitchen execution plan.

RULES:
1. Total time must NOT exceed {CHALLENGE_TIMELINE_MINUTES} minutes.
2. Identify the critical path — long-cook items (lentils, rice, cassava, chickpeas) must START FIRST.
3. Use parallel tracks to maximize efficiency (e.g., sauce prep while base cooks).
4. Every step must specify which appliance/station handles it.
5. Respect the chef's refinements if provided.
{refinement_block}

Return ONLY valid JSON:
{{
  "dish_name": "<name>",
  "total_time_minutes": <number>,
  "timeline_plan": [
    {{
      "time_start": "0:00",
      "time_end": "0:15",
      "task": "<description>",
      "responsible_appliance": "<Stovetop|Oven|etc>",
      "parallel_with": "<task running simultaneously or null>",
      "notes": "<chef tip for this step>"
    }}
  ],
  "step_by_step_instructions": [
    "<step 1>",
    "<step 2>"
  ],
  "ingredient_quantities": [
    "<200g Red lentils>",
    "<2 tbsp Ghee>"
  ],
  "techniques_applied": ["<technique1>", "<technique2>"]
}}"""

        user_prompt = f"""Selected dish: {selected.get('dish_name', 'Unknown')} {selected.get('emoji', '')}
Primary ingredients: {', '.join(selected.get('primary_ingredients', ingredients[:8]))}
Techniques: {', '.join(selected.get('key_techniques', []))}
Available appliances: {', '.join(appliances)}
Skill level: {skill}
Dietary: {', '.join(dietary) if dietary else 'None'}

Innovation: {selected.get('innovation_highlight', '')}

Generate the complete 90-minute kitchen execution plan."""

        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
            response = self.llm.invoke(messages)
            content = response.content.strip()

            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            content = content.strip().rstrip("```").strip()

            result = json.loads(content)
            existing_log = state.get("agent_log", [])

            log_entry = (
                f"⏱️ **Timeline Agent** — Built {len(result.get('timeline_plan', []))} "
                f"parallel steps for a {result.get('total_time_minutes', '?')}-minute execution plan."
            )

            return {
                **state,
                "timeline_plan": result.get("timeline_plan", []),
                "final_recipe": {
                    "dish_name": result.get("dish_name", selected.get("dish_name", "")),
                    "step_by_step_instructions": result.get("step_by_step_instructions", []),
                    "ingredient_quantities": result.get("ingredient_quantities", []),
                    "techniques_applied": result.get("techniques_applied", []),
                    "total_time_minutes": result.get("total_time_minutes", CHALLENGE_TIMELINE_MINUTES),
                },
                "processing_step": "timeline_complete",
                "agent_log": existing_log + [log_entry],
                "error_message": "",
            }

        except Exception as e:
            existing_log = state.get("agent_log", [])
            return {
                **state,
                "processing_step": "timeline_error",
                "agent_log": existing_log + [f"❌ Timeline Agent error: {e}"],
                "error_message": str(e),
                "timeline_plan": [],
            }
