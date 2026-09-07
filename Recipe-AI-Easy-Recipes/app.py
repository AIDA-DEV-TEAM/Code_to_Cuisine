"""
Code to Cuisine — AI Culinary Engine
Main Streamlit Application — 5-Step Wizard with Human-in-the-Loop Chef Intervention.

Wizard Flow:
  Step 1: Setup (pantry, cuisine, appliances)
  Step 2: Chef Briefing (Checkpoint 1 — pre-ideation)
  Step 3: AI Generation (Ideation + Validation agents)
  Step 4: Choose Dish (Checkpoint 2 — chef selects & refines)
  Step 5: Final Recipe (Timeline + Presentation agents → CulinaryOutput)
  Bonus:  Chat (post-generation Q&A)
"""

import streamlit as st
from uuid import uuid4

from app_config import (
    APP_NAME, UI_PAGE_ICON, LLM_MODEL_NAME
)
from models import RecipeState
from src.services.workflow_service import WorkflowService
from src.ui.components import (
    inject_custom_css,
    render_setup_step,
    render_chef_pre_briefing,
    render_agent_log,
    render_dish_options_carousel,
    render_chef_refinement_panel,
    render_culinary_output,
    render_chat_interface,
    RecipeUI,
)
from src.ui.wizard import (
    init_wizard_state,
    render_wizard_nav,
    render_breadcrumb,
    render_step_nav_buttons,
    get_current_step,
    advance_step,
    WIZARD_STEPS,
)


# ─────────────────────────────────────────────────────────────────────────────
# Page config (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon=UI_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_api_key() -> str | None:
    return st.session_state.get("groq_api_key")


def _build_initial_state(setup: dict, briefing: dict) -> RecipeState:
    """Build a RecipeState from Step 1 + Step 2 inputs."""
    return RecipeState(
        # Step 1 inputs
        ingredients=setup["ingredients"],
        appliance=setup.get("appliance", "Stovetop"),
        available_appliances=setup["available_appliances"],
        dietary_restrictions=setup["dietary_restrictions"],
        cuisine_preference=setup["cuisine_preference"],
        skill_level=setup["skill_level"],
        # Step 2 HITL inputs
        chef_pre_notes=briefing.get("chef_pre_notes", ""),
        chef_pre_priority_ingredients=briefing.get("chef_pre_priority_ingredients", []),
        chef_pre_techniques=briefing.get("chef_pre_techniques", []),
        chef_pre_context=briefing.get("chef_pre_context", ""),
        # Checkpoint 2 defaults
        selected_dish_index=0,
        chef_post_notes="",
        chef_post_removals=[],
        chef_post_swaps={},
        # Agent state defaults
        flavor_pairing_mode="",
        flavor_rationale="",
        dish_options=[],
        validation_attempts=0,
        hallucinated_ingredients=[],
        timeline_plan=[],
        plating_guide={},
        culinary_output={},
        chat_history=[],
        thread_id=st.session_state.get("thread_id", str(uuid4())),
        # Legacy compat
        parsed_ingredients=[],
        recipe_suggestions=[],
        selected_recipe={},
        alternative_recipes=[],
        user_selected_alternative=None,
        nutrition_info={},
        shopping_list=[],
        cooking_tips=[],
        final_recipe={},
        online_search_results=[],
        search_enhanced=False,
        search_enhancement_complete=False,
        verification_result=None,
        processing_step="",
        error_message="",
        agent_log=[],
    )


def _get_workflow() -> WorkflowService:
    """Return a cached WorkflowService (re-used across reruns)."""
    if "workflow_service" not in st.session_state:
        api_key = _get_api_key()
        if api_key:
            st.session_state.workflow_service = WorkflowService(
                groq_api_key=api_key,
                model_name=LLM_MODEL_NAME,
            )
    return st.session_state.get("workflow_service")


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — API Key Configuration
# ─────────────────────────────────────────────────────────────────────────────

def render_api_sidebar():
    """Render API key config at the top of the sidebar."""
    with st.sidebar:
        with st.expander("🔑 API Configuration", expanded=not bool(_get_api_key())):
            with st.form("api_key_form"):
                api_key = st.text_input(
                    "Groq API Key",
                    type="password",
                    placeholder="gsk_...",
                    key="api_key_input",
                )
                submitted = st.form_submit_button("🔑 Save Key", type="primary", use_container_width=True)
                if submitted:
                    if api_key and api_key.startswith("gsk_"):
                        st.session_state.groq_api_key = api_key
                        # Reset cached workflow so it picks up new key
                        st.session_state.pop("workflow_service", None)
                        st.success("✅ API key saved!")
                        st.rerun()
                    else:
                        st.error("Invalid key format. Groq keys typically start with 'gsk_'.")

        if _get_api_key():
            st.markdown("🟢 _Groq key active_")
        else:
            st.markdown("🔴 _Groq key required_")


# ─────────────────────────────────────────────────────────────────────────────
# Step renderers
# ─────────────────────────────────────────────────────────────────────────────

