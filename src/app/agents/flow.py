import logging
import os
from typing import List, Tuple

from openai import AsyncOpenAI

from app.agents.helpers import (
    compute_overall_score,
    create_evaluation_prompt,
    create_questions_prompt,
    determine_feedback,
    parse_evaluation_result,
    parse_questions_response,
)

LOGGER = logging.getLogger(__name__)


async def call_OpenAI_API(prompt: str) -> str:
    """
    Call the OpenAI API with the given prompt and return the raw text response.
    """

    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
    OPENAI_MODEL_MAX_TOKENS = int(os.environ.get("OPENAI_MODEL_MAX_TOKENS", 100))
    OPENAI_MODEL_TEMPERATURE = float(os.environ.get("OPENAI_MODEL_TEMPERATURE", 0.7))

    client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    response = await client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[{"role": "system", "content": prompt}],
        max_tokens=OPENAI_MODEL_MAX_TOKENS,
        temperature=OPENAI_MODEL_TEMPERATURE,
    )
    # Assuming the API response has this structure
    result_text = response.choices[0].message.content
    LOGGER.debug("Raw API response: %s", result_text)
    return result_text


async def generate_questions(job_description: str) -> List[str]:
    """
    Generate interview questions for a candidate applying for the given job.

    Steps:
    1. Create a prompt based on the job description.
    2. Call the AI API using the prompt.
    3. Parse the raw API response into a list of questions.
    """
    prompt = create_questions_prompt(job_description)
    LOGGER.debug("Generated prompt: %s", prompt)
    raw_response = await call_OpenAI_API(prompt)
    return parse_questions_response(raw_response)


async def evaluate_response(question: str, response_text: str) -> Tuple[int, str]:
    """
    Evaluate the candidate's response by:
      1. Creating a prompt.
      2. Calling the AI evaluation API.
      3. Parsing the API response.

    Returns a tuple of (score, comment).
    """
    prompt = create_evaluation_prompt(question, response_text)
    LOGGER.debug("Evaluation prompt: %s", prompt)

    result_text = await call_OpenAI_API(prompt)
    return parse_evaluation_result(result_text)


async def validate_scores(evaluations: List[dict]) -> Tuple[str, float]:
    """
    Validate a list of evaluations by computing an overall score and determining feedback.

    Returns a tuple of (feedback, overall_score).
    """
    overall_score = compute_overall_score(evaluations)
    feedback = determine_feedback(overall_score)
    return feedback, overall_score
