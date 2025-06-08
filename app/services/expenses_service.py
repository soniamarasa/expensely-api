from typing import List
from app.db.supabase_client import supabase
from app.schemas.expense_schema import ExpenseCreate, Expense
from app.services.workspaces_service import user_has_access_to_workspace


def create_expense_service(expense: ExpenseCreate, user_id: str) -> Expense:
    if not user_has_access_to_workspace(user_id, expense.workspaceId):
        raise Exception("Usuário não tem acesso a este workspace.")

    data = expense.dict()
    data["userId"] = user_id

    response = supabase.table("expenses").insert(data).execute()
    if response.status_code != 201:
        raise Exception("Erro ao criar despesa")
    return Expense(**response.data[0])


def get_expenses_by_workspace(workspace_id: str, user_id: str) -> List[Expense]:
    if not user_has_access_to_workspace(user_id, workspace_id):
        raise Exception("Usuário não tem acesso a este workspace.")

    response = (
        supabase.table("expenses").select("*").eq("workspaceId", workspace_id).execute()
    )
    if response.status_code != 200:
        raise Exception("Erro ao buscar despesas")
    return [Expense(**item) for item in response.data]


def delete_expense(expense_id: str, user_id: str):
    # Primeiro busca a despesa
    resp = supabase.table("expenses").select("*").eq("id", expense_id).single().execute()
    if not resp.data:
        raise Exception("Despesa não encontrada.")

    current_data = resp.data

    # Valida se o user logado tem acesso ao workspace da despesa
    if not user_has_access_to_workspace(user_id, current_data["workspaceId"]):
        raise Exception("Usuário não tem acesso a este workspace.")

    # Agora pode deletar
    response = supabase.table("expenses").delete().eq("id", expense_id).execute()
    if response.status_code != 200:
        raise Exception("Erro ao deletar despesa")

    return {"detail": "Despesa deletada"}


def update_expense(expense_id: str, expense: ExpenseCreate, user_id: str) -> Expense:
    # Busca a despesa atual
    resp = (
        supabase.table("expenses").select("*").eq("id", expense_id).single().execute()
    )
    if not resp.data:
        raise Exception("Despesa não encontrada.")

    current_data = resp.data

    # Valida acesso ao workspace
    if not user_has_access_to_workspace(user_id, current_data["workspaceId"]):
        raise Exception("Usuário não tem acesso a este workspace.")

    # Prepara os dados para atualizar, mantendo o userId original
    data = expense.dict()
    data["userId"] = current_data["userId"]

    response = supabase.table("expenses").update(data).eq("id", expense_id).execute()
    if response.status_code != 200:
        raise Exception("Erro ao atualizar despesa")
    return Expense(**response.data[0])
