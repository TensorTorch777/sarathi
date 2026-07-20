"""In-memory conversation session store (progressive disclosure only)."""

from __future__ import annotations

from threading import Lock
from uuid import UUID

from app.conversation.conversation_state import ConversationSession


class ConversationSessionStore:
    """Process-local sessions keyed by conversation id."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, ConversationSession] = {}
        self._lock = Lock()

    def get_or_create(self, conversation_id: UUID | None) -> ConversationSession:
        with self._lock:
            if conversation_id is not None and conversation_id in self._sessions:
                return self._sessions[conversation_id]
            session = ConversationSession()
            if conversation_id is not None:
                session.session_id = conversation_id
            self._sessions[session.session_id] = session
            return session

    def save(self, session: ConversationSession) -> None:
        with self._lock:
            self._sessions[session.session_id] = session

    def clear(self) -> None:
        with self._lock:
            self._sessions.clear()


# Shared store for the API process
default_session_store = ConversationSessionStore()
