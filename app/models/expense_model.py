from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    category = Column(JSONB, nullable=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id"), nullable=True)
    date = Column(DateTime, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    description = Column(String)
    color = Column(String)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tag = relationship("Tag", back_populates="expenses", lazy="joined")
    user = relationship("User", back_populates="expenses", lazy="joined")
    workspace = relationship("Workspace", back_populates="expenses", lazy="joined")
