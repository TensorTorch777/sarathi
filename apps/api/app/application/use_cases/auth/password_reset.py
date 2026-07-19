"""Password reset placeholder — email delivery not implemented yet."""

from app.core.logging import get_logger
from app.domain.repositories import UserRepository

logger = get_logger(__name__)


class RequestPasswordResetUseCase:
    """Accept a password-reset request without revealing account existence."""

    def __init__(self, *, users: UserRepository) -> None:
        self._users = users

    async def execute(self, email: str) -> dict[str, str]:
        """Acknowledge a reset request.

        Does not send email yet. Always returns a neutral message to avoid
        email enumeration. Token generation and mail delivery are future work.
        """
        normalized = email.strip().lower()
        user = await self._users.get_by_email(normalized)
        if user is not None:
            logger.info("password_reset_requested_placeholder", user_id=str(user.id))
        else:
            logger.info("password_reset_requested_unknown_email")

        return {
            "status": "accepted",
            "message": (
                "If an account exists for this email, password reset instructions "
                "will be sent. Email delivery is not enabled yet."
            ),
        }
