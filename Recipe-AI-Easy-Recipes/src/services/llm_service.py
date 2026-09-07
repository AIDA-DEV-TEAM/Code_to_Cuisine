"""
LLM Service for the Code to Cuisine AI Culinary Engine.
Handles standard, structured-output, and streaming LLM interactions using Groq.
"""

from typing import Any, Dict, Generator, Type
import json

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from app_config import LLM_MODEL_NAME, LLM_DEFAULT_TEMPERATURE, LLM_IDEATION_TEMPERATURE


class LLMService:
    """Service for managing LLM interactions."""

    def __init__(
        self,
        groq_api_key: str,
        model_name: str = LLM_MODEL_NAME,
        timeout: float = 180.0,
        max_retries: int = 3,
    ):
        self.api_key = groq_api_key
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries

        # Standard client (balanced temperature)
        self.client = ChatGroq(
            model_name=model_name,
            temperature=LLM_DEFAULT_TEMPERATURE,
            api_key=groq_api_key,
            max_tokens=6000,
            timeout=timeout,
            max_retries=max_retries,
        )

        # High-creativity client (for ideation)
        self.creative_client = ChatGroq(
            model_name=model_name,
            temperature=LLM_IDEATION_TEMPERATURE,
            api_key=groq_api_key,
            max_tokens=6000,
            timeout=timeout,
            max_retries=max_retries,
        )

    def generate_json_response(
        self,
        system_prompt: str,
        user_prompt: str,
        creative: bool = False,
    ) -> Dict[str, Any]:
        """Generate JSON response and parse it."""
        try:
            llm = self.creative_client if creative else self.client
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = llm.invoke(messages)
            content = response.content
            if isinstance(content, list):
                content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
            content = content.strip()

            # Strip markdown fences
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            return json.loads(content.strip())

        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {e}")
        except Exception as e:
            raise Exception(f"JSON generation failed: {e}")

    def generate_with_pydantic(
        self,
        system_prompt: str,
        user_prompt: str,
        pydantic_model: Type[BaseModel],
        creative: bool = False,
    ) -> BaseModel:
        """Generate response and parse into a Pydantic model using structured output."""
        try:
            llm = self.creative_client if creative else self.client
            structured_llm = llm.with_structured_output(pydantic_model)
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            return structured_llm.invoke(messages)
        except Exception as e:
            raise Exception(f"Structured output generation failed: {e}")

    def generate_text_response(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a plain text response."""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            response = self.client.invoke(messages)
            content = response.content
            if isinstance(content, list):
                content = content[0].get("text", "") if isinstance(content[0], dict) else str(content[0])
            return content.strip()
        except Exception as e:
            raise Exception(f"Text generation failed: {e}")

    def stream_response(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> Generator[str, None, None]:
        """Stream response tokens for live display."""
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
            for chunk in self.client.stream(messages):
                if chunk.content:
                    if isinstance(chunk.content, list):
                        yield str(chunk.content[0])
                    else:
                        yield chunk.content
        except Exception as e:
            yield f"[Streaming error: {e}]"
