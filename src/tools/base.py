from logging import getLogger
from typing import Any, Optional, Type, Union

from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.messages.tool import ToolCall
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel

logger = getLogger(__name__)


class MiMaizeyTool(BaseTool):
    """
    Base interface for building MiMaizey tools, tailored for asynchronous operations.

    This class is designed to be subclassed by specific tool implementations.
    It mandates the definition of an asynchronous method `_arun` where the tool's
    logic must be implemented.

    Attributes:
        name (str): Name of the tool.
        description (str): Description of what the tool does.
        args_schema (Type[BaseModel]): Pydantic model defining the structure of input arguments.
        response_format (str): Format of the response; defaults to "content_and_artifact".

    Methods:
        ainvoke: Asynchronously invoke the tool with given input and configuration.
        _arun: Abstract method where the tool's core logic is to be defined by subclasses.
    """

    def __init_subclass__(
        cls, name: str | None = None, description: str | None = None, **kwargs
    ):
        cls.name = name if name else cls.name
        cls.description = description if description else cls.description
        super().__init_subclass__(**kwargs)

    name: str
    description: str
    args_schema: Type[BaseModel]
    response_format: str = "content_and_artifact"

    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Placeholder for synchronous tool methods, which are currently unsupported.

        Raises:
            NotImplementedError: Always raised to indicate no support for synchronous calls.
        """
        raise NotImplementedError("MiMaizeyTool does not support sync invocation.")

    async def ainvoke(
        self,
        input: Union[str, dict, ToolCall],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ):
        """
        Asynchronously invoke the tool using the specified input and configuration.

        Args:
            input (Union[str, dict, ToolCall]):
                The input for the tool, can be a string, dict, or a structured ToolCall.
            config (Optional[RunnableConfig]): Configuration for the tool's runtime, if any.

        Returns:
            The result of the tool's asynchronous run method.

        Raises:
            Exception: Re-raises any exceptions encountered during the tool's execution.
        """
        try:
            logger.info(f"\n🔧🔧🔧 TOOL SELECTED: {input}")
            return await super().ainvoke(input, config, **kwargs)
        except Exception as e:
            logger.exception(f"TOOL ERROR: {self.name} - {e}")
            raise

    async def _arun(
        self,
        config: RunnableConfig,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ):
        """
        Define the tool's core asynchronous logic in this method in the subclass.

        Args:
            config (RunnableConfig): Configuration settings for the tool run.
            run_manager (Optional[AsyncCallbackManagerForToolRun]): Manager for handling callbacks during the run.

        Note:
            This method should be overridden in any subclass to implement specific tool logic.
        """

        pass
