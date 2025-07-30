from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

workspace_users = Table(
    "workspace_users",
    Base.metadata,
    Column("workspace_id", String, ForeignKey("workspaces.id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
)

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    type = Column(String, nullable=False)

    user_id = Column(String, ForeignKey("users.id"), nullable=False)  # dono workspace

    owner = relationship(
        "User", back_populates="owned_workspaces", foreign_keys=[user_id]
    )

    users = relationship(
        "User", secondary=workspace_users, back_populates="workspaces", lazy="joined"
    )

    expenses = relationship("Expense", back_populates="workspace", lazy="joined")

    tags = relationship("Tag", back_populates="workspace", lazy="joined")
