
import pytest
from pydantic import ValidationError

from structured_agent.providers import MockTaskProvider


def test_mock_provider_uses_prompt():
    provider = MockTaskProvider()

    result = provider.generate(
        "Help me study computer networks",
        feedback="Correct the previous output",
    )

    assert "computer networks" in result.summary
    assert result.confidence == 0.95


def test_mock_provider_rejects_blank_prompt():
    provider = MockTaskProvider()

    with pytest.raises(ValueError):
        provider.generate("   ")


def test_mock_provider_returns_validated_result():
    provider = MockTaskProvider()

    result = provider.generate("Study Python")

    assert result.confidence <= 1.0
    assert len(result.next_steps) <= 5
