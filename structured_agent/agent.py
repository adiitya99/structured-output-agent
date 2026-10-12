
import logging
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from structured_agent.schemas import TaskResult


logger = logging.getLogger("structured_agent")


class AgentError(Exception):
    """Base exception for agent failures."""


class MaxRetriesExceeded(AgentError):
    """Raised when all validation attempts fail."""


def validate_with_retry(
    response_generator: Callable[[str | None], dict[str, Any]],
    max_attempts: int = 3,
) -> TaskResult:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    feedback = None

    for attempt in range(1, max_attempts + 1):
        logger.info("Starting attempt %s/%s", attempt, max_attempts)

        try:
            raw_response = response_generator(feedback)
        except AgentError:
            raise
        except Exception as error:
            logger.exception("Response generation failed")
            raise AgentError(
                "Could not generate an agent response."
            ) from error

        try:
            result = TaskResult.model_validate(raw_response)
        except ValidationError as error:
            feedback = str(error)

            logger.warning(
                "Schema validation failed on attempt %s/%s",
                attempt,
                max_attempts,
            )

            if attempt == max_attempts:
                raise MaxRetriesExceeded(
                    f"Response validation failed after {max_attempts} attempts."
                ) from error

            continue

        logger.info("Schema validation succeeded on attempt %s", attempt)
        return result

    raise MaxRetriesExceeded("No valid response was generated.")


