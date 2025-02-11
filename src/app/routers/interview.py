import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.agents import flow 
from app.database import get_db
from app.models import InterviewSession
from app.schemas import (
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitResponses,
    SubmitResponsesResponse,
)

LOGGER = logging.getLogger(__name__)
router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start", response_model=StartInterviewResponse)
async def start_interview(
    data: StartInterviewRequest, db: AsyncSession = Depends(get_db)
):
    questions = await flow.generate_questions(data.job_description)
    LOGGER.debug("Generated questions: %s", questions)

    # Build the initial session data dictionary.
    session_data = {
        "candidate_id": data.candidate_id,
        "job_description": data.job_description,
        "questions": questions,
        "responses": [],
        "evaluations": [],
    }

    session_id = str(uuid.uuid4())

    # Create and persist the InterviewSession record.
    interview_session = InterviewSession(
        id=session_id,
        candidate_id=data.candidate_id,
        job_title=data.job_description,
        session_data=session_data,
    )
    db.add(interview_session)
    await db.commit()

    # Return a response containing the session details.
    return StartInterviewResponse(
        session_id=session_id,
        candidate_id=data.candidate_id,
        job_description=data.job_description,
        questions=questions,
    )


@router.post("/submit", response_model=SubmitResponsesResponse)
async def submit_responses(data: SubmitResponses, db: AsyncSession = Depends(get_db)):
    # Retrieve the InterviewSession record from the database.
    result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == data.session_id)
    )
    session_record = result.scalar_one_or_none()
    if session_record is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    LOGGER.info("Session record found: %s", session_record)
    context = session_record.session_data
    LOGGER.info("Session context: %s", context)

    # Ensure the number of responses matches the number of questions.
    questions = context.get("questions", [])
    if len(data.responses) != len(questions):
        raise HTTPException(
            status_code=400,
            detail="Number of responses does not match the number of questions.",
        )

    evaluations = []
    # For each question-response pair, evaluate the response.
    for question, response_text in zip(questions, data.responses):
        score, comment = await flow.evaluate_response(question, response_text)
        evaluations.append(
            {
                "question": question,
                "response": response_text,
                "score": score,
                "comment": comment,
            }
        )

    # Validate the evaluations to get overall feedback and score.
    feedback, overall_score = await flow.validate_scores(evaluations)

    # Update the session record with the responses, evaluations, and feedback.
    context["responses"] = data.responses
    context["evaluations"] = evaluations
    context["feedback"] = feedback
    context["overall_score"] = overall_score
    session_record.session_data = context
    await db.commit()

    return SubmitResponsesResponse(
        session_id=data.session_id,
        candidate_id=context.get("candidate_id"),
        feedback=feedback,
        overall_score=overall_score,
    )
