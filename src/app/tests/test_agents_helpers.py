import pytest

from app.agents.helpers import (
    compute_overall_score,
    create_evaluation_prompt,
    create_questions_prompt,
    determine_feedback,
    parse_evaluation_result,
    parse_questions_response,
)


# --- Tests for create_questions_prompt ---
def test_create_questions_prompt():
    job_desc = "Software Engineer"
    prompt = create_questions_prompt(job_desc)
    expected_prompt = (
        "Generate 3 interview questions for a candidate applying for the role: Software Engineer. "
        "List each question on a new line."
    )
    assert prompt == expected_prompt


# --- Tests for parse_questions_response ---
def test_parse_questions_response():
    sample_response = """
    1. What is your experience with Python?
    2. How do you approach debugging?
    3. Describe your teamwork skills.
    """
    questions = parse_questions_response(sample_response)
    expected = [
        "1. What is your experience with Python?",
        "2. How do you approach debugging?",
        "3. Describe your teamwork skills.",
    ]
    # Verify that only the first three non-empty questions are returned.
    assert questions == expected


# --- Tests for create_evaluation_prompt ---
def test_create_evaluation_prompt():
    question = "What is your experience with Python?"
    response_text = "I have 5 years of experience."
    prompt = create_evaluation_prompt(question, response_text)
    # Ensure the prompt contains the necessary parts.
    assert "Evaluate the candidate's response" in prompt
    assert "Question: What is your experience with Python?" in prompt
    assert "Response: I have 5 years of experience." in prompt


# --- Tests for parse_evaluation_result ---
@pytest.mark.parametrize(
    "input_text, expected_score, expected_comment",
    [
        # Standard case: proper format.
        ("Score: 4, Comment: Good experience.", 4, "Good experience."),
        # Missing comment.
        ("Score: 5", 5, "No comment provided."),
        # Extra spaces and punctuation.
        ("Score:    3 , Comment:    Needs improvement.", 3, "Needs improvement."),
    ],
)
def test_parse_evaluation_result(input_text, expected_score, expected_comment):
    score, comment = parse_evaluation_result(input_text)
    assert score == expected_score
    assert comment == expected_comment


def test_parse_evaluation_result_invalid():
    # If parsing fails, default to 3 and error message.
    input_text = "Some invalid format"
    score, comment = parse_evaluation_result(input_text)
    assert score == 3
    assert comment == "Evaluation could not be parsed."


# --- Tests for compute_overall_score ---
def test_compute_overall_score():
    evaluations = [{"score": 4}, {"score": 5}, {"score": 3}]
    overall = compute_overall_score(evaluations)
    assert overall == pytest.approx(4.0)


# --- Tests for determine_feedback ---
@pytest.mark.parametrize(
    "overall_score, expected_feedback",
    [
        (4.0, "Overall performance is satisfactory."),
        (3.0, "Candidate may need further evaluation."),
        (3.5, "Overall performance is satisfactory."),
    ],
)
def test_determine_feedback(overall_score, expected_feedback):
    feedback = determine_feedback(overall_score)
    assert feedback == expected_feedback
