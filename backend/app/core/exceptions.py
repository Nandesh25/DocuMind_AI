"""Domain-level exceptions mapped to HTTP responses by the global handlers."""


class AppException(Exception):
    """Base application exception."""

    status_code: int = 400
    code: str = "APP_ERROR"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.__doc__ or "Application error"
        super().__init__(self.detail)


class NotFoundError(AppException):
    """Requested resource was not found."""

    status_code = 404
    code = "NOT_FOUND"


class ConflictError(AppException):
    """Resource conflict."""

    status_code = 409
    code = "CONFLICT"


class UnauthorizedError(AppException):
    """Authentication required or failed."""

    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(AppException):
    """Insufficient permissions for this action."""

    status_code = 403
    code = "FORBIDDEN"


class ValidationError(AppException):
    """Business validation failed."""

    status_code = 422
    code = "VALIDATION_ERROR"


class ServiceUnavailableError(AppException):
    """A downstream AI service is unavailable."""

    status_code = 503
    code = "SERVICE_UNAVAILABLE"
