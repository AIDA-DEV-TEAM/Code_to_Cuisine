"""
Flavor science helpers for international computational gastronomy.
Determines pairing philosophy and builds cuisine-authentic prompt instructions.
"""

from typing import List
from app_config import CUISINE_PAIRING_MAP, CUISINE_FLAVOR_IDENTITY


def get_pairing_mode(cuisine: str) -> str:
    """Return 'uniform' or 'contrasting' based on the cuisine."""
    return CUISINE_PAIRING_MAP.get(cuisine, "contrasting")


def get_flavor_identity(cuisine: str) -> str:
    """Return the cuisine's characteristic flavor identity description."""
    return CUISINE_FLAVOR_IDENTITY.get(cuisine, "Match the characteristic flavor profile of the selected cuisine.")


def build_flavor_prompt_instruction(mode: str, cuisine: str, ingredients: List[str]) -> str:
    """
    Return the LLM flavor-science instruction block.
    Blends computational gastronomy theory with cuisine-authentic flavor identity.
    """
    ing_str = ", ".join(ingredients[:12])
    identity = get_flavor_identity(cuisine)

    base = (
        f"## Flavor Science Directive — {cuisine} Cuisine\n"
        f"**Cuisine flavor identity:** {identity}\n\n"
        f"Every dish option MUST taste authentically {cuisine}. "
        f"Use the characteristic flavor building blocks, aromatics, and techniques of "
        f"{cuisine} cuisine as the lens through which all ingredients are expressed.\n\n"
    )

    if mode == "uniform":
        science = (
            "**Pairing mode: Uniform / Harmonic** — Maximise shared flavor compounds "
            "between the selected ingredients. Identify overlapping volatile molecules "
            f"among: {ing_str}. Build each dish so ingredients reinforce each other's "
            "dominant notes, creating cohesion. The flavor rationale must cite at least "
            "two specific shared molecules.\n"
        )
    else:
        science = (
            "**Pairing mode: Contrasting / Layered** — Deliberately create orthogonal "
            "flavor layers using spice, acid, and fat as contrast agents. "
            f"From: {ing_str} — build bass notes (umami/fermented), mid notes (spice/herb), "
            "and top notes (acid/fresh) as the architecture of the dish. "
            "The flavor rationale must name the chemical contrast and which molecules create the surprise.\n"
        )

    return base + science


def describe_pairing_mode(mode: str, cuisine: str = "") -> str:
    """Return a short user-facing description of the pairing mode."""
    identity = get_flavor_identity(cuisine) if cuisine else ""
    if mode == "uniform":
        return (
            f"**Uniform (Harmonic)** — Ingredients share flavor compounds for cohesive, "
            f"smooth taste. {identity}"
        )
    return (
        f"**Contrasting (Layered)** — Ingredients create orthogonal flavor layers for "
        f"surprising depth. {identity}"
    )
