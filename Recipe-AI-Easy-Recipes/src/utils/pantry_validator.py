"""
Ingredient validator — validates AI-generated recipes against the user's
actual ingredient list (no fixed pantry).
"""

import re
from typing import List, Set, Tuple


def normalize_ingredient(name: str) -> str:
    """Normalize an ingredient name: lowercase, strip quantities."""
    name = name.lower().strip()
    # Remove leading quantities/units
    name = re.sub(r'^[\d\s./]+(g|kg|ml|l|tbsp|tsp|cup|cups|oz|lb|lbs|cloves?|pinch|handful)?\s*', '', name)
    # Remove trailing plural 's' for simple matching
    if len(name) > 4 and name.endswith('s') and not name.endswith('ss'):
        name = name[:-1]
    return name.strip()


def validate_ingredients(
    ai_ingredients: List[str],
    user_ingredients: List[str],
) -> Tuple[List[str], List[str]]:
    """
    Validate that AI-generated ingredient list only uses what the user provided.

    Args:
        ai_ingredients: Ingredients mentioned by the AI in the recipe.
        user_ingredients: Ingredients the user declared they have.

    Returns:
        (valid, hallucinated) — partitioned lists.
    """
    # Build normalized user set
    user_set: Set[str] = {normalize_ingredient(i) for i in user_ingredients}

    valid: List[str] = []
    hallucinated: List[str] = []

    for ing in ai_ingredients:
        normalized = normalize_ingredient(ing)

        # Direct match
        if normalized in user_set:
            valid.append(ing)
            continue

        # Bidirectional substring match for items >= 6 chars
        # (prevents short words like "oil" matching "olive oil" accidentally)
        matched = any(
            (normalized in u or u in normalized)
            for u in user_set
            if len(u) >= 6
        )

        if matched:
            valid.append(ing)
        else:
            hallucinated.append(ing)

    return valid, hallucinated


def format_hallucination_report(hallucinated: List[str], user_ingredients: List[str]) -> str:
    """Return a human-readable report of out-of-scope ingredients."""
    if not hallucinated:
        return "✅ All ingredients are within the user's available list."
    items = ", ".join(f"**{h}**" for h in hallucinated)
    return (
        f"⚠️ The following ingredient(s) were NOT in the user's provided list and MUST be removed: {items}. "
        f"Find substitutes from: {', '.join(user_ingredients[:10])}{'...' if len(user_ingredients) > 10 else ''}."
    )
