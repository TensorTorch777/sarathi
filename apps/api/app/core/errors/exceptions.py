"""Domain and application exception hierarchy."""


class AppError(Exception):
    """Base application error with an HTTP-friendly code and message."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "app_error",
        status_code: int = 400,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found",
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, code="not_found", status_code=404, details=details)


class ValidationAppError(AppError):
    """Raised for application-level validation failures."""

    def __init__(
        self,
        message: str = "Validation failed",
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, code="validation_error", status_code=422, details=details)


class UnauthorizedError(AppError):
    """Raised when authentication is missing or invalid."""

    def __init__(
        self,
        message: str = "Unauthorized",
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, code="unauthorized", status_code=401, details=details)


class ForbiddenError(AppError):
    """Raised when the caller lacks permission."""

    def __init__(
        self,
        message: str = "Forbidden",
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, code="forbidden", status_code=403, details=details)


class ConflictError(AppError):
    """Raised when a resource conflicts with existing state."""

    def __init__(
        self,
        message: str = "Conflict",
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message, code="conflict", status_code=409, details=details)


class NotImplementedAppError(AppError):
    """Raised for intentionally unimplemented features (placeholders)."""

    def __init__(
        self,
        message: str = "Not implemented",
        *,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            code="not_implemented",
            status_code=501,
            details=details,
        )
