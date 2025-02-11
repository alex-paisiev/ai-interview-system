import importlib

import pytest

from app.agents import flow


# Ensure the flow module is reloaded before each test.
@pytest.fixture(autouse=True)
def reload_flow_module():
    importlib.reload(flow)


@pytest.mark.asyncio
async def test_generate_questions(monkeypatch):
    dummy_questions_response = (
        "1. What is your experience with Python?\n"
        "2. How do you approach debugging?\n"
        "3. Describe your teamwork experience."
    )

    async def dummy_call_api(prompt: str) -> str:
        return dummy_questions_response

    monkeypatch.setattr(flow, "call_OpenAI_API", dummy_call_api)

    job_description = "Software Engineer"
    questions = await flow.generate_questions(job_description)

    expected_questions = [
        "1. What is your experience with Python?",
        "2. How do you approach debugging?",
        "3. Describe your teamwork experience.",
    ]
    assert questions == expected_questions


@pytest.mark.asyncio
async def test_evaluate_response(monkeypatch):
    dummy_evaluation_response = "Score: 4, Comment: Good job."

    async def dummy_call_api(prompt: str) -> str:
        return dummy_evaluation_response

    monkeypatch.setattr(flow, "call_OpenAI_API", dummy_call_api)

    question = "What is your experience with Python?"
    candidate_response = "I have been programming in Python for 5 years."
    score, comment = await flow.evaluate_response(question, candidate_response)

    assert score == 4
    assert comment == "Good job."


@pytest.mark.asyncio
async def test_validate_scores():
    evaluations = [
        {"score": 4, "comment": "Good."},
        {"score": 3, "comment": "Okay."},
        {"score": 5, "comment": "Excellent."},
    ]
    feedback, overall_score = await flow.validate_scores(evaluations)

    assert overall_score == pytest.approx(4.0)
    assert feedback == "Overall performance is satisfactory."
