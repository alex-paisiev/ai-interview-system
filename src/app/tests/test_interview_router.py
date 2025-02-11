import asyncio
import importlib

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Reload modules for a clean state.
from app import agents, main

importlib.reload(agents)
importlib.reload(main)

from app.database import get_db
from app.main import app
from app.models import Base

# Use a file-based SQLite database for testing.
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
async_session_test = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


# Override the get_db dependency.
async def override_get_db():
    async with async_session_test() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# Use an async fixture for setting up and tearing down the database.
@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# --- Monkeypatch the Flow Module Functions ---
from app.agents import flow


async def dummy_generate_questions(job_description: str) -> list:
    return ["Question 1: Dummy?", "Question 2: Dummy?", "Question 3: Dummy?"]


async def dummy_evaluate_response(question: str, response_text: str) -> tuple:
    return (4, "Dummy evaluation")


@pytest.fixture(autouse=True)
def override_flow(monkeypatch):
    monkeypatch.setattr(flow, "generate_questions", dummy_generate_questions)
    monkeypatch.setattr(flow, "evaluate_response", dummy_evaluate_response)


# Reload the router module so that it picks up our monkeypatched functions.
importlib.reload(__import__("app.routers.interview", fromlist=[""]))


# Create an async client fixture using ASGITransport.
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# --- Tests for Endpoints ---


@pytest.mark.asyncio
async def test_start_interview(async_client: AsyncClient):
    payload = {"candidate_id": "1", "job_description": "Software Engineer"}
    response = await async_client.post("/interview/start", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "session_id" in data
    assert data["candidate_id"] == "1"
    assert data["job_description"] == "Software Engineer"
    expected_questions = [
        "Question 1: Dummy?",
        "Question 2: Dummy?",
        "Question 3: Dummy?",
    ]
    assert data["questions"] == expected_questions


@pytest.mark.asyncio
async def test_submit_responses(async_client: AsyncClient):
    # Create an interview session.
    start_payload = {"candidate_id": "1", "job_description": "Software Engineer"}
    start_response = await async_client.post("/interview/start", json=start_payload)
    assert start_response.status_code == 200, start_response.text
    start_data = start_response.json()
    session_id = start_data["session_id"]

    # Submit responses.
    submit_payload = {
        "session_id": session_id,
        "responses": ["Answer 1", "Answer 2", "Answer 3"],
    }
    submit_response = await async_client.post("/interview/submit", json=submit_payload)
    assert submit_response.status_code == 200, submit_response.text
    submit_data = submit_response.json()
    assert submit_data["session_id"] == session_id
    assert submit_data["candidate_id"] == "1"
    assert submit_data["overall_score"] == pytest.approx(4.0)
    assert submit_data["feedback"] == "Overall performance is satisfactory."
