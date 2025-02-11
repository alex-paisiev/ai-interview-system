import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import interview
from app.utils.middleware import add_middleware

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Add shutdown logic if necessary.


app = FastAPI(title="AI-Driven Interview System", lifespan=lifespan)

app.include_router(interview.router)
add_middleware(app)
