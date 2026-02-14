"""Delivery channels package."""

from .console import ConsoleDelivery
from .email_out import EmailDelivery
from .telegram_out import TelegramDelivery

CHANNELS = {
    "console": ConsoleDelivery,
    "email": EmailDelivery,
    "telegram": TelegramDelivery,
}


def get_delivery(name: str):
    cls = CHANNELS.get(name.lower())
    if not cls:
        available = ", ".join(CHANNELS.keys())
        raise ValueError(f"Unknown delivery channel '{name}'. Available: {available}")
    return cls()