def render_step_1():
    """Step 1 — Setup."""
    render_breadcrumb()
    setup = render_setup_step()

    # Persist setup in session
    st.session_state.setup_data = setup

    render_step_nav_buttons(
        show_back=False,
        next_label="Next: Chef Briefing →",
        next_disabled=not setup.get("can_proceed", False),
    )


def render_step_2():
    """Step 2 — Chef Briefing (Checkpoint 1)."""
    render_breadcrumb()
    setup = st.session_state.get("setup_data", {})
    ingredients = setup.get("ingredients", [])

    briefing = render_chef_pre_briefing(ingredients)
    st.session_state.briefing_data = briefing

    st.markdown("---")
    st.info(
        "ℹ️ Chef briefing is **optional** — you can proceed without adding any notes. "
        "The AI will still generate excellent dish options from the pantry selection.",
        icon="ℹ️",
    )

    render_step_nav_buttons(
        next_label="🚀 Begin AI Generation →",
        next_type="primary",
    )


def render_step_3():
    """Step 3 — AI Generation (Ideation + Validation)."""
    render_breadcrumb()

    st.markdown('<div class="section-title">🧠 AI Agent Generation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The AI agents are building dish options from your Mystery Pantry selection.</div>', unsafe_allow_html=True)

    # Check if phase 1 already done
    if st.session_state.get("phase1_complete") and st.session_state.get("dish_options"):
        st.success(
            f"✅ AI generated **{len(st.session_state.dish_options)} dish options** — proceed to select your choice.",
            icon="✅",
        )
        render_agent_log(st.session_state.get("agent_log", []))
        render_step_nav_buttons(
            next_label="🍽️ Review Dish Options →",
        )
        return

    # API key check
    if not _get_api_key():
        st.error("❌ Groq API key required. Please add it in the sidebar.")
        return

    setup = st.session_state.get("setup_data", {})
    briefing = st.session_state.get("briefing_data", {})

    if not setup.get("ingredients"):
        st.warning("Please go back to Step 1 and select pantry ingredients.")
        render_step_nav_buttons(show_next=False)
        return

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        run_btn = st.button(
            "🚀 Generate Dish Options",
            use_container_width=True,
            type="primary",
            key="run_generation",
        )

    if run_btn:
        # Assign thread_id
        if not st.session_state.get("thread_id"):
            st.session_state.thread_id = str(uuid4())

        initial_state = _build_initial_state(setup, briefing)
        workflow = _get_workflow()

        if not workflow:
            st.error("Failed to initialize workflow. Check your API key.")
            return

        with st.status("🤖 AI Agents Running...", expanded=True) as status:
            st.write("🧠 **Ideation Agent** — Generating creative dish options...")

            try:
                result = workflow.execute_phase1(
                    initial_state,
                    thread_id=st.session_state.thread_id,
                )

                dish_options = result.get("dish_options", [])
                agent_log = result.get("agent_log", [])

                if dish_options:
                    st.write(f"✅ **Constraint Validator** — {len(dish_options)} valid options confirmed!")
                    status.update(
                        label=f"✅ {len(dish_options)} dish options generated!",
                        state="complete",
                    )

                    # Persist to session
                    st.session_state.dish_options = dish_options
                    st.session_state.agent_log = agent_log
                    st.session_state.phase1_state = dict(result)
                    st.session_state.phase1_complete = True

                    render_agent_log(agent_log)
                    st.rerun()
                else:
                    error = result.get("error_message", "Unknown error")
                    status.update(label=f"❌ Generation failed: {error}", state="error")
                    st.error(f"Generation failed: {error}")

            except Exception as e:
                status.update(label=f"❌ Error: {e}", state="error")
                st.error(f"Workflow error: {e}")


def render_step_4():
    """Step 4 — Choose Dish (Checkpoint 2)."""
    render_breadcrumb()

    dish_options = st.session_state.get("dish_options", [])
    setup = st.session_state.get("setup_data", {})
    selected_idx = render_dish_options_carousel(dish_options)

    if selected_idx is not None:
        selected_option = dish_options[selected_idx] if dish_options else {}
        refinement = render_chef_refinement_panel(
            selected_option,
            setup.get("ingredients", []),
        )
        st.session_state.refinement_data = refinement

        st.success(
            f"✅ **{selected_option.get('emoji','')} {selected_option.get('dish_name','')}** selected. "
            "Proceed to generate the full recipe.",
            icon="✅",
        )

        render_step_nav_buttons(
            next_label="📋 Generate Final Recipe →",
        )
    else:
        st.info("Select a dish option above to continue.")
        render_step_nav_buttons(show_next=False)

    # Regenerate option
    st.markdown("---")
    if st.button("🔄 Regenerate All Options", key="regenerate_btn"):
        st.session_state.phase1_complete = False
        st.session_state.dish_options = []
        st.session_state.agent_log = []
        st.session_state.current_step = 3
        st.rerun()


