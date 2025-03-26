import logging
import os
from datetime import datetime
from itertools import chain
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    ToolMessage,
    filter_messages,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import StructuredTool
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import Command

from src.graph.prompts import SYSPROMPT
from src.graph.states import AgentGraphState
from src.graph.utils import (
    get_artifact_sources,
    get_tool_call_args,
    get_tool_names_from_messages,
    validate_tool_artifact,
)
from src.tools.schemas import ToolCall

load_dotenv()

logger = logging.getLogger(__name__)


class Assistant:
    def __init__(self, llm_with_tools: AzureChatOpenAI, prompt: ChatPromptTemplate):
        self.llm_with_tools = llm_with_tools
        self.prompt = prompt

    async def __call__(self, state: dict, config: RunnableConfig):
        """
        NOTE: config to always have the key 'name' in the "configurable" key.
        """
        configuration = config.get("configurable", {})
        formatted_prompt = self.prompt.format_messages(
            messages=state["messages"],
        )
        while True:
            try:
                result = self.llm_with_tools.invoke(formatted_prompt)
            except KeyError as e:
                logger.exception(e)
                return {
                    "messages": [
                        AIMessage(
                            content="An error occurred while processing your request",
                            usage_metadata={
                                "input_tokens": 0,
                                "output_tokens": 0,
                                "total_tokens": 0,
                            },
                        )
                    ]
                }

            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("text")
            ):
                state = {
                    **state,
                    "messages": add_messages(
                        state["messages"],
                        [HumanMessage(content="Respond with a real output.")],
                    ),
                }
            else:
                break

        return {"messages": result}


class AgentGraph:
    """
    A self-contained AI graph that integrates assistant interactions and tool calls.
    This class wraps the functionality into one class (without using a base class)
    while keeping the Assistant class separate and unchanged.
    """

    def __init__(
        self,
        state_class: type = AgentGraphState,
        tools: list[StructuredTool] = [],
        config: dict = {},
    ):
        self.config = config
        self.system_prompt = SYSPROMPT

        # Initialize the LLM with AzureChatOpenAI using environment variables.
        self._llm = AzureChatOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            openai_organization=os.getenv("AZURE_OPENAI_ORGANIZATION"),
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )

        # Set up the primary prompt with a system prompt and a messages placeholder.
        self.primary_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(time=datetime.now().strftime("%A %Y-%m-%d %H:%M:%S"))

        self._state_class = state_class
        self._tools = tools

        # Create the state graph.
        self._graph = StateGraph(self._state_class)
        self.setup_graph()

    def setup_graph(self):
        """Sets up the graph with the appropriate nodes and transitions."""
        # Create the assistant node using the pre-existing Assistant class.
        assistant = Assistant(self.llm_with_tools, self.primary_prompt)
        self._graph.add_node("assistant", assistant)

        # Create tool nodes and add them to the graph.
        for tool_name in self.tools_map:
            self._graph.add_node(tool_name, self.tool_node)

        # Set the entry point to the assistant node.
        self._graph.set_entry_point("assistant")
        # Add conditional edges from the assistant to tools.
        self._graph.add_conditional_edges(source="assistant", path=self.tools_condition)

    @property
    def tools_map(self):
        """Returns a mapping of tool names to tool instances."""
        return {tool.name: tool for tool in self._tools}

    @property
    def llm_with_tools(self):
        """Binds the available tools to the LLM (parallel tool calls disabled)."""
        return self._llm.bind_tools(self._tools, parallel_tool_calls=False)

    async def tool_node(self, state: dict, config: RunnableConfig):
        """
        Invokes a tool node using the last message from the assistant and
        returns a command to continue with the assistant node.
        """
        tool_node = ToolNode(self._tools)
        tool_node_output = await tool_node.ainvoke(
            {"messages": [state["messages"][-1]]}, config=config
        )
        tool_messages = tool_node_output.get("messages")
        return Command(update={"messages": tool_messages}, goto="assistant")

    def tools_condition(self, state: dict):
        """
        Examines the last message for a tool call.
        Returns the tool name if one is detected, otherwise returns '__end__'.
        """
        if isinstance(state["messages"], list):
            ai_message = state["messages"][-1]
            if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
                return ai_message.tool_calls[0]["name"]
        else:
            raise ValueError(f"No messages found in input state: {state}")
        return "__end__"

    def compile(self):
        """Compiles the underlying state graph."""
        self.compiled_graph = self._graph.compile()

    async def invoke(
        self,
        chat_history: list[AnyMessage],
        message: str,
        runtime_config: dict[str, Any] = {},
    ):
        """
        Invokes the graph with the current chat history and a new human message.
        Returns the final messages, a flattened list of tool sources, and details of tool calls.
        """
        logger.info(f"\n💬💬💬 {len(chat_history)} message(s) in chat history.")
        # Merge runtime configuration with the base configuration.
        config_to_invoke = {**self.config}
        config_to_invoke["configurable"].update(runtime_config)

        output = await self.compiled_graph.ainvoke(
            {
                "messages": add_messages(
                    chat_history,
                    [HumanMessage(content=[{"type": "text", "text": message}])],
                )
            },
            config_to_invoke,
        )

        messages: list[AnyMessage] = output.get("messages")
        logger.info(f"\nGRAPH OUTPUT: {messages}")

        # Process tool messages to extract tool names, arguments, and artifact sources.
        tool_messages: list[ToolMessage] = filter_messages(
            messages, include_types=("tool",)
        )
        tool_names = get_tool_names_from_messages(tool_messages)
        tool_artifacts = list(map(validate_tool_artifact, tool_messages))
        tool_sources = map(get_artifact_sources, tool_artifacts)
        flattened_sources = list(set(chain.from_iterable(tool_sources)))
        tool_args = map(get_tool_call_args, tool_artifacts)
        tool_calls = [
            ToolCall(tool_name=name, metadata={"args": args})
            for name, args in zip(tool_names, tool_args)
        ]

        return messages, flattened_sources, tool_calls
