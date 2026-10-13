
from pydantic import BaseModel, ConfigDict, Field


class TaskResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=200)
    category: str
    confidence: float = Field(ge=0.0, le=1.0)
    next_steps: list[str] = Field(default_factory=list, max_length=5)



