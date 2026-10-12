
import logging
import os
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from structured_agent.providers import MockTaskProvider
from structured_agent.schemas import TaskResult


load_dotenv()

logger = logging.getLogger("structured_agent")

app = FastAPI(title="Structured Output Agent API")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

provider = MockTaskProvider()


class TaskRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    prompt: str = Field(min_length=1, max_length=2000)


def require_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    expected_key = os.getenv("AGENT_API_KEY")

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )

    if x_api_key is None or not __import__("secrets").compare_digest(
        x_api_key, expected_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "ApiKey"},
        )


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    supplied_id = request.headers.get("X-Request-ID")

    try:
        request_id = (
            str(UUID(supplied_id))
            if supplied_id
            else str(uuid4())
        )
    except (ValueError, TypeError, AttributeError):
        request_id = str(uuid4())

    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/tasks",
    response_model=TaskResult,
    dependencies=[Depends(require_api_key)],
)
@limiter.limit("10/minute")
def create_task(
    request: Request,
    task: TaskRequest,
) -> TaskResult:
    request_id = request.state.request_id

    try:
        logger.info("Task request received | request_id=%s", request_id)
        result = provider.generate(task.prompt)
        logger.info("Task request completed | request_id=%s", request_id)
        return result

    except ValueError as error:
        logger.warning(
            "Invalid task input | request_id=%s",
            request_id,
        )
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except Exception as error:
        logger.exception(
            "Task processing failed | request_id=%s",
            request_id,
        )
        raise HTTPException(
            status_code=502,
            detail="Task processing failed.",
        ) from error

