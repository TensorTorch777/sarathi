"""SQLAlchemy ORM models.

Import all models here so Alembic autogenerate discovers metadata.
"""

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.associations import JournalEmotion, MessageEmotion, MessageVerse
from app.infrastructure.db.models.career_goal import CareerGoal
from app.infrastructure.db.models.conversation import Conversation
from app.infrastructure.db.models.emotion import Emotion
from app.infrastructure.db.models.favorite_verse import FavoriteVerse
from app.infrastructure.db.models.feedback import Feedback
from app.infrastructure.db.models.journal import Journal
from app.infrastructure.db.models.memory_item import MemoryItem
from app.infrastructure.db.models.message import Message
from app.infrastructure.db.models.prompt_log import PromptLog
from app.infrastructure.db.models.reflection import Reflection
from app.infrastructure.db.models.user import User
from app.infrastructure.db.models.verse import Verse

__all__ = [
    "Base",
    "User",
    "Conversation",
    "Message",
    "Verse",
    "Emotion",
    "Journal",
    "Reflection",
    "Feedback",
    "PromptLog",
    "MemoryItem",
    "CareerGoal",
    "FavoriteVerse",
    "MessageVerse",
    "MessageEmotion",
    "JournalEmotion",
]
