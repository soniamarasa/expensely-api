import uuid
from sqlalchemy import Column, String, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))

    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    gender = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)
    income = Column(Float, nullable=True)

    # Relacionamentos
    owned_workspaces = relationship(
        "Workspace", back_populates="owner", foreign_keys="[Workspace.user_id]"
    )

    workspaces = relationship(
        "Workspace", secondary="workspace_users", back_populates="users", lazy="joined"
    )

    expenses = relationship("Expense", back_populates="user", lazy="joined")
    tags = relationship("Tag", back_populates="user", lazy="joined")
