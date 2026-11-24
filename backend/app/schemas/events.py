import time
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StreamEventType(str, Enum):
    STATUS = "STATUS"
    TOKEN = "TOKEN"
    SOURCE = "SOURCE"
    DONE = "DONE"
    ERROR = "ERROR"
    CHUNK = "CHUNK"


class ResearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=3, max_length=500)
    depth: Literal["quick", "deep"] = "quick"


class StreamEvent(BaseModel):
    event: StreamEventType
    data: dict | str = Field(default_factory=dict)
    timestamp: float = Field(default_factory=time.time)
