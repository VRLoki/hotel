"""Anthropic LLM provider (Claude)."""

import requests
from .base import BaseLLM
from config import settings


class AnthropicLLM(BaseLLM):
    API_URL = "https://api.anthropic.com/v1/messages"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY not set. Add it to .env or environment.")

        body = {
            "model": settings.ANTHROPIC_MODEL,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            body["system"] = system_prompt

        resp = requests.post(
            self.API_URL,
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["content"][0]["text"]
