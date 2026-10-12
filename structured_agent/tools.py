
import logging

from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("structured_agent")


class CalculatorInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    a: int
    b: int


class CalculatorOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=0)


def calculator_tool(arguments: CalculatorInput) -> dict:
    """Simulated calculator tool."""
    return {"total": arguments.a + arguments.b}


def run_tool(raw_arguments: dict) -> CalculatorOutput:
    logger.info("Validating calculator arguments")

    # Step 1: Validate tool input
    arguments = CalculatorInput.model_validate(raw_arguments)

    logger.info("Running calculator tool")

    # Step 2: Execute the tool
    raw_result = calculator_tool(arguments)

    # Step 3: Validate tool output
    validated_result = CalculatorOutput.model_validate(raw_result)

    logger.info("Calculator result validated successfully")

    return validated_result


if __name__ == "__main__":
    result = run_tool({"a": 10, "b": 20})
    print("\nVALIDATED TOOL OUTPUT:")
    print(result.model_dump_json(indent=2))
