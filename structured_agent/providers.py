
from typing import Protocol

from structured_agent.schemas import TaskResult


class TaskProvider(Protocol):
    """Contract every task provider must implement."""

    def generate(
        self,
        prompt: str,
        feedback: str | None = None,
    ) -> TaskResult:
        ...


class MockTaskProvider:
    """Local provider for testing without API calls."""

    def generate(
        self,
        prompt: str,
        feedback: str | None = None,
    ) -> TaskResult:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if feedback is None:
            return TaskResult(
                summary="Initial simulated response",
                category="study",
                confidence=0.9,
                next_steps=["Review the task"],
            )

        return TaskResult(
            summary=f"Task received: {prompt[:150]}",
            category="study",
            confidence=0.95,
            next_steps=[
                "Review the requirements",
                "Complete the task",
            ],
        )
