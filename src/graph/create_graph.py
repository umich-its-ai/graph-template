# import asyncio
import importlib
import inspect
import pkgutil
from typing import List

from src.graph.agent_graph import AgentGraph
from src.tools.base import MiMaizeyTool


def load_tools_from_directory(package_path: str) -> List[MiMaizeyTool]:
    """
    Dynamically load and instantiate all tools from the given package.
    Expects package_path in dot notation (e.g. "tools.tool_directory").
    """
    tools = []
    # Import the package that contains our tools
    package = importlib.import_module(package_path)
    # Iterate through all modules in the package
    for _, modname, _ in pkgutil.iter_modules(package.__path__):
        full_module_name = f"{package_path}.{modname}"
        module = importlib.import_module(full_module_name)
        # Inspect each member of the module
        for name, cls in inspect.getmembers(module, inspect.isclass):
            # Check if it is a subclass of MiMaizeyTool (and not the base class itself)
            if issubclass(cls, MiMaizeyTool) and cls is not MiMaizeyTool:
                tools.append(cls())
    return tools


def create_mimaizey_graph() -> AgentGraph:
    """
    Creates a new instance of the AgentGraph with the user's tools and configuration.
    It automatically loads all tools from the tools directory.
    """
    configured_tools = load_tools_from_directory("src.tools.tool_directory")

    graph_config = {"configurable": {}}

    mimaizey_instance: AgentGraph = AgentGraph(
        tools=configured_tools, config=graph_config
    )
    mimaizey_instance.compile()

    return mimaizey_instance


# async def main():
#     mimaizey_graph = create_mimaizey_graph()
#     resp = await mimaizey_graph.invoke(
#         chat_history=[],
#         message="I want to multiply 3 by 4",
#     )
#     print(resp[0])


# asyncio.run(main())
