"""Local LLM provider via Ollama."""

import requests
from .base import BaseLLM
from config import settings


class LocalLLM(BaseLLM):

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"

        full_prompt = ""
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n---\n\n{prompt}"
        else:
            full_prompt = prompt

        resp = requests.post(
            url,
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {"temperature": 0.4},
            },
            timeout=300,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
