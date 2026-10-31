from __future__ import annotations


class SafeSesiError(Exception):
    """Base exception for SafeSesi application errors."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(SafeSesiError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ForbiddenError(SafeSesiError):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status_code=403)


class ConflictError(SafeSesiError):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)


class LLMServiceError(SafeSesiError):
    def __init__(self, message: str = "Layanan AI klien virtual sedang tidak dapat merespons. Silakan coba kembali."):
        super().__init__(message, status_code=503)

