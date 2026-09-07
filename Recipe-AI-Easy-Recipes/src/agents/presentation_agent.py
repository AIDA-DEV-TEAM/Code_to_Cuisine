"""
Presentation Agent — Culinary Storyteller.
Generates plating guide, pitch narrative, AI dish image, and CulinaryOutput.
Uses Tavily for web-sourced plating ideas (optional) and Pollinations.ai for
free AI image generation.
"""

import json
import urllib.parse
from typing import Any, Dict, List, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from app_config import LLM_CREATIVE_TEMPERATURE, LLM_MODEL_NAME, CHALLENGE_TIMELINE_MINUTES


class PresentationAgent:
    """Presentation agent — plating, pitch, AI image, and CulinaryOutput compilation."""

    def __init__(self, groq_api_key: str, model_name: str = LLM_MODEL_NAME, tavily_api_key: Optional[str] = None):
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=LLM_CREATIVE_TEMPERATURE,
            api_key=groq_api_key,
            max_tokens=6000,
        )
        self.tavily_api_key = tavily_api_key

    def _get_selected_option(self, state: Dict[str, Any]) -> Dict[str, Any]:
        dish_options = state.get("dish_options", [])
        idx = state.get("selected_dish_index", 0)
        if dish_options and 0 <= idx < len(dish_options):
            return dish_options[idx]
        return dish_options[0] if dish_options else {}

    def _search_plating_ideas(self, dish_name: str, cuisine: str) -> List[str]:
        """Search Tavily for top-rated plating references. Falls back to empty list."""
        if not self.tavily_api_key:
            return []
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_api_key)
            query = f"professional restaurant plating presentation {cuisine} {dish_name} fine dining"
            results = client.search(query=query, max_results=5)
            urls = [r.get("url", "") for r in results.get("results", []) if r.get("url")]
            return urls[:4]
        except Exception:
            return []

    def _generate_dish_image_url(self, dish_name: str, cuisine: str, plating_desc: str) -> str:
        """Generate an AI dish image URL using Pollinations.ai (free, no key needed)."""
        prompt = (
            f"Professional food photography, {cuisine} cuisine, dish: {dish_name}. "
            f"{plating_desc} "
            "Shot from above at 45-degree angle, soft natural light, white ceramic plate, "
            "Michelin-star restaurant plating, shallow depth of field, vibrant colors, "
            "ultra-realistic food photography, 4K, magazine quality."
        )
        encoded = urllib.parse.quote(prompt)
        return f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=600&nologo=true"

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the Presentation Agent and return updated state with CulinaryOutput."""
        selected = self._get_selected_option(state)
        final_recipe = state.get("final_recipe", {})
        cuisine = state.get("cuisine_preference", "International")
        flavor_mode = state.get("flavor_pairing_mode", "contrasting")
        flavor_rationale = state.get("flavor_rationale", "")
        ingredients = state.get("ingredients", [])

        # Chef notes
        chef_pre_notes = state.get("chef_pre_notes", "")
        chef_pre_context = state.get("chef_pre_context", "")
        chef_post_notes = state.get("chef_post_notes", "")
        chef_removals = state.get("chef_post_removals", [])
        chef_swaps = state.get("chef_post_swaps", {})

        chef_story = ""
        if chef_pre_notes or chef_post_notes or chef_pre_context:
            parts = []
            if chef_pre_context:
                parts.append(f"designed for {chef_pre_context}")
            if chef_pre_notes:
                parts.append(f"guided by the chef's insight: '{chef_pre_notes}'")
            if chef_post_notes or chef_removals or chef_swaps:
                parts.append("refined through direct chef intervention")
            chef_story = "This dish was " + "; ".join(parts) + "."

        dish_name = selected.get("dish_name", "the dish")
        substitutions = selected.get("substitutions_made", [])
        substitution_note = ""
        if substitutions:
            substitution_note = f"\nIngredient substitutions applied: {'; '.join(substitutions)}"

        # Web search for plating references
        plating_refs = self._search_plating_ideas(dish_name, cuisine)

        system_prompt = f"""You are a culinary storyteller, plating expert, and food scientist specialising in {cuisine} cuisine.

Given a dish concept and execution plan, generate a comprehensive presentation package.

The dish is authentic {cuisine} cuisine — reflect all plating conventions, color palettes, garnish traditions, and presentation standards of {cuisine} restaurants.

