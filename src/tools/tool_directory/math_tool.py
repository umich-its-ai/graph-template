# Example tool that multiplies two numbers
import logging
from typing import Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel

from src.tools.base import MiMaizeyTool
from src.tools.schemas import ToolArtifact, ToolSource

logger = logging.getLogger(__name__)


# Define the input schema for the tool
class MultiplicationToolInput(BaseModel):
    num1: float
    num2: float


class MultiplicationTool(MiMaizeyTool):
    name: str = "multiplication_tool"
    description: str = """
        Use this tool to multiply two numbers.
    """
    args_schema: Type[BaseModel] = MultiplicationToolInput

    # note that the args are the same as the input schema
    async def _arun(
        self, num1: float, num2: float, config: RunnableConfig
    ) -> tuple[float, ToolArtifact]:

        configurable = {
            k: v
            for k, v in config.get("configurable", {}).items()
            if not k.startswith("__") and not k.startswith("checkpoint")
        }  # Filter out private keys and checkpoint keys. You are only interested in the keys that are added by you.
        logger.info(f"✨✨✨✨ config is {configurable}")

        return num1 * num2, ToolArtifact(
            sources=[ToolSource(label="Multiplication", url="")],
            metadata={"args": {"num1": num1, "num2": num2}},
        )
