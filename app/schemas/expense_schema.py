from pydantic import BaseModel, RootModel
from typing import Optional, List, Dict
from datetime import datetime


# Schema para criação de uma nova despesa
class ExpenseCreate(BaseModel):
    name: Optional[str] = None
    value: Optional[float] = None
    category: Optional[Dict] = None
    tagId: Optional[str] = None
    date: Optional[datetime] = None
    userId: Optional[str] = None
    description: str
    color: str
    workspaceId: str


# Schema de resposta de uma despesa
class Expense(BaseModel):
    id: str
    name: Optional[str] = None
    value: Optional[float] = None
    category: Optional[Dict] = None
    tagId: Optional[str] = None
    tag: Optional[Dict] = None
    date: Optional[datetime] = None
    userId: Optional[str] = None
    description: str
    color: str
    workspaceId: str

    class Config:
        orm_mode = True


# Informações do usuário que gastou
class UserInfo(BaseModel):
    id: str
    name: str


# Gasto total por usuário
class UserExpense(BaseModel):
    user: UserInfo
    total: float


# Gasto por categoria com lista de usuários
class CategorySummary(BaseModel):
    itens: List[UserExpense]
    total: float


# Resumo de gastos por mês
class MonthSummary(BaseModel):
    total: float
    categories: Dict[str, CategorySummary]


# Resumo anual de despesas (chave = mês)
class AnnualExpenseSummary(RootModel[Dict[str, MonthSummary]]):
    pass
