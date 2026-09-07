"""
Data models for the Code to Cuisine AI Culinary Engine.
Includes RecipeState (LangGraph workflow), HITL state fields,
and CulinaryOutput (master Pydantic output model).
"""

from typing import Dict, List, Any, TypedDict, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph Workflow State
# ─────────────────────────────────────────────────────────────────────────────

class RecipeState(TypedDict):
    """State object that flows through the 4-agent LangGraph workflow."""

    # ── User inputs (Step 1: Setup) ──
    ingredients: List[str]               # Selected pantry items
    available_appliances: List[str]
    dietary_restrictions: List[str]
    cuisine_preference: str
    skill_level: str

    # ── HITL: Checkpoint 1 — Pre-Ideation Chef Briefing (Step 2) ──
    chef_pre_notes: str                        # Free-text chef wisdom
    chef_pre_priority_ingredients: List[str]   # Ingredients to highlight
    chef_pre_techniques: List[str]             # Requested techniques
    chef_pre_context: str                      # Occasion / cultural context

    # ── Agent outputs ──
    flavor_pairing_mode: str               # "uniform" or "contrasting"
    flavor_rationale: str                  # Scientific justification
    dish_options: List[Dict[str, Any]]     # 3 AI-generated dish proposals
    validation_attempts: int               # Retry counter for constraint loop
    hallucinated_ingredients: List[str]    # Caught by validator
    timeline_plan: List[Dict[str, Any]]    # 90-min sequenced steps
    plating_guide: Dict[str, Any]          # Color, texture, presentation
    culinary_output: Dict[str, Any]        # Final CulinaryOutput dict

    # ── HITL: Checkpoint 2 — Post-Options Chef Selection (Step 4) ──
    selected_dish_index: int               # 0, 1, or 2
    chef_post_notes: str                   # Refinement free-text
    chef_post_removals: List[str]          # Ingredients to remove
    chef_post_swaps: Dict[str, str]        # {old: new} ingredient swaps

    # ── Chat interface ──
    chat_history: List[Dict[str, str]]
    thread_id: str

    # ── Legacy / compat fields ──
    appliance: str
    parsed_ingredients: List[Dict[str, Any]]
    recipe_suggestions: List[Dict[str, Any]]
    selected_recipe: Dict[str, Any]
    alternative_recipes: List[Dict[str, Any]]
    user_selected_alternative: Optional[str]
    nutrition_info: Dict[str, Any]
    shopping_list: List[str]
    cooking_tips: List[str]
    final_recipe: Dict[str, Any]
    online_search_results: List[Dict[str, Any]]
    search_enhanced: bool
    search_enhancement_complete: bool
    verification_result: Optional[Dict[str, Any]]

    # ── Metadata ──
    processing_step: str
    error_message: Optional[str]
    agent_log: List[str]                   # Visible reasoning log entries


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic Output Models
# ─────────────────────────────────────────────────────────────────────────────

class NutritionInfo(BaseModel):
    """Nutritional information per serving."""
    calories_per_serving: int = Field(description="Estimated calories per serving")
    protein_g: float = Field(description="Protein in grams")
    carbs_g: float = Field(description="Carbohydrates in grams")
    fat_g: float = Field(description="Fat in grams")
    fiber_g: float = Field(description="Fiber in grams")
    key_nutrients: List[str] = Field(description="Notable vitamins/minerals")
    health_benefits: List[str] = Field(description="Health benefits")


class TimelineStep(BaseModel):
    """A single step in the 90-minute kitchen execution plan."""
    time_start: str = Field(description="Start time e.g. '0:00'")
    time_end: str = Field(description="End time e.g. '0:15'")
    task: str = Field(description="Task description")
    responsible_appliance: str = Field(description="Appliance or station")
    parallel_with: Optional[str] = Field(default=None, description="Task running in parallel")
    notes: str = Field(description="Chef notes for this step")


