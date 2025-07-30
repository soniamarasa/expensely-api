from sqlalchemy.orm import Session
from uuid import uuid4
from app.models import Expense as ExpenseModel
from app.schemas.expense_schema import ExpenseCreate, Expense, AnnualExpenseSummary
from app.services.workspaces_service import user_has_access_to_workspace
from datetime import datetime
from typing import List, Optional
from collections import defaultdict
from app.models import User as UserModel


def create_expense_service(
    expense: ExpenseCreate, user_id: str, db: Session
) -> Expense:
    if not user_has_access_to_workspace(user_id, expense.workspaceId, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    new_expense = ExpenseModel(
        id=str(uuid4()),
        user_id=user_id,
        workspace_id=expense.workspaceId,
        name=expense.name,
        value=expense.value,
        date=expense.date,
        description=expense.description,
        color=expense.color,
        tag_id=expense.tagId,
        category_id=expense.category.get("id") if expense.category else None,
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return Expense.from_orm(new_expense)


def get_expenses_by_workspace(
    workspace_id: str,
    user_id: str,
    db: Session,
    month: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Expense]:
    if not user_has_access_to_workspace(user_id, workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    query = db.query(ExpenseModel).filter(ExpenseModel.workspace_id == workspace_id)

    if month and year:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + int(month == 12), (month % 12) + 1, 1)
        query = query.filter(
            ExpenseModel.date >= start_date, ExpenseModel.date < end_date
        )

    expenses = query.all()
    return [Expense.from_orm(e) for e in expenses]


def delete_expense(expense_id: str, user_id: str, db: Session):
    expense = db.query(ExpenseModel).filter_by(id=expense_id).first()
    if not expense:
        raise Exception("Despesa não encontrada.")

    if not user_has_access_to_workspace(user_id, expense.workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    db.delete(expense)
    db.commit()

    return {"detail": "Despesa deletada"}


def update_expense(
    expense_id: str, data: ExpenseCreate, user_id: str, db: Session
) -> Expense:
    expense = db.query(ExpenseModel).filter_by(id=expense_id).first()
    if not expense:
        raise Exception("Despesa não encontrada.")

    if not user_has_access_to_workspace(user_id, expense.workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    expense.name = data.name
    expense.value = data.value
    expense.date = data.date
    expense.description = data.description
    expense.color = data.color
    expense.tag_id = data.tagId
    expense.category_id = data.category.get("id") if data.category else None

    db.commit()
    db.refresh(expense)

    return Expense.from_orm(expense)


def get_annual_expense_summary(
    workspace_id: str, year: int, user_id: str, db: Session
) -> dict:
    if not user_has_access_to_workspace(user_id, workspace_id, db):
        raise Exception("Usuário não tem acesso a este workspace.")

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)

    expenses = (
        db.query(ExpenseModel)
        .filter(
            ExpenseModel.workspace_id == workspace_id,
            ExpenseModel.date >= start_date,
            ExpenseModel.date <= end_date,
        )
        .all()
    )

    result = defaultdict(lambda: {"total": 0.0})

    for item in expenses:
        month = item.date.strftime("%B").lower()
        category_id = item.category_id or "Sem Categoria"

        if category_id not in result[month]:
            result[month][category_id] = {"itens": [], "total": 0.0}

        user_entry = next(
            (
                e
                for e in result[month][category_id]["itens"]
                if e["user"]["id"] == item.user_id
            ),
            None,
        )

        if user_entry:
            user_entry["total"] += item.value or 0
        else:
            result[month][category_id]["itens"].append(
                {
                    "user": {
                        "id": item.user_id,
                        "name": item.user.name if item.user else "Desconhecido",
                    },
                    "total": item.value or 0,
                }
            )

        result[month][category_id]["total"] += item.value or 0
        result[month]["total"] += item.value or 0

    return result
