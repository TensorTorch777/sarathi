"""Conversation state machine for progressive disclosure + journeys."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4


class TurnState(StrEnum):
    """Ordered conversation states — no skipping."""

    START = "START"
    UNDERSTAND = "UNDERSTAND"
    RETRIEVE = "RETRIEVE"
    RESPOND_L1 = "RESPOND_L1"
    WAIT = "WAIT"
    RESPOND_L2 = "RESPOND_L2"
    RESPOND_L3 = "RESPOND_L3"
    JOURNEY_STEP = "JOURNEY_STEP"
    END = "END"


class ResponseLevel(StrEnum):
    """Progressive disclosure depth."""

    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class JourneyStatus(StrEnum):
    """Journey lifecycle within a single conversation (not long-term memory)."""

    NONE = "none"
    OFFERED = "offered"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXITED = "exited"


# Valid transitions (current → allowed next)
_TRANSITIONS: dict[TurnState, frozenset[TurnState]] = {
    TurnState.START: frozenset({TurnState.UNDERSTAND}),
    TurnState.UNDERSTAND: frozenset({TurnState.RETRIEVE}),
    TurnState.RETRIEVE: frozenset({TurnState.RESPOND_L1}),
    TurnState.RESPOND_L1: frozenset({TurnState.WAIT, TurnState.END}),
    TurnState.WAIT: frozenset(
        {
            TurnState.RESPOND_L2,
            TurnState.RESPOND_L3,
            TurnState.JOURNEY_STEP,
            TurnState.UNDERSTAND,  # new topic / new question
            TurnState.END,
        }
    ),
    TurnState.RESPOND_L2: frozenset({TurnState.WAIT, TurnState.END}),
    TurnState.RESPOND_L3: frozenset({TurnState.WAIT, TurnState.END}),
    TurnState.JOURNEY_STEP: frozenset({TurnState.WAIT, TurnState.END, TurnState.JOURNEY_STEP}),
    TurnState.END: frozenset({TurnState.START, TurnState.UNDERSTAND}),
}


@dataclass
class ConversationSession:
    """In-memory session for progressive disclosure + journey progress."""

    session_id: UUID = field(default_factory=uuid4)
    state: TurnState = TurnState.START
    response_level: ResponseLevel | None = None
    intent: str | None = None
    primary_node_id: str | None = None
    primary_family_id: str | None = None
    retrieved_node_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    followup_asked: bool = False
    last_user_message: str | None = None
    turn_count: int = 0
    # Journey (conversation-scoped only)
    journey_status: JourneyStatus = JourneyStatus.NONE
    offered_journey_id: str | None = None
    active_journey_id: str | None = None
    journey_step_index: int = 0
    journey_completed_steps: list[int] = field(default_factory=list)
    journey_select_reason: str | None = None

    def advance(self, next_state: TurnState) -> None:
        """Move to next state if transition is allowed."""
        allowed = _TRANSITIONS.get(self.state, frozenset())
        if next_state not in allowed:
            msg = f"Illegal transition {self.state} → {next_state}"
            raise ValueError(msg)
        self.state = next_state

    def clear_journey(self) -> None:
        self.journey_status = JourneyStatus.NONE
        self.offered_journey_id = None
        self.active_journey_id = None
        self.journey_step_index = 0
        self.journey_completed_steps = []
        self.journey_select_reason = None

    def reset_for_new_topic(self) -> None:
        """Begin a fresh UNDERSTAND cycle without destroying session id."""
        self.state = TurnState.START
        self.response_level = None
        self.intent = None
        self.primary_node_id = None
        self.primary_family_id = None
        self.retrieved_node_ids = []
        self.confidence = 0.0
        self.followup_asked = False
        self.clear_journey()
        self.advance(TurnState.UNDERSTAND)
