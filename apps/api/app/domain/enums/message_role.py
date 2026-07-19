"""Message role enumeration."""

from enum import StrEnum


class MessageRole(StrEnum):
    """Role of a participant message within a conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
