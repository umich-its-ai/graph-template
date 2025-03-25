from langchain_core.messages.tool import ToolMessage

from src.tools.schemas import ToolArtifact


def get_tool_names_from_messages(tool_messages: list[ToolMessage]):
    return [tool_message.name for tool_message in tool_messages]


def validate_tool_artifact(tool_message: ToolMessage):
    """
    Validates the ToolArtifact of a ToolMessage
    """
    if tool_message.artifact:
        return tool_message.artifact
    return None


def get_artifact_sources(
    tool_artifact: ToolArtifact | None,
):
    """
    Extracts the sources from a ToolArtifact
    """
    if not tool_artifact:
        return []
    if tool_artifact.sources:
        return tool_artifact.sources
    return []


def get_tool_call_args(tool_artifact: ToolArtifact | None):
    """
    Extracts the name of the tool from a ToolArtifact
    """
    if not tool_artifact:
        return None
    return tool_artifact.metadata.get("args", None)
