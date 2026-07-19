"""Long-term memory API — goals, favorites, journals, reflections, recall."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Query, Response
from sqlalchemy import select

from app.api.v1.deps import CurrentUserDep
from app.api.v1.schemas.memory import (
    CareerGoalCreateRequest,
    CareerGoalResponse,
    ConversationSummaryRequest,
    FavoriteVerseCreateRequest,
    FavoriteVerseResponse,
    JournalCreateRequest,
    JournalResponse,
    MemoryCreateRequest,
    MemoryItemResponse,
    MemoryRecallRequest,
    RecalledMemoryResponse,
    ReflectionCreateRequest,
    ReflectionResponse,
)
from app.application.dto.memory import UpsertMemoryCommand
from app.core.di.providers import DbSessionDep, SettingsDep
from app.core.errors import AppError, ForbiddenError, NotFoundError
from app.domain.entities.journal import Journal
from app.domain.entities.reflection import Reflection
from app.domain.enums.memory_kind import MemoryKind
from app.infrastructure.db.models.career_goal import CareerGoal as CareerGoalModel
from app.infrastructure.db.models.favorite_verse import FavoriteVerse as FavoriteVerseModel
from app.infrastructure.db.models.verse import Verse as VerseModel
from app.infrastructure.db.repositories.journal_repository import SqlAlchemyJournalRepository
from app.infrastructure.db.repositories.memory_repository import SqlAlchemyMemoryRepository
from app.infrastructure.db.repositories.reflection_repository import (
    SqlAlchemyReflectionRepository,
)
from app.infrastructure.memory.factory import (
    build_index_memory_use_case,
    build_recall_memory_use_case,
)
from app.infrastructure.vector.memory_store import QdrantMemoryStore

router = APIRouter(prefix="/memory")


def _item_response(item) -> MemoryItemResponse:
    return MemoryItemResponse(
        id=item.id,
        kind=item.kind,
        title=item.title,
        content=item.content,
        source_id=item.source_id,
        metadata=dict(item.metadata),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


@router.get("/items", response_model=list[MemoryItemResponse])
async def list_memory_items(
    user: CurrentUserDep,
    session: DbSessionDep,
    kind: MemoryKind | None = None,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[MemoryItemResponse]:
    """List the user's long-term memory items."""
    repo = SqlAlchemyMemoryRepository(session)
    items = await repo.list_by_user(user.id, kind=kind, limit=limit)
    return [_item_response(i) for i in items]


