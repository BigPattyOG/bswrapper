from __future__ import annotations

from typing import Optional


class APIError(Exception):
    def __init__(
        self, status_code: int, message: str, *, response_text: Optional[str] = None
    ) -> None:
        super().__init__(f"API Error: {status_code} - {message}")
        self.status_code: int = status_code
        self.response_text: Optional[str] = response_text


class NotFound(APIError):
    pass


class Unauthorized(APIError):
    pass


class RateLimited(APIError):
    def __init__(
        self, status_code: int, message: str, retry_after: Optional[float]
    ) -> None:
        super().__init__(status_code, message)
        self.retry_after: Optional[float] = retry_after
