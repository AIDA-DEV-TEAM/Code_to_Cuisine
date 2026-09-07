"""
Wizard Step Controller — Multi-Step Navigation for Code to Cuisine.
Manages the 5-step wizard flow with sidebar progress tracking.
"""

import streamlit as st
from typing import List


WIZARD_STEPS = [
    ("🍜", "Setup", "Select pantry ingredients, cuisine & appliances"),
    ("👨‍🍳", "Chef Briefing", "Head chef inputs experience & direction"),
    ("🧠", "AI Generation", "AI agents generate & validate dish options"),
    ("🍽️", "Choose Dish", "Chef reviews options and refines selection"),
    ("📋", "Final Recipe", "Complete culinary output & pitch materials"),
]

STEP_KEYS = ["setup", "chef_briefing", "generating", "choose_dish", "final_recipe"]


def init_wizard_state():
    """Initialize wizard session state variables if not already set."""
    defaults = {
        "current_step": 1,
        "completed_steps": set(),
        "thread_id": None,
        "chef_pre_notes": "",
        "chef_pre_priority_ingredients": [],
        "chef_pre_techniques": [],
        "chef_pre_context": "",
        "dish_options": [],
        "selected_dish_index": 0,
        "chef_post_notes": "",
        "chef_post_removals": [],
        "chef_post_swaps": {},
        "culinary_output": {},
        "agent_log": [],
        "chat_messages": [],
        "workflow_state": {},
        "phase1_complete": False,
        "phase2_complete": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def get_current_step() -> int:
    return st.session_state.get("current_step", 1)


def advance_step():
    current = get_current_step()
    st.session_state.completed_steps.add(current)
    st.session_state.current_step = min(current + 1, len(WIZARD_STEPS))
    st.rerun()


def go_back():
    current = get_current_step()
    st.session_state.current_step = max(current - 1, 1)
    st.rerun()


def go_to_step(n: int):
    """Jump to a completed or current step."""
    current = get_current_step()
    completed = st.session_state.get("completed_steps", set())
    if n <= current or (n - 1) in completed:
        st.session_state.current_step = n
        st.rerun()


def is_step_accessible(n: int) -> bool:
    """Check if a step can be navigated to."""
    current = get_current_step()
    completed = st.session_state.get("completed_steps", set())
    return n <= current or (n - 1) in completed


def render_wizard_nav():
    """Render the sidebar wizard navigation with step indicators."""
    with st.sidebar:
        st.markdown(
            """
            <div style='text-align:center; padding: 12px 0 4px 0;'>
                <span style='font-size:2rem;'>🍛</span><br>
                <span style='font-size:1.1rem; font-weight:700; color:#c0392b;'>Code to Cuisine</span><br>
                <span style='font-size:0.75rem; color:#8b6a52;'>AI Culinary Engine</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        current = get_current_step()
        completed = st.session_state.get("completed_steps", set())

        for i, (icon, label, desc) in enumerate(WIZARD_STEPS, start=1):
            step_num = i
            is_current = step_num == current
            is_done = step_num in completed
            is_locked = not is_step_accessible(step_num)

            if is_done:
                badge = "✅"
                color = "#2e7d32"
                weight = "600"
            elif is_current:
                badge = "🔶"
                color = "#c0392b"
                weight = "700"
            else:
                badge = "○"
                color = "#c5a88a" if is_locked else "#7d4e2d"
                weight = "400"

            btn_label = f"{badge} Step {step_num}: {label}"

            if not is_locked and not is_current:
                if st.button(
                    btn_label,
                    key=f"nav_step_{step_num}",
                    use_container_width=True,
                    type="secondary",
                ):
                    go_to_step(step_num)
                st.caption(f"   _{desc}_")
            else:
                st.markdown(
                    f"<div style='padding:6px 8px; border-radius:6px; "
                    f"background:{'#fde8dc' if is_current else 'transparent'}; "
                    f"border-left:{'3px solid #c0392b' if is_current else 'none'}; "
                    f"color:{color}; font-weight:{weight}; font-size:0.9rem;'>"
                    f"{btn_label}</div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"   _{desc}_")

        st.divider()

        # Quick actions
        st.markdown("**⚙️ Quick Actions**")
        if st.button("🔄 Reset Session", use_container_width=True, type="secondary"):
            for key in list(st.session_state.keys()):
                if key not in ("groq_api_key", "tavily_api_key"):
                    del st.session_state[key]
            st.rerun()

        # Show selected pantry summary if available
        selected = st.session_state.get("workflow_state", {}).get("ingredients", [])
        cuisine = st.session_state.get("workflow_state", {}).get("cuisine_preference", "")
        if selected:
            st.divider()
            st.markdown(f"**🌍 Cuisine:** `{cuisine}`")
            st.markdown(f"**🧺 Pantry:** {len(selected)} items selected")
            with st.expander("View selected ingredients"):
                for ing in selected:
                    st.markdown(f"• {ing}")


def render_breadcrumb():
    """Render a top-of-page breadcrumb trail."""
    current = get_current_step()
    crumbs = []
    for i, (icon, label, _) in enumerate(WIZARD_STEPS, start=1):
        if i < current:
            crumbs.append(f"<span style='color:#2e7d32; font-weight:500;'>{icon} {label}</span>")
        elif i == current:
            crumbs.append(f"<span style='color:#c0392b; font-weight:700;'>{icon} {label}</span>")
        else:
            crumbs.append(f"<span style='color:#c5a88a;'>{icon} {label}</span>")

    breadcrumb_html = " <span style='color:#e8d5bf;'>›</span> ".join(crumbs)
    st.markdown(
        f"<div style='padding:8px 0 16px 0; font-size:0.9rem; background:#fbebd8; border-radius:8px; padding:8px 16px; margin-bottom:16px;'>{breadcrumb_html}</div>",
        unsafe_allow_html=True,
    )


def render_step_nav_buttons(
    show_back: bool = True,
    show_next: bool = True,
    next_label: str = "Next Step →",
    back_label: str = "← Back",
    next_disabled: bool = False,
    next_type: str = "primary",
):
    """Render Back / Next navigation buttons."""
    current = get_current_step()
    cols = st.columns([1, 3, 1])

    with cols[0]:
        if show_back and current > 1:
            if st.button(back_label, use_container_width=True):
                go_back()

    with cols[2]:
        if show_next and current < len(WIZARD_STEPS):
            if st.button(
                next_label,
                use_container_width=True,
                type=next_type,
                disabled=next_disabled,
            ):
                advance_step()
