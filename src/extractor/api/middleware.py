"""Middlewares da API."""

import time
from collections import defaultdict
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from extractor.utils.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting simples em memória."""

    def __init__(
        self,
        app: ASGIApp,
        requests: int = 100,
        window: int = 60,
    ) -> None:
        super().__init__(app)
        self.requests = requests
        self.window = window
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Processa request com rate limiting."""
        client_ip = request.client.host if request.client else "unknown"

        now = time.time()
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if now - ts < self.window
        ]

        if len(self._requests[client_ip]) >= self.requests:
            logger.warning("rate_limit_exceeded", client_ip=client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Try again later.",
            )

        self._requests[client_ip].append(now)
        response = await call_next(request)

        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(
            self.requests - len(self._requests[client_ip])
        )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Loga request e response."""
        start_time = time.perf_counter()

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(process_time * 1000, 2),
        )

        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
        return response
