
import logging

from pydantic import ValidationError
from schemas import TaskResult

logging.getLogger().setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


def validate_with_retry(response_generator, max_attempts=3):
    feedback = None

    for attempt in range(1, max_attempts + 1):
        print(f"\nAttempt {attempt}/{max_attempts}")

        # Get a response from our simulated AI.
        raw_response = response_generator(feedback)

        try:
            # Validate the response using Pydantic.
            result = TaskResult.model_validate(raw_response)

            print("Validation successful!")
            return result

        except ValidationError as error:
            feedback = str(error)

            logging.warning(
                "Validation failed on attempt %s: %s",
                attempt,
                feedback,
            )

            if attempt == max_attempts:
                raise RuntimeError(
                    "All attempts failed validation."
                ) from error

            print("Retrying with validation feedback...")


# These responses simulate an AI that makes a mistake
# and then corrects it.
simulated_responses = [
    {
        "summary": "Networking study plan",
        "category": "study",
        "confidence": 1.5,  # Invalid!
        "next_steps": ["Review IP addressing"],
    },
    {
        "summary": "Networking study plan",
        "category": "study",
        "confidence": 0.9,  # Valid!
        "next_steps": [
            "Review IP addressing",
            "Study routing",
        ],
    },
]


def simulated_ai(feedback):
    if feedback:
        print("Previous validation error received.")

    return simulated_responses.pop(0)


if __name__ == "__main__":
    result = validate_with_retry(simulated_ai)

    print("\nFINAL VALIDATED JSON:")
    print(result.model_dump_json(indent=2))