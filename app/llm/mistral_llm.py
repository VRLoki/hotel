"""Mistral LLM provider."""

import requests
from .base import BaseLLM
from config import settings


class MistralLLM(BaseLLM):
    API_URL = "https://api.mistral.ai/v1/chat/completions"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not settings.MISTRAL_API_KEY:
            raise RuntimeError("MISTRAL_API_KEY not set. Add it to .env or environment.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        resp = requests.post(
            self.API_URL,
            headers={
                "Authorization": f"Bearer {settings.MISTRAL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.MISTRAL_MODEL,
                "messages": messages,
                "temperature": 0.4,
                "max_tokens": 4096,
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
