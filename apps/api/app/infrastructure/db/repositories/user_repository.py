"""SQLAlchemy implementation of UserRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import User
from app.infrastructure.db.mappers.user_mapper import apply_domain, to_domain
from app.infrastructure.db.models import User as UserModel
from app.infrastructure.db.repositories.base import SQLAlchemyRepository


class SqlAlchemyUserRepository(SQLAlchemyRepository[UserModel, UUID]):
    """Persist users through SQLAlchemy."""

    model = UserModel

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by identifier."""
        model = await self._session.get(UserModel, user_id)
        return to_domain(model) if model is not None else None

    async def get_by_email(self, email: str) -> User | None:
        """Fetch a user by unique email address."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.lower()),
        )
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def get_by_oauth_subject(
        self,
        auth_provider: str,
        oauth_subject: str,
    ) -> User | None:
        """Fetch a user by OAuth provider subject."""
        result = await self._session.execute(
            select(UserModel).where(
                UserModel.auth_provider == auth_provider,
                UserModel.oauth_subject == oauth_subject,
            ),
        )
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def add(self, user: User) -> User:
        """Persist a new user."""
        model = UserModel(
            id=user.id,
            email=user.email.lower(),
            hashed_password=user.hashed_password,
            display_name=user.display_name,
            is_active=user.is_active,
            role=user.role.value,
            auth_provider=user.auth_provider.value,
            oauth_subject=user.oauth_subject,
            locale=user.locale,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return to_domain(model)

    async def update(self, user: User) -> User:
        """Persist changes to an existing user."""
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise ValueError(f"User {user.id} not found")
        apply_domain(model, user)
        model.email = user.email.lower()
        await self._session.flush()
        await self._session.refresh(model)
        return to_domain(model)

    async def delete(self, user_id: UUID) -> bool:
        """Delete a user by identifier."""
        return await super().delete(user_id)
