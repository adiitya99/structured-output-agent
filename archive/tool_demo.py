
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from logging_config import logger


class CalculatorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    a: int
    b: int


class CalculatorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=0)


def calculator_tool(raw_arguments: dict) -> dict:
    arguments = CalculatorInput.model_validate(raw_arguments)

    # Simulate a tool that returns an incorrect result.
    return {"total": -10}


def run_tool(raw_arguments: dict) -> CalculatorOutput:
    logger.info("Validating calculator arguments")

    try:
        arguments = CalculatorInput.model_validate(raw_arguments)
    except ValidationError:
        logger.exception("Invalid calculator arguments")
        raise

    logger.info("Running calculator tool")

    # Here, the tool deliberately returns an invalid result.
    raw_result = calculator_tool(arguments.model_dump())

    try:
        validated_result = CalculatorOutput.model_validate(raw_result)
    except ValidationError:
        logger.exception("Invalid calculator result")
        raise

    logger.info("Calculator result validated successfully")
    return validated_result


if __name__ == "__main__":
    try:
        result = run_tool({"a": 10, "b": 20})
        print(result.model_dump_json(indent=2))
    except ValidationError:
        print("Tool failed validation. Check agent.log.")

