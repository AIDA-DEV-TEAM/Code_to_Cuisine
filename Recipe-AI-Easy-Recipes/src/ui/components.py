"""
UI Components for the Code to Cuisine AI Culinary Engine.
All display methods for the 5-step wizard interface.
"""

import streamlit as st
from typing import Any, Dict, List, Optional

from app_config import (
    SUPPORTED_CUISINES, SUPPORTED_APPLIANCES,
    SUPPORTED_SKILL_LEVELS, SUPPORTED_DIETARY_RESTRICTIONS,
    SUPPORTED_CHEF_TECHNIQUES, CHEF_CONTEXT_OPTIONS,
    GLOBAL_INGREDIENT_SUGGESTIONS, INGREDIENT_BASICS_REMINDER,
    CUISINE_PAIRING_MAP,
)
from src.utils.flavor_science import describe_pairing_mode, get_pairing_mode


# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────────────────

def inject_custom_css():
    """Inject the premium design system CSS — Warm Light Mode."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

    /* Root tokens - Warm Light Palette */
    :root {
        --c-primary:       #c0392b;
        --c-primary-dark:  #a93226;
        --c-primary-light: #f7cac9;
        --c-secondary:     #7d4e2d;
        --c-accent:        #e07b39;
        --c-success:       #2e7d32;
        --c-warning:       #e07b39;
        --c-danger:        #c0392b;
        --c-bg:            #fdf6ef;
        --c-bg-alt:        #fbebd8;
        --c-card:          #ffffff;
        --c-card-border:   #e8d5bf;
        --c-text:          #3b2a1a;
        --c-text-muted:    #8b6a52;
        --radius:          12px;
        --shadow:          0 2px 16px rgba(120, 60, 20, 0.10);
        --shadow-hover:    0 6px 24px rgba(120, 60, 20, 0.18);
    }

    /* Base */
    .stApp { background-color: var(--c-bg) !important; }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--c-text); }

    /* Streamlit element overrides */
    .stApp [data-testid="stAppViewContainer"] { background-color: var(--c-bg) !important; }
    .stMarkdown, .stMarkdown p, .stMarkdown li { color: var(--c-text); }
    .stTextInput input, .stTextArea textarea {
        background: var(--c-card) !important;
        border: 1px solid var(--c-card-border) !important;
        color: var(--c-text) !important;
        border-radius: 8px !important;
    }
    .stMultiSelect [data-baseweb="select"] {
        background: var(--c-card) !important;
        border-color: var(--c-card-border) !important;
        border-radius: 8px !important;
    }
    .stNumberInput input {
        background: var(--c-card) !important;
        border-color: var(--c-card-border) !important;
        color: var(--c-text) !important;
    }
    [data-baseweb="tag"] {
        background-color: var(--c-primary-light) !important;
        color: var(--c-primary-dark) !important;
    }
    .stAlert { border-radius: var(--radius) !important; }
    .stTabs [data-baseweb="tab"] { color: var(--c-text-muted) !important; }
    .stTabs [aria-selected="true"] { color: var(--c-primary) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--c-primary) !important; }
    .stTabs [data-baseweb="tab-list"] {
        background-color: var(--c-bg-alt) !important;
        border-radius: 8px !important;
        padding: 4px !important;
    }
    .stExpander { border: 1px solid var(--c-card-border) !important; border-radius: var(--radius) !important; }
    label, .stCheckbox span { color: var(--c-text) !important; }
    .stCaption { color: var(--c-text-muted) !important; }
    .stInfo    { background-color: #fff8f0 !important; border-color: var(--c-accent) !important; color: var(--c-text) !important; }
    .stSuccess { background-color: #f0faf1 !important; color: var(--c-text) !important; }
    .stWarning { background-color: #fffbf0 !important; color: var(--c-text) !important; }
    .stError   { background-color: #fff5f5 !important; color: var(--c-text) !important; }
    hr { border-color: var(--c-card-border) !important; }

    /* Cards */
    .cuisine-card, .agent-card, .metric-card, .timeline-card, .option-card {
        background: var(--c-card);
        border: 1px solid var(--c-card-border);
        border-radius: var(--radius);
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: var(--shadow);
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
        color: var(--c-text);
    }
    .cuisine-card:hover, .option-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
        border-color: var(--c-accent);
    }

    /* Option cards */
    .option-card { border-left: 4px solid var(--c-accent); }
    .option-card.selected { border-color: var(--c-success); background: #f0faf1; }

    /* Section headers */
    .section-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: var(--c-primary);
        margin-bottom: 6px;
    }
    .section-subtitle { font-size: 0.92rem; color: var(--c-text-muted); margin-bottom: 20px; }

    /* Timeline rows */
    .timeline-early { border-left: 4px solid #2e7d32; background: #f5fbf5; color: var(--c-text); }
    .timeline-mid   { border-left: 4px solid #e07b39; background: #fff9f4; color: var(--c-text); }
    .timeline-late  { border-left: 4px solid #c0392b; background: #fff5f5; color: var(--c-text); }

    /* Agent log */
    .agent-log-entry {
        padding: 8px 14px;
        border-radius: 8px;
        margin: 5px 0;
        background: #fff8f0;
        border-left: 3px solid var(--c-accent);
        font-size: 0.88rem;
        color: var(--c-text);
    }

    /* Chef checkpoint banners */
    .checkpoint-banner {
        background: linear-gradient(135deg, #fff3e0, #ffe0cc);
        border: 1px solid var(--c-accent);
        border-radius: var(--radius);
        padding: 18px 22px;
        margin-bottom: 20px;
    }
    .checkpoint-banner h3 { color: var(--c-primary); margin: 0 0 4px 0; }
    .checkpoint-banner p  { color: var(--c-text-muted); margin: 0; font-size: 0.9rem; }

    /* Innovation banner */
    .innovation-banner {
        background: linear-gradient(135deg, #f0faf1, #e8f5e9);
        border: 1px solid #66bb6a;
        border-radius: var(--radius);
        padding: 16px 20px;
        margin: 12px 0;
        color: var(--c-text);
    }

    /* Pitch card */
    .pitch-card {
        background: linear-gradient(135deg, #fffde7, #fff8e1);
        border: 1px solid #e6b800;
        border-radius: var(--radius);
        padding: 22px;
        margin: 12px 0;
        color: var(--c-text);
    }

    /* Buttons */
    .stButton > button[kind="primary"] {
        background: var(--c-primary) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
        transition: background 0.15s ease, transform 0.1s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: var(--c-primary-dark) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"] {
        background: var(--c-card) !important;
        border: 1px solid var(--c-card-border) !important;
        border-radius: 8px !important;
        color: var(--c-text) !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--c-accent) !important;
        color: var(--c-primary) !important;
    }

    /* Pantry pills */
    .pantry-pill {
        display: inline-block;
        background: var(--c-bg-alt);
        border: 1px solid var(--c-card-border);
        border-radius: 20px;
        padding: 3px 10px;
        margin: 2px;
        font-size: 0.8rem;
        color: var(--c-text);
    }

    /* Color swatches */
    .color-swatch {
        display: inline-block;
        width: 24px; height: 24px;
        border-radius: 50%;
        margin-right: 8px;
        vertical-align: middle;
        border: 2px solid var(--c-card-border);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #fdf0e0 !important;
        border-right: 1px solid #e8d5bf !important;
    }
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span { color: var(--c-text) !important; }
    [data-testid="stSidebar"] hr { border-color: #e8d5bf !important; }
    [data-testid="stSidebar"] .stButton > button {
        background: var(--c-card) !important;
        color: var(--c-text) !important;
        border: 1px solid var(--c-card-border) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        border-color: var(--c-accent) !important;
        color: var(--c-primary) !important;
    }

    /* Metric tiles */
    .metric-tile {
        background: var(--c-bg-alt);
        border: 1px solid var(--c-card-border);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: var(--c-primary); }
    .metric-label { font-size: 0.8rem; color: var(--c-text-muted); margin-top: 2px; }

    /* Download button */
    .stDownloadButton > button {
        background: var(--c-card) !important;
        border: 1px solid var(--c-card-border) !important;
        color: var(--c-text) !important;
        border-radius: 8px !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--c-accent) !important;
        color: var(--c-primary) !important;
    }

    /* Chat */
    [data-testid="stChatMessage"] { background: var(--c-card) !important; border-radius: 10px !important; }
    [data-testid="stChatInputContainer"] {
        background: var(--c-card) !important;
        border: 1px solid var(--c-card-border) !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Setup
# ─────────────────────────────────────────────────────────────────────────────

def render_setup_step() -> Dict[str, Any]:
    """Step 1: Free-text + searchable ingredient input, cuisine, appliances, skill."""
    st.markdown('<div class="section-title">\U0001f9d1\u200d\U0001f373 Step 1: Kitchen Setup</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Tell us exactly what ingredients you have. Include EVERYTHING — even salt, oil, and water. The AI will only use what you provide.</div>',
        unsafe_allow_html=True,
    )

    # Cuisine selector
    st.markdown("#### \U0001f30d Target Cuisine")
    cuisine_col1, cuisine_col2 = st.columns([2, 1])
    with cuisine_col1:
        cuisine = st.selectbox(
            "Select cuisine style",
            SUPPORTED_CUISINES,
            index=0,
            help="The AI will generate dishes that taste authentically like the chosen cuisine.",
            key="cuisine_select",
        )
        pairing_mode = get_pairing_mode(cuisine)
        mode_emoji = "\U0001f300" if pairing_mode == "contrasting" else "\U0001f3b5"
        st.caption(f"{mode_emoji} **{cuisine}** \u2192 {pairing_mode.title()} flavor pairing mode")
    st.divider()

    # Ingredient selection
    st.markdown("#### \U0001f944 Your Available Ingredients")
    st.info(
        "**Important:** Include ALL ingredients you have access to \u2014 salt, oil, sugar, water, "
        "spices, everything. The recipe will use ONLY what you list here. If you don't include "
        "an ingredient, the AI will substitute or work without it.",
        icon="\U0001f512",
    )

    # Searchable multiselect from global list
    selected_from_list = st.multiselect(
        "Search and select from 300+ global ingredients (veg + non-veg)",
        GLOBAL_INGREDIENT_SUGGESTIONS,
        key="ingredients_multiselect",
        help="Type to search. Both vegetarian and non-vegetarian options included.",
        placeholder="Type ingredient name (e.g. Chicken breast, Tofu, Lemon...)",
    )

    # Free-text custom ingredient adder
    st.markdown("**\u2795 Add a custom ingredient not in the list above:**")
    custom_col, btn_col = st.columns([4, 1])
    with custom_col:
        custom_ing = st.text_input(
            "Custom ingredient",
            key="custom_ingredient_input",
            placeholder="e.g. Wild boar belly, Purple yam, Dried barberries...",
            label_visibility="collapsed",
        )
    with btn_col:
        add_clicked = st.button("Add \u2795", key="add_custom_ing", use_container_width=True)

    if "custom_ingredients" not in st.session_state:
        st.session_state.custom_ingredients = []

    if add_clicked and custom_ing.strip():
        ing = custom_ing.strip().title()
        if ing not in st.session_state.custom_ingredients:
            st.session_state.custom_ingredients.append(ing)
            st.rerun()

    # Show custom ingredients with remove buttons
    if st.session_state.custom_ingredients:
        st.markdown("**Custom ingredients added:**")
        remove_cols = st.columns(min(len(st.session_state.custom_ingredients), 4))
        for i, ing in enumerate(st.session_state.custom_ingredients):
            with remove_cols[i % 4]:
                if st.button(f"\u274c {ing}", key=f"remove_custom_{i}", use_container_width=True):
                    st.session_state.custom_ingredients.pop(i)
                    st.rerun()

    # Combine all ingredients (deduplicate)
    all_selected = list(dict.fromkeys(selected_from_list + st.session_state.custom_ingredients))

    if all_selected:
        # Missing basics warning
        missing_basics = [b for b in INGREDIENT_BASICS_REMINDER if not any(
            b.lower() in a.lower() or a.lower() in b.lower() for a in all_selected
        )]
        if missing_basics:
            st.warning(
                f"\u26a0\ufe0f **Common basics not in your list:** {', '.join(missing_basics[:5])}. "
                "The AI will find creative substitutes from your listed ingredients.",
                icon="\U0001f4a1",
            )
        # Ingredient count with veg/non-veg split
        non_veg_keywords = ["chicken","beef","lamb","pork","fish","prawn","shrimp","salmon",
                             "tuna","cod","duck","turkey","crab","lobster","squid","bacon",
                             "ham","venison","quail","anchov","mackerel","sardine","mussel",
                             "scallop","clam","goat","veal"]
        non_veg_count = sum(1 for i in all_selected if any(k in i.lower() for k in non_veg_keywords))
        veg_count = len(all_selected) - non_veg_count
        st.success(
            f"\U0001f6d2 **{len(all_selected)} ingredients ready** \u2014 "
            f"\U0001f33f {veg_count} plant-based \u00b7 \U0001f969 {non_veg_count} animal-based"
        )
    else:
        st.info("\U0001f446 Start by searching for your ingredients above.", icon="\U0001f4a1")

    st.divider()

    # Kitchen setup
    st.markdown("#### \U0001f525 Kitchen Configuration")
    setup_col1, setup_col2 = st.columns(2)
    with setup_col1:
        appliances = st.multiselect(
            "Available Cooking Appliances",
            SUPPORTED_APPLIANCES,
            default=["Stovetop / Gas hob"],
            key="appliances_select",
        )
        skill = st.selectbox("Skill Level", SUPPORTED_SKILL_LEVELS, index=1, key="skill_select")
    with setup_col2:
        dietary = st.multiselect(
            "Dietary Restrictions / Requirements",
            SUPPORTED_DIETARY_RESTRICTIONS,
            key="dietary_select",
        )
        st.caption("The AI will respect all dietary restrictions across all dish options.")

    can_proceed = len(all_selected) >= 3 and len(appliances) >= 1
    if not can_proceed:
        st.warning("\u26a0\ufe0f Please add at least 3 ingredients and select an appliance to continue.", icon="\u26a0\ufe0f")

    return {
        "ingredients": all_selected,
        "cuisine_preference": cuisine,
        "available_appliances": appliances,
        "appliance": appliances[0] if appliances else "Stovetop / Gas hob",
        "skill_level": skill,
        "dietary_restrictions": dietary,
        "can_proceed": can_proceed,
    }

# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Chef Briefing (Checkpoint 1)
# ─────────────────────────────────────────────────────────────────────────────

def render_chef_pre_briefing(selected_ingredients: List[str]) -> Dict[str, Any]:
    """Checkpoint 1: Head Chef pre-ideation briefing form."""
    st.markdown(
        """<div class="checkpoint-banner">
        <h3>👨‍🍳 Checkpoint 1 — Head Chef Briefing</h3>
        <p>Before the AI begins ideation, share your culinary experience and direction.
        Your input will be injected directly into the AI's creative process.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        context = st.selectbox(
            "🎯 Occasion / Cultural Context",
            [""] + CHEF_CONTEXT_OPTIONS,
            help="This shapes the dish formality and presentation direction.",
            key="chef_context",
        )
        priority_ings = st.multiselect(
            "⭐ Ingredients to Feature Prominently",
            [i for i in selected_ingredients if i not in ("Water", "Salt", "Pepper", "Sugar")],
            help="These ingredients will be highlighted in the AI's ideation prompt.",
            key="chef_priority_ings",
        )

    with col2:
        techniques = st.multiselect(
            "🔪 Techniques to Apply",
            SUPPORTED_CHEF_TECHNIQUES,
            help="The AI will build the dish around these cooking methods.",
            key="chef_techniques",
        )

    chef_notes = st.text_area(
        "📝 Your Personal Experience & Notes",
        placeholder=(
            "Share your culinary instincts here...\n\n"
            "e.g. 'I've found that slow-cooking red lentils with tamarind creates a beautiful "
            "acidic balance. I'd like to explore combining it with the bittersweet chocolate "
            "for an unexpected mole-like depth.'"
        ),
        height=150,
        key="chef_notes_input",
    )

    if chef_notes or priority_ings or techniques or context:
        st.success("✅ Chef guidance captured — AI will incorporate this into the ideation prompt.", icon="👨‍🍳")

    return {
        "chef_pre_notes": chef_notes,
        "chef_pre_priority_ingredients": priority_ings,
        "chef_pre_techniques": techniques,
        "chef_pre_context": context,
        "has_input": bool(chef_notes or priority_ings or techniques or context),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — AI Generation Console
# ─────────────────────────────────────────────────────────────────────────────

def render_agent_log(log_entries: List[str]):
    """Render the visible AI reasoning console."""
    if not log_entries:
        return
    st.markdown("#### 🤖 AI Reasoning Console")
    for entry in log_entries:
        st.markdown(
            f'<div class="agent-log-entry">{entry}</div>',
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Choose Dish (Checkpoint 2)
# ─────────────────────────────────────────────────────────────────────────────

def render_dish_options_carousel(dish_options: List[Dict[str, Any]]) -> Optional[int]:
    """
    Checkpoint 2: Display 3 dish options as cards; return the selected index or None.
    """
    st.markdown(
        """<div class="checkpoint-banner">
        <h3>🍽️ Checkpoint 2 — Chef Reviews & Selects</h3>
        <p>The AI has generated 3 distinct dish concepts. Review each option and 
        select, modify, or request a complete regeneration.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    if not dish_options:
        st.warning("No dish options generated yet.")
        return None

    selected_index = st.session_state.get("selected_dish_index", None)
    cols = st.columns(len(dish_options))

    for i, option in enumerate(dish_options):
        with cols[i]:
            name = option.get("dish_name", f"Option {i+1}")
            emoji = option.get("emoji", "🍽️")
            summary = option.get("flavor_profile_summary", "")
            techniques = option.get("key_techniques", [])
            innovation = option.get("innovation_highlight", "")
            difficulty = option.get("difficulty", "")
            primary_ings = option.get("primary_ingredients", [])

            is_selected = (selected_index == i)
            card_class = "option-card selected" if is_selected else "option-card"

            st.markdown(
                f"""<div class="{card_class}">
                <div style="font-size:2.5rem; text-align:center; margin-bottom:8px;">{emoji}</div>
                <div style="font-weight:700; font-size:1.1rem; color:#c0392b; text-align:center; margin-bottom:12px;">{name}</div>
                <div style="font-size:0.85rem; color:#7d4e2d; margin-bottom:12px;">{summary}</div>
                <div style="font-size:0.8rem; margin-bottom:8px;">
                    <strong>Techniques:</strong> {', '.join(techniques[:2])}
                </div>
                <div style="font-size:0.8rem; color:#2e7d32; margin-bottom:8px;">
                    ✨ <em>{innovation}</em>
                </div>
                <div style="font-size:0.8rem; color:#7d4e2d;">Difficulty: {difficulty}</div>
                </div>""",
                unsafe_allow_html=True,
            )

            if st.button(
                f"✅ Select Option {i+1}",
                key=f"select_dish_{i}",
                use_container_width=True,
                type="primary" if not is_selected else "secondary",
            ):
                st.session_state.selected_dish_index = i
                st.rerun()

    return st.session_state.get("selected_dish_index", None)


def render_chef_refinement_panel(selected_option: Dict[str, Any], selected_ingredients: List[str]) -> Dict[str, Any]:
    """Refinement panel after dish selection."""
    if not selected_option:
        return {}

    st.markdown("---")
    st.markdown("#### ✏️ Refine Your Selection")
    st.markdown(
        f"**Selected:** {selected_option.get('emoji','🍽️')} **{selected_option.get('dish_name','')}**"
    )

    with st.expander("🔧 Open Refinement Panel", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            removals = st.multiselect(
                "Remove ingredients",
                selected_option.get("primary_ingredients", []),
                key="chef_removals",
            )
            technique_change = st.text_input(
                "Change/add technique",
                placeholder="e.g. 'Use Dum instead of boiling'",
                key="technique_change",
            )
        with col2:
            portion_note = st.number_input("Adjust servings", min_value=1, max_value=20, value=4, key="servings_adj")

        post_notes = st.text_area(
            "Additional chef notes / final instructions",
            placeholder="e.g. 'Reduce the tamarind by half, add a jaggery glaze at the end for sweetness...'",
            height=100,
            key="chef_post_notes_input",
        )

    combined_notes = post_notes
    if technique_change:
        combined_notes = f"Technique: {technique_change}. Servings: {portion_note}. {post_notes}"

    return {
        "chef_post_notes": combined_notes,
        "chef_post_removals": removals,
        "chef_post_swaps": {},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Final Recipe Display
# ─────────────────────────────────────────────────────────────────────────────

def _section_chat(output: dict, state: dict, section: str, workflow, key_prefix: str):
    """Render a compact contextual AI chat for a specific output section."""
    thread_id = state.get("thread_id", "default")
    chat_key = f"{key_prefix}_chat_history"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []

    with st.expander(f"\U0001f4ac Ask AI about this section", expanded=False):
        for msg in st.session_state[chat_key]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input(f"Ask about {section.replace('_', ' ')}...", key=f"chat_input_{key_prefix}"):
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            with st.spinner("Thinking..."):
                try:
                    reply = workflow.invoke_chat(
                        message=prompt,
                        thread_id=thread_id,
                        state=state,
                        context_section=section,
                    )
                except Exception as e:
                    reply = f"Sorry, I encountered an error: {e}"
            st.session_state[chat_key].append({"role": "assistant", "content": reply})
            st.rerun()


def render_culinary_output(output: dict, state: dict = None, workflow=None):
    """Master display for the complete CulinaryOutput with 6-tab layout."""
    if not output:
        st.warning("No recipe output available.")
        return

    dish_name = output.get("dish_name", "Dish")
    emoji = output.get("emoji", "\U0001f37d\ufe0f")
    cuisine = output.get("cuisine_type", "")
    cook_time = len(output.get("timeline_plan", [])) * 10 or 60

    # Hero header
    st.markdown(
        f"""<div style='background:linear-gradient(135deg,#fff3e0,#fbebd8);
        border:1px solid #e8d5bf; border-radius:16px; padding:24px 28px; margin-bottom:24px;'>
        <div style='font-family:Playfair Display,serif; font-size:2rem; font-weight:700; color:#c0392b;'>
        {emoji} {dish_name}</div>
        <div style='color:#7d4e2d; font-size:1rem; margin-top:4px;'>
        {cuisine} cuisine &middot; ~{cook_time} minutes</div>
        </div>""",
        unsafe_allow_html=True,
    )

    # 6 tabs
    tabs = st.tabs([
        "\U0001f4d6 Dish Concept",
        "\u23f1\ufe0f 60-Min Plan",
        "\U0001f3a8 Plating Guide",
        "\U0001f5bc\ufe0f Plating Vision",
        "\U0001f9ea Flavor Science",
        "\U0001f3a4 Pitch",
    ])

    with tabs[0]:
        _render_dish_concept_tab(output, state, workflow)
    with tabs[1]:
        _render_timeline_tab(output, state, workflow)
    with tabs[2]:
        _render_plating_tab(output, state, workflow)
    with tabs[3]:
        _render_plating_vision_tab(output, state, workflow)
    with tabs[4]:
        _render_flavor_science_tab(output, state, workflow)
    with tabs[5]:
        _render_pitch_tab(output, state, workflow)


def _render_dish_concept_tab(output: dict, state: dict = None, workflow=None):
    """Tab 1: Dish Concept document."""
    st.markdown("### \U0001f4d6 Dish Concept")

    summary = output.get("dish_concept_summary", "")
    if summary:
        st.markdown(f"> {summary}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**\U0001f9c2 Ingredients Used**")
        for ing in output.get("ingredients_used", []):
            st.markdown(f"- {ing}")
        subs = output.get("substitutions_made", [])
        if subs:
            st.markdown("**\U0001f504 Substitutions Made**")
            for s in subs:
                st.info(s, icon="\U0001f4a1")
    with col2:
        st.markdown("**\U0001f52a Techniques**")
        for t in output.get("techniques", []):
            st.markdown(f"- **{t}**")
        st.markdown("**\U0001f4ca Nutrition (estimated)**")
        nutr = output.get("nutrition_summary", {})
        if nutr:
            n1, n2, n3 = st.columns(3)
            n1.metric("Calories", f"{nutr.get('calories_per_serving', 0)} kcal")
            n2.metric("Protein", f"{nutr.get('protein_g', 0)}g")
            n3.metric("Carbs", f"{nutr.get('carbs_g', 0)}g")

    allergens = output.get("allergen_info", [])
    if allergens:
        st.warning(f"\u26a0\ufe0f Allergens: {', '.join(allergens)}", icon="\u26a0\ufe0f")

    if output.get("serving_suggestions"):
        st.markdown(f"**\U0001f374 Serving Suggestions:** {output['serving_suggestions']}")

    if state and workflow:
        _section_chat(output, state, "dish_concept", workflow, "dish_concept")


def _render_timeline_tab(output: dict, state: dict = None, workflow=None):
    """Tab 2: 60-minute execution timeline."""
    st.markdown("### \u23f1\ufe0f 60-Minute Kitchen Execution Plan")

    timeline = output.get("timeline_plan", [])
    if timeline:
        for step in timeline:
            t = step.get("start_minute", 0)
            css_class = "timeline-early" if t < 20 else ("timeline-mid" if t < 45 else "timeline-late")
            st.markdown(
                f"""<div class='{css_class}' style='border-radius:8px; padding:12px 16px; margin:8px 0;'>
                <strong>{step.get('emoji', '\u23f0')} {step.get('start_minute', 0)}-{step.get('end_minute', 0)} min
                &mdash; {step.get('task', '')}</strong><br>
                <span style='color:var(--c-text-muted); font-size:0.9rem;'>
                {step.get('parallel_tasks', step.get('detail', ''))}</span>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        steps = output.get("step_by_step_instructions", [])
        if steps:
            for i, step in enumerate(steps, 1):
                st.markdown(f"**Step {i}:** {step}")
        else:
            st.info("Timeline not generated — run Phase 2 to produce the execution plan.")

    if state and workflow:
        _section_chat(output, state, "timeline", workflow, "timeline")


def _render_plating_tab(output: dict, state: dict = None, workflow=None):
    """Tab 3: Plating Guide."""
    st.markdown("### \U0001f3a8 Plating Guide")

    guide = output.get("plating_guide", {})
    if not guide:
        st.info("Plating guide will be generated in Phase 2.")
        return

    # Visual description
    if guide.get("visual_description"):
        st.markdown(
            f"""<div class='pitch-card' style='background:linear-gradient(135deg,#fffde7,#fff8e1);'>
            <em>"{guide['visual_description']}"</em></div>""",
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)
    with col1:
        seq = guide.get("plating_sequence", [])
        if seq:
            st.markdown("**\U0001f4cd Plating Sequence**")
            for step in seq:
                st.markdown(f"- {step}")

        garnish = guide.get("garnish_suggestions", [])
        if garnish:
            st.markdown("**\U0001f33f Garnish**")
            for g in garnish:
                st.markdown(f"- {g}")

        if guide.get("plate_type_recommendation"):
            st.markdown(f"**\U0001f37d\ufe0f Plate:** {guide['plate_type_recommendation']}")

    with col2:
        colors = guide.get("primary_colors", [])
        if colors:
            st.markdown("**\U0001f3a8 Color Palette**")
            for c in colors:
                st.markdown(f"- {c}")

        if guide.get("texture_contrast"):
            st.markdown(f"**\U0001f9f1 Texture:** {guide['texture_contrast']}")

        if guide.get("color_theory_note"):
            st.markdown(f"**\U0001f4ac Color Theory:** {guide['color_theory_note']}")

    if state and workflow:
        _section_chat(output, state, "plating", workflow, "plating")


def _render_plating_vision_tab(output: dict, state: dict = None, workflow=None):
    """Tab 4: AI-generated dish image + web plating references."""
    st.markdown("### \U0001f5bc\ufe0f Plating Vision — AI Dish Visualization")
    st.caption("An AI-generated image showing how this dish could look plated. Use as a visual reference.")

    img_url = output.get("plating_image_url", "")
    dish_name = output.get("dish_name", "Dish")
    cuisine = output.get("cuisine_type", "")

    if img_url:
        st.image(img_url, caption=f"{dish_name} — {cuisine} style plating concept", use_container_width=True)
        st.caption(
            "\U0001f916 AI-generated via Pollinations.ai &middot; "
            "Use this as a creative reference, not a strict blueprint."
        )
    else:
        st.info(
            "The AI plating image will appear here after Phase 2 is complete. "
            "It is generated using Pollinations.ai (free, no API key required).",
            icon="\U0001f4f7",
        )

    # Web-sourced plating references
    refs = output.get("plating_web_references", [])
    if refs:
        st.divider()
        st.markdown("#### \U0001f310 Web Plating References")
        st.caption("Top-rated plating inspiration sourced via Tavily web search:")
        for i, url in enumerate(refs, 1):
            st.markdown(f"{i}. [{url[:60]}...]({url})")
    elif img_url:
        st.info(
            "\U0001f50e Add a Tavily API key in the sidebar to enable live web plating references.",
            icon="\U0001f4a1",
        )

    if state and workflow:
        _section_chat(output, state, "plating", workflow, "plating_vision")


def _render_flavor_science_tab(output: dict, state: dict = None, workflow=None):
    """Tab 5: Flavor Science."""
    st.markdown("### \U0001f9ea Flavor Science")

    mode = output.get("flavor_pairing_mode", "")
    rationale = output.get("flavor_rationale", "")
    profile = output.get("flavor_profile", "")

    if mode:
        mode_color = "#e07b39" if mode == "contrasting" else "#2e7d32"
        st.markdown(
            f"<div style='display:inline-block; background:{mode_color}22; "
            f"border:1px solid {mode_color}; border-radius:20px; padding:4px 14px; "
            f"color:{mode_color}; font-weight:600; font-size:0.9rem;'>"
            f"\U0001f9ea {mode.title()} Pairing Mode</div>",
            unsafe_allow_html=True,
        )

    if rationale:
        st.markdown(f"\n**Flavor Rationale:**\n> {rationale}")

    if profile:
        st.markdown(f"**Flavor Profile:**\n{profile}")

    if not rationale and not profile:
        st.info("Flavor science analysis will be generated in Phase 2.")

    if state and workflow:
        _section_chat(output, state, "flavor", workflow, "flavor_science")


def _render_pitch_tab(output: dict, state: dict = None, workflow=None):
    """Tab 6: Pitch Narrative."""
    st.markdown("### \U0001f3a4 Pitch Narrative")

    innovation = output.get("innovation_statement", "")
    if innovation:
        st.markdown(
            f"""<div class='innovation-banner'>
            <strong>\U0001f4a1 Innovation Statement</strong><br>{innovation}
            </div>""",
            unsafe_allow_html=True,
        )

    rationale = output.get("culinary_rationale", "")
    if rationale:
        st.markdown("**Culinary Rationale for Judges:**")
        for para in rationale.split("\n\n"):
            if para.strip():
                st.markdown(para.strip())

    story = output.get("human_ai_collaboration_story", "")
    if story:
        st.markdown("---")
        st.markdown("**\U0001f91d Human-AI Collaboration Story:**")
        for para in story.split("\n\n"):
            if para.strip():
                st.markdown(para.strip())

    chef_notes = output.get("chef_adaptation_notes", "")
    if chef_notes:
        st.info(f"\U0001f468\u200d\U0001f373 Chef's Influence: {chef_notes}", icon="\U0001f468\u200d\U0001f373")

    if state and workflow:
        _section_chat(output, state, "pitch", workflow, "pitch")


def render_export_panel(output: Dict[str, Any]):
    """Export recipe as markdown card."""
    if not output:
        return
    st.markdown("#### 📥 Export Recipe")

    recipe_md = f"""# {output.get('emoji','🍽️')} {output.get('dish_name','')}
**Cuisine:** {output.get('cuisine_type','')}

## Dish Concept
{output.get('dish_concept_summary','')}

## Ingredients
{chr(10).join('- ' + q for q in output.get('ingredient_quantities', output.get('ingredients_used',[])))}

## Techniques
{chr(10).join('- ' + t for t in output.get('techniques', []))}

## Step-by-Step Instructions
{chr(10).join(f'{i+1}. {s}' for i,s in enumerate(output.get('step_by_step_instructions',[])))}

## Flavor Science
**Mode:** {output.get('flavor_pairing_mode','').title()}
{output.get('flavor_rationale','')}

## Innovation
{output.get('innovation_statement','')}

## Culinary Rationale
{output.get('culinary_rationale','')}

## Human-AI Collaboration
{output.get('human_ai_collaboration_story','')}
"""

    st.download_button(
        label="📥 Download Recipe Card (Markdown)",
        data=recipe_md,
        file_name=f"{output.get('dish_name','recipe').replace(' ','_')}_recipe.md",
        mime="text/markdown",
        use_container_width=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Chat Interface
# ─────────────────────────────────────────────────────────────────────────────

def render_chat_interface():
    """Post-generation chat interface with message history."""
    st.markdown("### 💬 Ask the AI Culinary Assistant")
    st.caption("Ask follow-up questions about the recipe — substitutions, technique tips, timing adjustments.")

    chat_messages = st.session_state.get("chat_messages", [])

    # Display history
    for msg in chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Ask about the recipe...", key="chat_input_main"):
        return prompt
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Legacy RecipeUI class (kept for compatibility)
# ─────────────────────────────────────────────────────────────────────────────

class RecipeUI:
    """Legacy UI class — provides simple display helpers."""

    def display_success_message(self, message: str):
        st.success(message)

    def display_error_message(self, message: str):
        st.error(message)

    def display_warning_message(self, message: str):
        st.warning(message)

    def display_info_message(self, message: str):
        st.info(message)

    def display_complete_recipe(self, result: Dict[str, Any]):
        culinary_output = result.get("culinary_output", {})
        if culinary_output:
            render_culinary_output(culinary_output)
        else:
            st.json(result.get("final_recipe", result))
