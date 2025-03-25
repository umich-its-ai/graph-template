from typing import Any

from pydantic import BaseModel, ConfigDict


class ToolSource(BaseModel):
    model_config = ConfigDict(frozen=True)
    label: str
    url: str = ""


class ToolCall(BaseModel):
    tool_name: str
    metadata: dict[str, Any] = {}


class ToolArtifact(BaseModel):
    """
    Schema for MiMaizey tool responses
    """

    sources: list[ToolSource]
    metadata: dict[str, Any] = {}
