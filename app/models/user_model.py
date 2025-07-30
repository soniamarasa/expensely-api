from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    gender = Column(String, nullable=True)
    birthdate = Column(Date, nullable=True)
    income = Column(Float, nullable=True)

    # Workspaces que o usuário é dono
    owned_workspaces = relationship(
        "Workspace", back_populates="owner", foreign_keys="[Workspace.user_id]"
    )

    # Workspaces que o usuário participa (muitos-para-muitos)
    workspaces = relationship(
        "Workspace", secondary="workspace_users", back_populates="users", lazy="joined"
    )

    # Expenses do usuário
    expenses = relationship("Expense", back_populates="user", lazy="joined")

    # Tags do usuário
    tags = relationship("Tag", back_populates="user", lazy="joined")
