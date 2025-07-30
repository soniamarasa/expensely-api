from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=True)

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)

    user = relationship("User", back_populates="tags")
    workspace = relationship("Workspace", back_populates="tags")

    expenses = relationship("Expense", back_populates="tag", lazy="joined")
