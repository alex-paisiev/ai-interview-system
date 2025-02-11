from typing import List

from pydantic import BaseModel


class StartInterviewRequest(BaseModel):
    candidate_id: str
    job_description: str


class StartInterviewResponse(BaseModel):
    session_id: str
    candidate_id: str
    job_description: str
    questions: List[str]


class SubmitResponses(BaseModel):
    session_id: str
    responses: List[str]


class SubmitResponsesResponse(BaseModel):
    session_id: str
    candidate_id: str
    feedback: str
    overall_score: float
