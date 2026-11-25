import uuid
from enum import Enum

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, enum_column


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_threads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, default="", nullable=False)
    sources: Mapped[list[dict]] = mapped_column(JSONB, default=list, nullable=False)
    role: Mapped[MessageRole] = mapped_column(enum_column(MessageRole), nullable=False)
