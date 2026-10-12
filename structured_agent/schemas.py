
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


NonEmptyText = Annotated[
    str,
    Field(min_length=1, max_length=200),
]


class TaskResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    summary: NonEmptyText
    category: Annotated[str, Field(min_length=1, max_length=50)]
    confidence: float = Field(ge=0.0, le=1.0)
    next_steps: list[NonEmptyText] = Field(
        default_factory=list,
        max_length=5,
    )

