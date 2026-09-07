"""
Recipe Service — Utility layer for pantry validation and flavor pairing.
Replaces the old generate_combined_recipe with challenge-specific helpers.
"""

from typing import List, Set, Tuple
from app_config import PANTRY_FLAT_LIST, CUISINE_PAIRING_MAP, FLAVOR_PAIRING_MODE_CONTRASTING
from src.utils.pantry_validator import validate_ingredients, normalize_ingredient
from src.utils.flavor_science import get_pairing_mode, build_flavor_prompt_instruction


def validate_against_pantry(
    ingredients: List[str],
    pantry_set: Set[str] | None = None,
) -> List[str]:
    """
    Return a list of hallucinated (invalid) ingredient names.
    
    Args:
        ingredients: Raw ingredient names to check.
        pantry_set: Optional custom pantry. Defaults to PANTRY_FLAT_LIST.

    Returns:
        List of ingredient names NOT found in the pantry.
    """
    if pantry_set is None:
        pantry_set = PANTRY_FLAT_LIST
    _, hallucinated = validate_ingredients(ingredients, pantry_set)
    return hallucinated


def determine_flavor_pairing_mode(cuisine: str) -> str:
    """
    Return the flavor pairing mode for a given cuisine.

    Args:
        cuisine: Cuisine name string.

    Returns:
        'uniform' or 'contrasting'
    """
    return get_pairing_mode(cuisine)


def parse_culinary_output(raw: dict) -> dict:
    """
    Validate and clean a raw CulinaryOutput dict.
    Ensures required keys are present and applies defaults.
    """
    required_keys = [
        "dish_name", "cuisine_type", "ingredients_used",
        "step_by_step_instructions", "timeline_plan",
    ]
    for key in required_keys:
        if key not in raw:
            raw[key] = [] if key.endswith("_plan") or key.endswith("_used") or key.endswith("_instructions") else ""
    return raw


def get_flavor_prompt(cuisine: str, ingredients: List[str]) -> str:
    """Convenience wrapper: get full flavor science prompt block."""
    mode = determine_flavor_pairing_mode(cuisine)
    return build_flavor_prompt_instruction(mode, ingredients)
