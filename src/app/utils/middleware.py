# app/utils/middleware.py

import logging

from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

# Configure a logger for this module.
logger = logging.getLogger("app.middleware")


def add_middleware(app):
    # Add CORS middleware.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Register the log_requests middleware.
    app.middleware("http")(log_requests)


async def log_requests(request: Request, call_next):
    # Log the incoming request.
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    # Log the outgoing response.
    logger.info(
        f"Outgoing response: {response.status_code} for {request.method} {request.url}"
    )
    return response
