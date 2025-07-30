from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app.schemas.expense_schema import AnnualExpenseSummary, ExpenseCreate, Expense
from app.services.expenses_service import (
    create_expense_service,
    get_annual_expense_summary,
    get_expenses_by_workspace,
    delete_expense,
    update_expense,
)
from app.dependencies import get_current_user, get_db

router = APIRouter()


@router.post("/", response_model=Expense)
def create_expense(
    expense: ExpenseCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return create_expense_service(expense, user["id"], db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workspace_id}", response_model=List[Expense])
def list_expenses(
    workspace_id: str,
    month: Optional[int] = None,
    year: Optional[int] = None,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_expenses_by_workspace(
            workspace_id, user_id=user_data["id"], month=month, year=year, db=db
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{expense_id}")
def remove_expense(
    expense_id: str, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        return delete_expense(expense_id, user["id"], db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{expense_id}", response_model=Expense)
def edit_expense(
    expense_id: str,
    expense: ExpenseCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return update_expense(expense_id, expense, user["id"], db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/annual/{workspace_id}/{year}", response_model=AnnualExpenseSummary)
def get_annual_summary(
    workspace_id: str,
    year: int,
    user_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_annual_expense_summary(
            workspace_id=workspace_id, user_id=user_data["id"], year=year, db=db
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
