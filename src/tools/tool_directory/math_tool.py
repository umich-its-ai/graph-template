# Example tool that multiplies two numbers
import logging
from typing import Type

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.tools.base import MiMaizeyTool
from src.tools.schemas import ToolArtifact, ToolSource

logger = logging.getLogger(__name__)


# Define the input schema for the tool
class MultiplicationToolInput(BaseModel):
    num1: float = Field(
        description="The first number to multiply"
    )  # The description is used to provide additional information about the field to the AI
    num2: float = Field(description="The second number to multiply")


class MultiplicationTool(MiMaizeyTool):
    name: str = (
        "multiplication_tool"  # This is the name of the tool that the AI will use
    )
    description: str = """
        Use this tool to multiply two numbers.
    """  # This is the description of the tool. Add any custom instructions about the tool here.
    # The description should not be longer than 1024 characters.
    args_schema: Type[BaseModel] = (
        MultiplicationToolInput  # This is the input schema for the tool. It should be a Pydantic model which defines the structure of the input data.
    )
    # NOTE: Use Type[BaseModel] = None if the tool does not require any input

    # note that the args are the same as the input schema
    # Any custom logic goes in the _arun method
    async def _arun(
        self, num1: float, num2: float, config: RunnableConfig
    ) -> tuple[float, ToolArtifact]:

        configurable = {
            k: v
            for k, v in config.get("configurable", {}).items()
            if not k.startswith("__") and not k.startswith("checkpoint")
        }  # Filter out private keys and checkpoint keys. You are only interested in the keys that are added by you.
        # you need not to do the above. you can just get the appropriate key from the config if needed
        logger.info(f"✨✨✨✨ config is {configurable}")
        # The config is a dictionary that contains the runtime configuration of the tool.
        # Use this to pass any additional information to the tool that the AI does not need to be aware of.

        result = num1 * num2
        return result, ToolArtifact(
            sources=[ToolSource(label="Multiplication", url="")],
            metadata={"args": {"num1": num1, "num2": num2}},
        )
