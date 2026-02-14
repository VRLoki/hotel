"""Telegram delivery via Bot API."""

import requests
from config import settings


class TelegramDelivery:
    API_URL = "https://api.telegram.org/bot{token}/sendMessage"

    def deliver(self, recap: str, **kwargs) -> None:
        if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
            raise RuntimeError("Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")

        url = self.API_URL.format(token=settings.TELEGRAM_BOT_TOKEN)

        # Telegram has a 4096 char limit per message; split if needed
        chunks = self._split(recap, 4000)
        for chunk in chunks:
            resp = requests.post(url, json={
                "chat_id": settings.TELEGRAM_CHAT_ID,
                "text": chunk,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            }, timeout=30)
            resp.raise_for_status()

        print(f"✅ Recap sent to Telegram chat {settings.TELEGRAM_CHAT_ID}")

    @staticmethod
    def _split(text: str, max_len: int) -> list[str]:
        if len(text) <= max_len:
            return [text]
        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            # Try to split at a newline
            idx = text.rfind("\n", 0, max_len)
            if idx == -1:
                idx = max_len
            chunks.append(text[:idx])
            text = text[idx:].lstrip("\n")
        return chunks
