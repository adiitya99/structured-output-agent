from structured_agent.agent import validate_with_retry
import pytest
from pydantic import ValidationError

from structured_agent.schemas import TaskResult
from structured_agent.tools import run_tool
from structured_agent.agent import AgentError, MaxRetriesExceeded

def test_valid_task_result():
    result = TaskResult(
        summary="Study plan",
        category="study",
        confidence=0.9,
        next_steps=["Revise notes"],
    )
    assert result.confidence == 0.9


def test_invalid_confidence():
    with pytest.raises(ValidationError):
        TaskResult(
            summary="Study plan",
            category="study",
            confidence=1.5,
        )


def test_valid_calculator_tool():
    result = run_tool({"a": 10, "b": 20})
    assert result.total == 30


def test_invalid_calculator_input():
    with pytest.raises(ValidationError):
        run_tool({"a": 10, "b": "hello"})


def test_extra_calculator_argument():
    with pytest.raises(ValidationError):
        run_tool({"a": 10, "b": 20, "admin": True})


def test_agent_retries_after_invalid_response():
    responses = [
        {
            "summary": "Bad result",
            "category": "study",
            "confidence": 1.5,
        },
        {
            "summary": "Good result",
            "category": "study",
            "confidence": 0.9,
        },
    ]
    received_feedback = []

    def fake_ai(feedback):
        received_feedback.append(feedback)
        return responses.pop(0)

    result = validate_with_retry(fake_ai)

    assert result.confidence == 0.9
    assert len(received_feedback) == 2
    assert received_feedback[0] is None
    assert received_feedback[1] is not None



def test_agent_stops_after_max_attempts():
    def always_invalid(feedback):
        return {
            "summary": "Bad result",
            "category": "study",
            "confidence": 2.0,
        }

    with pytest.raises(MaxRetriesExceeded):
        validate_with_retry(always_invalid, max_attempts=2)


def test_agent_does_not_retry_unexpected_error():
    attempts = 0

    def failing_generator(feedback):
        nonlocal attempts
        attempts += 1
        raise TimeoutError("Simulated timeout")

    with pytest.raises(AgentError):
        validate_with_retry(failing_generator, max_attempts=3)

    assert attempts == 1


def test_zero_attempts_are_rejected():
    with pytest.raises(ValueError):
        validate_with_retry(lambda feedback: {}, max_attempts=0)


from main import mock_response


def test_mock_response_becomes_valid_after_retry():
    first_response = mock_response(None)
    assert first_response["confidence"] == 1.5

    second_response = mock_response("Previous validation error")
    result = TaskResult.model_validate(second_response)

    assert result.confidence == 0.95
    assert result.summary == "Study networking fundamentals"


        
def test_blank_summary_is_rejected():
    with pytest.raises(ValidationError):
        TaskResult(
            summary="   ",
            category="study",
            confidence=0.9,
        )


def test_string_confidence_is_rejected():
    with pytest.raises(ValidationError):
        TaskResult(
            summary="Study plan",
            category="study",
            confidence="0.9",
        )


def test_more_than_five_steps_is_rejected():
    with pytest.raises(ValidationError):
        TaskResult(
            summary="Study plan",
            category="study",
            confidence=0.9,
            next_steps=[
                "Step 1",
                "Step 2",
                "Step 3",
                "Step 4",
                "Step 5",
                "Step 6",
            ],
        )


def test_summary_whitespace_is_trimmed():
    result = TaskResult(
        summary="  Study plan  ",
        category="study",
        confidence=0.9,
    )

    assert result.summary == "Study plan"

