import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 768 dimensions corresponds to Google text-embedding-004 standard
    embedding = mapped_column(Vector(768), nullable=True)
    # Named "metadata" in SQL, attribute "chunk_metadata" in Python to avoid collision with Base.metadata
    chunk_metadata: Mapped[dict] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )
