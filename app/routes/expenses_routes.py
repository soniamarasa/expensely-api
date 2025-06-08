from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.schemas.expense_schema import ExpenseCreate, Expense
from app.services.expenses_service import (
    create_expense_service,
    get_expenses_by_workspace,
    delete_expense,
    update_expense,
)
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=Expense)
def create_expense(expense: ExpenseCreate, user=Depends(get_current_user)):
    try:
        return create_expense_service(expense, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workspace/{workspace_id}", response_model=List[Expense])
def list_expenses(workspace_id: str, user=Depends(get_current_user)):
    try:
        return get_expenses_by_workspace(workspace_id, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{expense_id}")
def remove_expense(expense_id: str, user=Depends(get_current_user)):
    try:
        return delete_expense(expense_id, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{expense_id}", response_model=Expense)
def edit_expense(
    expense_id: str, expense: ExpenseCreate, user=Depends(get_current_user)
):
    try:
        return update_expense(expense_id, expense, user["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