class PlatingGuide(BaseModel):
    """Plating aesthetics and presentation guide."""
    primary_colors: List[str] = Field(description="Key visual colors on the plate")
    texture_contrast: str = Field(description="Texture interplay description")
    plating_sequence: List[str] = Field(description="Order of elements on the plate")
    garnish_suggestions: List[str] = Field(description="Garnish ideas")
    visual_description: str = Field(description="Overall visual impression")
    color_theory_note: str = Field(description="Complementary/analogous color rationale")


class DishOption(BaseModel):
    """One of the 3 AI-generated dish proposals presented at Checkpoint 2."""
    option_number: int = Field(description="1, 2, or 3")
    dish_name: str
    emoji: str = Field(description="Representative emoji")
    flavor_profile_summary: str = Field(description="3-sentence flavor description")
    key_techniques: List[str]
    innovation_highlight: str = Field(description="What makes this unique")
    difficulty: str = Field(description="Beginner / Intermediate / Advanced")
    primary_ingredients: List[str] = Field(description="Top 5 pantry items used")


class CulinaryOutput(BaseModel):
    """Master output model encompassing all required challenge artefacts."""

    # ── Dish Concept Document fields ──
    dish_name: str = Field(description="Final dish name")
    emoji: str = Field(description="Representative emoji")
    cuisine_type: str = Field(description="Cuisine classification")
    dish_concept_summary: str = Field(description="1-paragraph Dish Concept Doc intro")

    # ── Flavor Science ──
    flavor_pairing_mode: str = Field(description="'uniform' or 'contrasting'")
    flavor_rationale: str = Field(description="Computational gastronomy justification")
    flavor_profile: str = Field(description="Taste/aroma description")

    # ── Ingredients ──
    ingredients_used: List[str] = Field(description="Pantry items used (validated)")
    ingredient_quantities: List[str] = Field(description="With exact measurements e.g. '200g Red lentils'")

    # ── Techniques ──
    techniques: List[str] = Field(description="Cooking methods applied")
    key_techniques_explained: List[str] = Field(description="Technique + why it was chosen")

    # ── Step-by-step ──
    step_by_step_instructions: List[str] = Field(description="Numbered cooking steps")

    # ── Preparation Plan fields ──
    timeline_plan: List[TimelineStep] = Field(description="90-minute kitchen execution plan")

    # ── Plating ──
    plating_guide: PlatingGuide = Field(description="Plating aesthetics guide")

    # ── Nutrition ──
    nutrition_summary: NutritionInfo = Field(description="Estimated nutrition per serving")
    allergen_info: List[str] = Field(description="Allergens present")
    serving_suggestions: str = Field(description="Pairing / accompaniments")

    # ── Pitch & Story fields ──
    culinary_rationale: str = Field(description="Pitch narrative for judges")
    innovation_statement: str = Field(description="What makes this dish unique")
    chef_adaptation_notes: str = Field(description="How chef shaped the final dish")
    human_ai_collaboration_story: str = Field(description="Full HITL narrative for pitch deck")


# ─────────────────────────────────────────────────────────────────────────────
# Legacy model (kept for backward compat with old nodes)
# ─────────────────────────────────────────────────────────────────────────────

class FinalRecipe(BaseModel):
    """Legacy model — kept for backward compatibility."""
    name: str = Field(description="Recipe name")
    description: str = Field(description="Recipe description")
    ingredients: List[str] = Field(description="List of ingredients with quantities")
    instructions: List[str] = Field(description="Step-by-step instructions")
    prep_time: int = Field(description="Preparation time in minutes")
    cook_time: int = Field(description="Cooking time in minutes")
    total_time: int = Field(description="Total time in minutes")
    servings: int = Field(description="Number of servings")
    difficulty: str = Field(description="Difficulty level")
    cuisine_type: str = Field(description="Type of cuisine")
    appliance_used: str = Field(description="Primary appliance used")
    nutrition: NutritionInfo = Field(description="Nutritional information")
    tips: List[str] = Field(description="Cooking tips")
    variations: List[str] = Field(description="Recipe variations")
    storage_instructions: str = Field(description="How to store leftovers")
    emoji_representation: str = Field(description="Fun emoji representation")
