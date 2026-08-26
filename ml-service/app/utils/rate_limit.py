from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request


class InMemoryRateLimiter:
    """Small deployment-safe baseline; use Redis for shared limits at scale."""

    def __init__(self, limit: int = 20, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, request: Request) -> None:
        client_id = request.client.host if request.client else "unknown"
        now = monotonic()
        window = self.requests[client_id]
        while window and window[0] <= now - self.window_seconds:
            window.popleft()
        if len(window) >= self.limit:
            raise HTTPException(status_code=429, detail="Too many requests. Please wait a minute and try again.")
        window.append(now)