@router.post("/items", response_model=MemoryItemResponse, status_code=201)
async def create_memory_item(
    body: MemoryCreateRequest,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> MemoryItemResponse:
    """Create a free-form memory note and index it in Qdrant."""
    indexer = build_index_memory_use_case(session=session, settings=settings)
    item = await indexer.execute(
        UpsertMemoryCommand(
            user_id=user.id,
            kind=body.kind,
            title=body.title,
            content=body.content,
            source_id=body.source_id,
            metadata=body.metadata,
        ),
    )
    await session.commit()
    return _item_response(item)


@router.delete("/items/{memory_id}")
async def delete_memory_item(
    memory_id: str,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> Response:
    """Delete a memory item from Postgres and Qdrant."""
    from uuid import UUID

    mid = UUID(memory_id)
    repo = SqlAlchemyMemoryRepository(session)
    item = await repo.get_by_id(mid)
    if item is None or item.user_id != user.id:
        raise NotFoundError("Memory item not found")
    if item.qdrant_point_id:
        store = QdrantMemoryStore(settings)
        try:
            await store.delete(item.qdrant_point_id)
        except Exception:  # noqa: BLE001
            pass
    await repo.delete(mid)
    await session.commit()
    return Response(status_code=204)


@router.post("/recall", response_model=list[RecalledMemoryResponse])
async def recall_memories(
    body: MemoryRecallRequest,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> list[RecalledMemoryResponse]:
    """Semantic recall over the user's vector memory."""
    if not settings.memory_enabled:
        raise AppError("Memory is disabled", code="memory_disabled", status_code=503)
    recall = build_recall_memory_use_case(session=session, settings=settings)
    hits = await recall.execute(
        user_id=user.id,
        query=body.query,
        top_k=body.top_k,
        kinds=body.kinds,
    )
    return [
        RecalledMemoryResponse(
            memory_id=h.memory_id,
            kind=h.kind,
            title=h.title,
            content=h.content,
            score=h.score,
            source_id=h.source_id,
            metadata=h.metadata,
        )
        for h in hits
    ]


@router.post("/goals", response_model=CareerGoalResponse, status_code=201)
async def create_career_goal(
    body: CareerGoalCreateRequest,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> CareerGoalResponse:
    """Save a career goal and index it for long-term recall."""
    goal_id = uuid4()
    indexer = build_index_memory_use_case(session=session, settings=settings)
    memory = await indexer.execute(
        UpsertMemoryCommand(
            user_id=user.id,
            kind=MemoryKind.CAREER_GOAL,
            title=body.title,
            content=body.description,
            source_id=goal_id,
            metadata={"status": body.status},
        ),
    )
    now = datetime.now(UTC)
    model = CareerGoalModel(
        id=goal_id,
        user_id=user.id,
        title=body.title,
        description=body.description,
        status=body.status,
        memory_item_id=memory.id,
        created_at=now,
        updated_at=now,
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return CareerGoalResponse(
        id=model.id,
        title=model.title,
        description=model.description,
        status=model.status,
        memory_item_id=model.memory_item_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


@router.get("/goals", response_model=list[CareerGoalResponse])
async def list_career_goals(
    user: CurrentUserDep,
    session: DbSessionDep,
) -> list[CareerGoalResponse]:
    """List career goals for the current user."""
    result = await session.execute(
        select(CareerGoalModel)
        .where(CareerGoalModel.user_id == user.id)
        .order_by(CareerGoalModel.updated_at.desc()),
    )
    rows = result.scalars().all()
    return [
        CareerGoalResponse(
            id=r.id,
            title=r.title,
            description=r.description,
            status=r.status,
            memory_item_id=r.memory_item_id,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]


@router.post("/favorites", response_model=FavoriteVerseResponse, status_code=201)
async def add_favorite_verse(
    body: FavoriteVerseCreateRequest,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> FavoriteVerseResponse:
    """Mark a verse as favorite and index the personal note + citation."""
    verse = await session.get(VerseModel, body.verse_id)
    if verse is None:
        raise NotFoundError("Verse not found")

    existing = await session.execute(
        select(FavoriteVerseModel).where(
            FavoriteVerseModel.user_id == user.id,
            FavoriteVerseModel.verse_id == body.verse_id,
        ),
    )
    if existing.scalar_one_or_none() is not None:
        raise AppError("Verse already favorited", code="already_favorited", status_code=409)

    fav_id = uuid4()
    citation = f"BG {verse.chapter}.{verse.verse_number}"
    content = (
        f"Favorite verse {citation}: {verse.translation}"
        + (f"\nPersonal note: {body.note}" if body.note else "")
    )
    indexer = build_index_memory_use_case(session=session, settings=settings)
    memory = await indexer.execute(
        UpsertMemoryCommand(
            user_id=user.id,
            kind=MemoryKind.FAVORITE_VERSE,
            title=citation,
            content=content,
            source_id=fav_id,
            metadata={"verse_id": str(verse.id), "citation": citation},
        ),
    )
    now = datetime.now(UTC)
    model = FavoriteVerseModel(
        id=fav_id,
        user_id=user.id,
        verse_id=body.verse_id,
        note=body.note,
        memory_item_id=memory.id,
        created_at=now,
        updated_at=now,
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return FavoriteVerseResponse(
        id=model.id,
        verse_id=model.verse_id,
        note=model.note,
        memory_item_id=model.memory_item_id,
        citation=citation,
        translation=verse.translation,
        created_at=model.created_at,
    )


@router.get("/favorites", response_model=list[FavoriteVerseResponse])
async def list_favorite_verses(
    user: CurrentUserDep,
    session: DbSessionDep,
) -> list[FavoriteVerseResponse]:
    """List favorited verses."""
    result = await session.execute(
        select(FavoriteVerseModel, VerseModel)
        .join(VerseModel, VerseModel.id == FavoriteVerseModel.verse_id)
        .where(FavoriteVerseModel.user_id == user.id)
        .order_by(FavoriteVerseModel.created_at.desc()),
    )
    rows = result.all()
    return [
        FavoriteVerseResponse(
            id=fav.id,
            verse_id=fav.verse_id,
            note=fav.note,
            memory_item_id=fav.memory_item_id,
            citation=f"BG {verse.chapter}.{verse.verse_number}",
            translation=verse.translation,
            created_at=fav.created_at,
        )
        for fav, verse in rows
    ]


@router.post("/journals", response_model=JournalResponse, status_code=201)
async def create_journal(
    body: JournalCreateRequest,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> JournalResponse:
    """Create a journal entry and index it into vector memory."""
    now = datetime.now(UTC)
    journal = Journal(
        id=uuid4(),
        user_id=user.id,
        title=body.title,
        content=body.content,
        mood_note=body.mood_note,
        created_at=now,
        updated_at=now,
    )
    repo = SqlAlchemyJournalRepository(session)
    saved = await repo.add(journal)
    indexer = build_index_memory_use_case(session=session, settings=settings)
    await indexer.execute(
        UpsertMemoryCommand(
            user_id=user.id,
            kind=MemoryKind.JOURNAL,
            title=saved.title or "Journal entry",
            content=saved.content,
            source_id=saved.id,
            metadata={"mood_note": saved.mood_note},
        ),
    )
    await session.commit()
    return JournalResponse(
        id=saved.id,
        title=saved.title,
        content=saved.content,
        mood_note=saved.mood_note,
        created_at=saved.created_at,
        updated_at=saved.updated_at,
    )


@router.get("/journals", response_model=list[JournalResponse])
async def list_journals(
    user: CurrentUserDep,
    session: DbSessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[JournalResponse]:
    """List journal entries."""
    repo = SqlAlchemyJournalRepository(session)
    rows = await repo.list_by_user(user.id, limit=limit)
    return [
        JournalResponse(
            id=j.id,
            title=j.title,
            content=j.content,
            mood_note=j.mood_note,
            created_at=j.created_at,
            updated_at=j.updated_at,
        )
        for j in rows
    ]


@router.post("/reflections", response_model=ReflectionResponse, status_code=201)
async def create_reflection(
    body: ReflectionCreateRequest,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> ReflectionResponse:
    """Create a personal reflection and index it."""
    journals = SqlAlchemyJournalRepository(session)
    journal = await journals.get_by_id(body.journal_id)
    if journal is None or journal.user_id != user.id:
        raise ForbiddenError("Journal not found for this user")

    now = datetime.now(UTC)
    reflection = Reflection(
        id=uuid4(),
        journal_id=body.journal_id,
        user_id=user.id,
        verse_id=body.verse_id,
        content=body.content,
        created_at=now,
        updated_at=now,
    )
    repo = SqlAlchemyReflectionRepository(session)
    saved = await repo.add(reflection)
    indexer = build_index_memory_use_case(session=session, settings=settings)
    await indexer.execute(
        UpsertMemoryCommand(
            user_id=user.id,
            kind=MemoryKind.REFLECTION,
            title="Personal reflection",
            content=saved.content,
            source_id=saved.id,
            metadata={
                "journal_id": str(saved.journal_id),
                "verse_id": str(saved.verse_id) if saved.verse_id else None,
            },
        ),
    )
    await session.commit()
    return ReflectionResponse(
        id=saved.id,
        journal_id=saved.journal_id,
        verse_id=saved.verse_id,
        content=saved.content,
        created_at=saved.created_at,
    )


@router.get("/reflections", response_model=list[ReflectionResponse])
async def list_reflections(
    user: CurrentUserDep,
    session: DbSessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[ReflectionResponse]:
    """List personal reflections."""
    repo = SqlAlchemyReflectionRepository(session)
    rows = await repo.list_by_user(user.id, limit=limit)
    return [
        ReflectionResponse(
            id=r.id,
            journal_id=r.journal_id,
            verse_id=r.verse_id,
            content=r.content,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.post("/conversations/summary", response_model=MemoryItemResponse, status_code=201)
async def save_conversation_summary(
    body: ConversationSummaryRequest,
    user: CurrentUserDep,
    session: DbSessionDep,
    settings: SettingsDep,
) -> MemoryItemResponse:
    """Store a conversation summary in vector memory for future recall."""
    source_id = body.conversation_id or uuid4()
    preview = "\n".join(f"- {m}" for m in body.messages_preview[:20])
    content = body.summary.strip()
    if preview:
        content = f"{content}\n\nKey moments:\n{preview}"

    indexer = build_index_memory_use_case(session=session, settings=settings)
    item = await indexer.execute(
        UpsertMemoryCommand(
            user_id=user.id,
            kind=MemoryKind.CONVERSATION_SUMMARY,
            title=body.title or "Conversation summary",
            content=content,
            source_id=source_id,
            metadata={
                "conversation_id": str(source_id),
                "kind": MemoryKind.CONVERSATION.value,
            },
        ),
    )
    await session.commit()
    return _item_response(item)
