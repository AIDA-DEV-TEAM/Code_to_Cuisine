"""
Workflow Service — 4-Agent LangGraph orchestration with MemorySaver.
Implements the full pipeline:
  Ideation → Validator (conditional loop) → [HITL Gate] → Timeline → Presentation
"""

from typing import Any, Dict, Optional
from uuid import uuid4

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from models import RecipeState
from src.agents.ideation_agent import IdeationAgent
from src.agents.validator_agent import ConstraintValidatorAgent
from src.agents.timeline_agent import TimelineSequenceAgent
from src.agents.presentation_agent import PresentationAgent
from app_config import WORKFLOW_MAX_VALIDATION_RETRIES, LLM_MODEL_NAME


class WorkflowService:
    """Orchestrates the 4-agent culinary AI pipeline with MemorySaver checkpointing."""

    def __init__(
        self,
        groq_api_key: str,
        model_name: str = LLM_MODEL_NAME,
        tavily_api_key: Optional[str] = None,
    ):
        self.groq_api_key = groq_api_key
        self.model_name = model_name
        self.tavily_api_key = tavily_api_key

        # Instantiate all four agents
        self.ideation_agent = IdeationAgent(groq_api_key, model_name)
        self.validator_agent = ConstraintValidatorAgent(groq_api_key, model_name)
        self.timeline_agent = TimelineSequenceAgent(groq_api_key, model_name)
        self.presentation_agent = PresentationAgent(groq_api_key, model_name, tavily_api_key=tavily_api_key)

        # MemorySaver checkpointer for persistent conversation memory
        self.checkpointer = MemorySaver()
        self.compiled_graph = self._build_graph()

    def _build_graph(self):
        """Build and compile the LangGraph StateGraph."""

        # Node wrappers
        def ideation_node(state: RecipeState) -> RecipeState:
            return self.ideation_agent.run(state)

        def validator_node(state: RecipeState) -> RecipeState:
            return self.validator_agent.run(state)

        def timeline_node(state: RecipeState) -> RecipeState:
            return self.timeline_agent.run(state)

        def presentation_node(state: RecipeState) -> RecipeState:
            return self.presentation_agent.run(state)

        # Conditional routing: validator → ideation (loop) or timeline (pass)
        def route_after_validation(state: RecipeState) -> str:
            if (
                state.get("processing_step") == "validation_failed"
                and state.get("validation_attempts", 0) < WORKFLOW_MAX_VALIDATION_RETRIES
            ):
                return "ideation_agent"
            return "timeline_agent"

        # Build graph
        graph = StateGraph(RecipeState)

        graph.add_node("ideation_agent", ideation_node)
        graph.add_node("constraint_validator", validator_node)
        graph.add_node("timeline_agent", timeline_node)
        graph.add_node("presentation_agent", presentation_node)

        # Edges
        graph.set_entry_point("ideation_agent")
        graph.add_edge("ideation_agent", "constraint_validator")
        graph.add_conditional_edges(
            "constraint_validator",
            route_after_validation,
            {
                "ideation_agent": "ideation_agent",
                "timeline_agent": "timeline_agent",
            },
        )
        graph.add_edge("timeline_agent", "presentation_agent")
        graph.add_edge("presentation_agent", END)

        return graph.compile(checkpointer=self.checkpointer)

    def execute_phase1(self, initial_state: RecipeState, thread_id: str) -> Dict[str, Any]:
        """
        Phase 1: Run Ideation + Validation only (returns 3 dish options for chef selection).
        This is the first half of the pipeline — stopped before Timeline/Presentation.
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        # Build a phase-1 only graph (ideation + validator only)
        graph_p1 = StateGraph(RecipeState)
        
        def ideation_node(state): return self.ideation_agent.run(state)
        def validator_node(state): return self.validator_agent.run(state)
        
        def route_after_validation(state):
            if (
                state.get("processing_step") == "validation_failed"
                and state.get("validation_attempts", 0) < WORKFLOW_MAX_VALIDATION_RETRIES
            ):
                return "ideation_agent"
            return END
        
        graph_p1.add_node("ideation_agent", ideation_node)
        graph_p1.add_node("constraint_validator", validator_node)
        graph_p1.set_entry_point("ideation_agent")
        graph_p1.add_edge("ideation_agent", "constraint_validator")
        graph_p1.add_conditional_edges(
            "constraint_validator",
            route_after_validation,
            {"ideation_agent": "ideation_agent", END: END},
        )
        compiled_p1 = graph_p1.compile(checkpointer=self.checkpointer)
        
        result = compiled_p1.invoke(initial_state, config=config)
        return result

    def execute_phase2(self, state: RecipeState, thread_id: str) -> Dict[str, Any]:
        """
        Phase 2: Run Timeline + Presentation on the chef-selected dish.
        Called after Checkpoint 2 when the chef finalises their choice.
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        graph_p2 = StateGraph(RecipeState)
        
        def timeline_node(state): return self.timeline_agent.run(state)
        def presentation_node(state): return self.presentation_agent.run(state)
        
        graph_p2.add_node("timeline_agent", timeline_node)
        graph_p2.add_node("presentation_agent", presentation_node)
        graph_p2.set_entry_point("timeline_agent")
        graph_p2.add_edge("timeline_agent", "presentation_agent")
        graph_p2.add_edge("presentation_agent", END)
        compiled_p2 = graph_p2.compile(checkpointer=self.checkpointer)
        
        result = compiled_p2.invoke(state, config=config)
        return result

    def execute_workflow(self, initial_state: RecipeState) -> Dict[str, Any]:
        """
        Full pipeline execution (used for non-HITL / automated testing).
        Runs all 4 agents sequentially.
        """
        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        try:
            result = self.compiled_graph.invoke(initial_state, config=config)
            return dict(result)
        except Exception as e:
            return {"error_message": str(e), "processing_step": "workflow_error"}

    def invoke_chat(
        self,
        message: str,
        thread_id: str,
        state: RecipeState,
        context_section: str = "general",
    ) -> str:
        """
        Post-generation chat — section-aware contextual responses.
        context_section: 'dish_concept' | 'timeline' | 'plating' | 'flavor' | 'pitch' | 'general'
        """
        from langchain_groq import ChatGroq
        from langchain_core.messages import HumanMessage, SystemMessage

        culinary_output = state.get("culinary_output", {})
        dish_name = culinary_output.get("dish_name", "the dish")
        cuisine = state.get("cuisine_preference", "International")

        section_contexts = {
            "dish_concept": (
                f"The chef is reviewing the **Dish Concept** for {dish_name} ({cuisine} cuisine). "
                f"Focus your answers on the dish's story, cultural context, flavour rationale, "
                f"and what makes this dish unique. Dish concept summary: {culinary_output.get('dish_concept_summary', '')[:300]}"
            ),
            "timeline": (
                f"The chef is reviewing the **60-Minute Execution Timeline** for {dish_name}. "
                f"Focus on timing, parallel cooking steps, prep order, and time management. "
                f"Suggest adjustments if asked."
            ),
            "plating": (
                f"The chef is reviewing the **Plating Guide** for {dish_name} ({cuisine} style). "
                f"Focus on presentation, color theory, garnish, plate selection, and visual arrangement. "
                f"Plating guidance: {str(culinary_output.get('plating_guide', {}))[:400]}"
            ),
            "flavor": (
                f"The chef is reviewing the **Flavor Science** section for {dish_name}. "
                f"Focus on the science of flavor pairing, aroma molecules, "
                f"and how the ingredients interact chemically. "
                f"Flavor rationale: {culinary_output.get('flavor_rationale', '')[:300]}"
            ),
            "pitch": (
                f"The chef is reviewing the **Pitch Narrative** for {dish_name}. "
                f"Help craft or improve the competition pitch, storytelling, "
                f"and culinary rationale for judges. "
                f"Innovation: {culinary_output.get('innovation_statement', '')}"
            ),
            "general": (
                f"You are the AI culinary assistant for {dish_name} ({cuisine} cuisine). "
                f"Answer any follow-up questions about the recipe, ingredients, techniques, "
                f"substitutions, timing, or plating. Be specific and concise."
            ),
        }

        system = (
            "You are an expert AI culinary assistant. " +
            section_contexts.get(context_section, section_contexts["general"])
        )

        llm = ChatGroq(
            model_name=self.model_name,
            temperature=0.4,
            api_key=self.groq_api_key,
            max_tokens=1500,
        )

        chat_history = state.get("chat_history", [])
        history_text = "\n".join(
            f"{m['role'].title()}: {m['content']}" for m in chat_history[-6:]
        )

        user_msg = f"{history_text}\nUser: {message}" if history_text else message

        messages = [SystemMessage(content=system), HumanMessage(content=user_msg)]
        response = llm.invoke(messages)
        content = response.content
        if isinstance(content, list):
            content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
        return content.strip()

