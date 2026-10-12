
import argparse
import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI

from structured_agent.agent import validate_with_retry
from structured_agent.schemas import TaskResult

from structured_agent.logging_config import logger

def mock_response(feedback):
    """Simulate an AI response without making an API call."""
    if feedback is None:
        return {
            "summary": "Study networking fundamentals",
            "category": "study",
            "confidence": 1.5,
            "next_steps": ["Review IP addressing"],
        }

    return {
        "summary": "Study networking fundamentals",
        "category": "study",
        "confidence": 0.95,
        "next_steps": [
            "Review IP addressing",
            "Practice subnetting",
        ],
    }


def api_response_generator(prompt):
    """Call the OpenAI API and return structured output."""
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env")

    client = OpenAI(api_key=api_key)

    def generate(feedback):
        messages = [
            {
                "role": "system",
                "content": (
                    "Return a useful task result matching the "
                    "required schema. Keep the summary concise."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        if feedback:
            messages.append({
                "role": "user",
                "content": (
                    "Your previous output failed validation. "
                    "Correct these issues:\n" + feedback
                ),
            })

        response = client.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=TaskResult,
        )

        message = response.choices[0].message

        if message.refusal:
            raise RuntimeError(f"Model refused: {message.refusal}")

        if message.parsed is None:
            raise RuntimeError("No parsed structured output returned.")

        return message.parsed.model_dump()

    return generate


def main():
    parser = argparse.ArgumentParser(
        description="Structured Output Agent"
    )
    parser.add_argument(
        "--mode",
        choices=["mock", "api"],
        default="mock",
        help="mock runs locally; api makes a real API call",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Task for the agent",
    )
    args = parser.parse_args()

    prompt = args.prompt or input("What do you want help with? ")

    try:
        if args.mode == "mock":
            generator = mock_response
            logger.info("Running in mock mode; no API calls.")
        else:
            generator = api_response_generator(prompt)
            logger.info("Running in API mode; API usage may cost money.")

        result = validate_with_retry(generator)

        print("\nVALIDATED OUTPUT:")
        print(json.dumps(result.model_dump(), indent=2))

    except Exception as error:
        logger.error("Agent failed: %s", error)


if __name__ == "__main__":
    main()