Return ONLY valid JSON:
{{
  "dish_concept_summary": "<1-paragraph Dish Concept Document intro — explain the dish's {cuisine} culinary story>",
  "flavor_profile": "<rich sensory description — taste, aroma, texture, mouthfeel>",
  "plating_guide": {{
    "primary_colors": ["<visual color present on plate>"],
    "texture_contrast": "<describe crispy vs soft vs creamy vs crunchy contrasts>",
    "plating_sequence": ["<1. lay base component>", "<2. position protein/main>", "<3. add sauce>", "<4. garnish>"],
    "garnish_suggestions": ["<authentic {cuisine} garnish>"],
    "visual_description": "<a vivid paragraph describing exactly what a diner sees when the plate arrives>",
    "color_theory_note": "<complementary/analogous color rationale specific to {cuisine} aesthetics>",
    "plate_type_recommendation": "<e.g. wide shallow white bowl, dark slate, banana leaf, wooden board>"
  }},
  "nutrition_summary": {{
    "calories_per_serving": <number>,
    "protein_g": <number>,
    "carbs_g": <number>,
    "fat_g": <number>,
    "fiber_g": <number>,
    "key_nutrients": ["<vitamin/mineral>"],
    "health_benefits": ["<benefit>"]
  }},
  "allergen_info": ["<allergen>"],
  "serving_suggestions": "<culturally authentic accompaniments and pairings for {cuisine}>",
  "culinary_rationale": "<2-3 paragraph pitch for judges — WHY this dish, the flavor science, what makes it memorable in context of {cuisine}>",
  "innovation_statement": "<1 crisp sentence: the genuinely novel idea>",
  "chef_adaptation_notes": "<how chef input shaped the result>",
  "human_ai_collaboration_story": "<compelling 2-paragraph story of how human expertise and AI reasoning created this dish — for a 5-min pitch>"
}}"""

        user_prompt = f"""Dish: {dish_name} {selected.get('emoji', '')}
Cuisine: {cuisine} — ensure authentic {cuisine} plating and presentation conventions
Flavor pairing mode: {flavor_mode}
Flavor rationale: {flavor_rationale}
Innovation: {selected.get('innovation_highlight', '')}
Techniques: {', '.join(selected.get('key_techniques', []))}
Ingredients: {', '.join(selected.get('primary_ingredients', ingredients[:10]))}
Chef context: {chef_story if chef_story else 'Pure AI-driven creation'}
Cook time: {final_recipe.get('total_time_minutes', CHALLENGE_TIMELINE_MINUTES)} minutes{substitution_note}

Generate the complete Presentation output."""

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

            presentation = json.loads(content)
            existing_log = state.get("agent_log", [])

            # Generate AI dish image
            plating_desc = presentation.get("plating_guide", {}).get("visual_description", "")
            image_url = self._generate_dish_image_url(dish_name, cuisine, plating_desc)

            # Compile master CulinaryOutput
            culinary_output = {
                "dish_name": dish_name,
                "emoji": selected.get("emoji", "🍽️"),
                "cuisine_type": cuisine,
                "dish_concept_summary": presentation.get("dish_concept_summary", ""),
                "flavor_pairing_mode": flavor_mode,
                "flavor_rationale": flavor_rationale,
                "flavor_profile": presentation.get("flavor_profile", ""),
                "ingredients_used": selected.get("primary_ingredients", ingredients),
                "ingredient_quantities": final_recipe.get("ingredient_quantities", []),
                "substitutions_made": substitutions,
                "techniques": selected.get("key_techniques", []),
                "key_techniques_explained": final_recipe.get("techniques_applied", []),
                "step_by_step_instructions": final_recipe.get("step_by_step_instructions", []),
                "timeline_plan": state.get("timeline_plan", []),
                "plating_guide": presentation.get("plating_guide", {}),
                "plating_image_url": image_url,
                "plating_web_references": plating_refs,
                "nutrition_summary": presentation.get("nutrition_summary", {}),
                "allergen_info": presentation.get("allergen_info", []),
                "serving_suggestions": presentation.get("serving_suggestions", ""),
                "culinary_rationale": presentation.get("culinary_rationale", ""),
                "innovation_statement": presentation.get("innovation_statement", ""),
                "chef_adaptation_notes": presentation.get("chef_adaptation_notes", ""),
                "human_ai_collaboration_story": presentation.get("human_ai_collaboration_story", ""),
            }

            img_note = " + AI plating image generated." if image_url else ""
            web_note = f" + {len(plating_refs)} plating references found." if plating_refs else ""
            log_entry = (
                f"🎨 **Presentation Agent** — Compiled CulinaryOutput with plating guide, "
                f"pitch narrative{img_note}{web_note}"
            )

            return {
                **state,
                "culinary_output": culinary_output,
                "plating_guide": presentation.get("plating_guide", {}),
                "processing_step": "presentation_complete",
                "agent_log": existing_log + [log_entry],
                "error_message": "",
            }

        except Exception as e:
            existing_log = state.get("agent_log", [])
            return {
                **state,
                "processing_step": "presentation_error",
                "agent_log": existing_log + [f"❌ Presentation Agent error: {e}"],
                "error_message": str(e),
                "culinary_output": {},
            }
