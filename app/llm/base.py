"""Base LLM class — interface that all providers implement."""

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Abstract LLM provider."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """
        Send a prompt to the LLM and return the generated text.

        Args:
            prompt: The user/main prompt.
            system_prompt: System-level instructions.

        Returns:
            Generated text string.
        """
        ...
