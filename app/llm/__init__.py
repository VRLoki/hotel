"""LLM provider abstraction layer."""

from __future__ import annotations

from .base import BaseLLM
from .openai_llm import OpenAILLM
from .anthropic_llm import AnthropicLLM
from .mistral_llm import MistralLLM
from .local_llm import LocalLLM

PROVIDERS: dict[str, type[BaseLLM]] = {
    "openai": OpenAILLM,
    "anthropic": AnthropicLLM,
    "mistral": MistralLLM,
    "local": LocalLLM,
}


def get_provider(name: str) -> BaseLLM:
    """Instantiate and return the named LLM provider."""
    cls = PROVIDERS.get(name.lower())
    if not cls:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown LLM provider '{name}'. Available: {available}")
    return cls()
