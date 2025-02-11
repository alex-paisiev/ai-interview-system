import logging
from typing import List, Tuple

LOGGER = logging.getLogger(__name__)


def create_questions_prompt(job_description: str) -> str:
    """
    Create a prompt to generate interview questions for a given job description.
    """
    return (
        f"Generate 3 interview questions for a candidate applying for the role: {job_description}. "
        "List each question on a new line."
    )


def parse_questions_response(questions_str: str) -> List[str]:
    """
    Parse the raw response string into a list of questions.
    """
    LOGGER.info("Raw questions response: %s", questions_str)
    questions_list = [q.strip() for q in questions_str.split("\n") if q.strip()]
    return questions_list[:3]


def create_evaluation_prompt(question: str, response_text: str) -> str:
    """
    Create the prompt to send to the AI for evaluating a candidate's response.
    """
    prompt = (
        f"Evaluate the candidate's response to the following question:\n"
        f"Question: {question}\nResponse: {response_text}\n\n"
        "Return a score between 1 (poor) and 5 (excellent) and a brief comment in the format:\n"
        "Score: <score>, Comment: <comment>"
    )
    return prompt


def parse_evaluation_result(result_text: str) -> Tuple[int, str]:
    """
    Parse the result text from the AI response and extract the score and comment.
    Returns a tuple (score, comment).
    """
    try:
        parts = result_text.split(",")
        # Extract the score portion (assumes format "Score: <score>")
        score_str = parts[0].split(":", 1)[1].strip()
        score = int(score_str)
        # Extract the comment portion (assumes format "Comment: <comment>")
        if len(parts) > 1:
            comment = parts[1].split(":", 1)[1].strip()
        else:
            comment = "No comment provided."
    except Exception as e:
        LOGGER.error("Error parsing evaluation result: %s", e)
        score = 3  # default score if parsing fails
        comment = "Evaluation could not be parsed."
    return score, comment


def compute_overall_score(evaluations: List[dict]) -> float:
    """
    Compute the overall average score from a list of evaluation dictionaries.
    Each dictionary is expected to have a key "score".
    """
    total_score = sum(eval_item["score"] for eval_item in evaluations)
    return total_score / len(evaluations)


def determine_feedback(overall_score: float) -> str:
    """
    Determine feedback based on the overall score.
    """
    if overall_score >= 3.5:
        return "Overall performance is satisfactory."
    else:
        return "Candidate may need further evaluation."