def render_step_5():
    """Step 5 — Final Recipe (Timeline + Presentation)."""
    render_breadcrumb()

    # If phase 2 already complete, just show output
    if st.session_state.get("phase2_complete") and st.session_state.get("culinary_output"):
        wf = _get_workflow()
        current_state = st.session_state.get("phase2_state", st.session_state.get("phase1_state", {}))
        current_state["chat_history"] = st.session_state.get("chat_history", [])
        render_culinary_output(st.session_state.culinary_output, state=current_state, workflow=wf)
        render_agent_log(
            [e for e in st.session_state.get("agent_log", []) 
             if "Timeline" in e or "Presentation" in e]
        )
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Chat with AI About This Recipe", use_container_width=True):
                st.session_state.show_chat = True
                st.rerun()
        return

    # Build phase 2 state
    if not st.session_state.get("phase1_state"):
        st.warning("Please complete Step 3 first.")
        return

    phase1_state = st.session_state.phase1_state
    selected_idx = st.session_state.get("selected_dish_index", 0)
    refinement = st.session_state.get("refinement_data", {})

    # Merge chef Checkpoint 2 data into state
    phase2_state = {
        **phase1_state,
        "selected_dish_index": selected_idx,
        "chef_post_notes": refinement.get("chef_post_notes", ""),
        "chef_post_removals": refinement.get("chef_post_removals", []),
        "chef_post_swaps": refinement.get("chef_post_swaps", {}),
    }

    selected_dish = (phase1_state.get("dish_options") or [{}])[selected_idx]
    st.markdown(
        f'<div class="section-title">{selected_dish.get("emoji","🍽️")} {selected_dish.get("dish_name","Generating recipe...")}</div>',
        unsafe_allow_html=True,
    )

    workflow = _get_workflow()
    if not workflow:
        st.error("Workflow not initialized. Check API key.")
        return

    with st.status("Finalising recipe...", expanded=True) as status:
        st.write("**Timeline Agent** — Building 60-minute execution plan...")
        try:
            # Convert to RecipeState
            from models import RecipeState as RS
            state_obj = RS(**{k: v for k, v in phase2_state.items() if k in RS.__annotations__})
        except Exception:
            state_obj = phase2_state  # fallback: pass raw dict

        try:
            result = workflow.execute_phase2(state_obj, thread_id=st.session_state.thread_id)
            st.write("🎨 **Presentation Agent** — Generating plating guide and pitch narrative...")

            culinary_output = result.get("culinary_output", {})
            if culinary_output:
                status.update(label="Recipe ready!", state="complete")
                st.session_state.culinary_output = culinary_output
                st.session_state.phase2_complete = True
                st.session_state.phase2_state = {**phase2_state, "culinary_output": culinary_output}
                st.session_state.agent_log = result.get("agent_log", st.session_state.get("agent_log", []))
                st.session_state.completed_steps.add(5)
                st.rerun()
            else:
                error = result.get("error_message", "Unknown error")
                status.update(label=f"❌ Failed: {error}", state="error")
                st.error(f"Recipe generation failed: {error}")

        except Exception as e:
            status.update(label=f"❌ Error: {e}", state="error")
            st.error(f"Workflow error: {e}")


def render_chat_step():
    """Bonus Chat step — post-generation Q&A."""
    st.markdown("### 💬 AI Culinary Assistant")
    st.caption("Continue the conversation about your recipe.")

    culinary_output = st.session_state.get("culinary_output", {})
    if not culinary_output:
        st.info("Complete Step 5 to enable the chat assistant.")
        return

    # Display chat
    prompt = render_chat_interface()

    if prompt:
        # Add user message
        chat_messages = st.session_state.get("chat_messages", [])
        chat_messages.append({"role": "user", "content": prompt})
        st.session_state.chat_messages = chat_messages

        # Get response
        workflow = _get_workflow()
        if workflow:
            try:
                phase1_state = st.session_state.get("phase1_state", {})
                state_for_chat = {
                    **phase1_state,
                    "culinary_output": culinary_output,
                    "chat_history": chat_messages,
                }
                response = workflow.invoke_chat(
                    message=prompt,
                    thread_id=st.session_state.get("thread_id", "default"),
                    state=state_for_chat,
                )
                chat_messages.append({"role": "assistant", "content": response})
                st.session_state.chat_messages = chat_messages
                st.rerun()
            except Exception as e:
                st.error(f"Chat error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Main App Entry
# ─────────────────────────────────────────────────────────────────────────────

def main():
    inject_custom_css()
    init_wizard_state()

    # Sidebar: API config + wizard nav
    render_api_sidebar()
    render_wizard_nav()

    # Main content
    current_step = get_current_step()

    if current_step == 1:
        render_step_1()
    elif current_step == 2:
        render_step_2()
    elif current_step == 3:
        render_step_3()
    elif current_step == 4:
        render_step_4()
    elif current_step == 5:
        render_step_5()

    # Chat overlay (shown below Step 5 output)
    if st.session_state.get("show_chat") or st.session_state.get("phase2_complete"):
        if current_step == 5:
            with st.container():
                render_chat_step()


if __name__ == "__main__":
    main()
