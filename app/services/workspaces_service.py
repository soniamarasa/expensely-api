from fastapi import APIRouter, Depends, HTTPException
from app.dependencies import get_current_user
from app.db.supabase_client import supabase
from typing import List

router = APIRouter()

def create_workspace(workspace: dict, user=Depends(get_current_user)):
    workspace_data = {
        "name": workspace["name"],
        "color": workspace["color"],
        "type": workspace["type"],
        "user_id": user["id"],
    }

    # Cria o workspace
    response = supabase.table("workspaces").insert(workspace_data).execute()
    if response.error:
        raise HTTPException(status_code=400, detail=response.error.message)

    workspace_id = response.data[0]["id"]

    # Cria entradas na tabela workspace_users
    member_ids = [user["id"]] + [
        u["id"] for u in workspace.get("users", []) if u["id"] != user["id"]
    ]
    for uid in member_ids:
        supabase.table("workspace_users").insert(
            {"workspace_id": workspace_id, "user_id": uid}
        ).execute()

    return {"message": "Workspace criado com sucesso", "id": workspace_id}


def list_user_workspaces(user=Depends(get_current_user)):
    workspaces_owned = (
        supabase.from_("workspaces")
        .select("*")
        .eq("user_id", user["id"])
        .execute()
        .data
    )

    relation_resp = (
        supabase.from_("workspace_users")
        .select("workspace_id")
        .eq("user_id", user["id"])
        .execute()
    )
    related_ids = [row["workspace_id"] for row in relation_resp.data]

    workspaces_joined = []
    if related_ids:
        workspaces_joined = (
            supabase.from_("workspaces")
            .select("*")
            .in_("id", related_ids)
            .execute()
            .data
        )

    return list({ws["id"]: ws for ws in workspaces_owned + workspaces_joined}.values())


def update_workspace(workspace_id: str, data: dict, user=Depends(get_current_user)):
    resp = (
        supabase.from_("workspaces")
        .select("user_id")
        .eq("id", workspace_id)
        .maybe_single()
        .execute()
    )
    if not resp.data or resp.data["user_id"] != user["id"]:
        raise HTTPException(
            status_code=403, detail="Apenas o dono pode editar o workspace"
        )

    update_resp = (
        supabase.from_("workspaces").update(data).eq("id", workspace_id).execute()
    )
    if update_resp.error:
        raise HTTPException(status_code=400, detail=update_resp.error.message)

    return {"message": "Workspace atualizado"}


def delete_workspace(workspace_id: str, user=Depends(get_current_user)):
    resp = (
        supabase.from_("workspaces")
        .select("user_id")
        .eq("id", workspace_id)
        .maybe_single()
        .execute()
    )
    if not resp.data or resp.data["user_id"] != user["id"]:
        raise HTTPException(
            status_code=403, detail="Apenas o dono pode deletar o workspace"
        )

    supabase.from_("workspace_users").delete().eq(
        "workspace_id", workspace_id
    ).execute()
    supabase.from_("workspaces").delete().eq("id", workspace_id).execute()

    return {"message": "Workspace deletado"}


def user_has_access_to_workspace(user_id: str, workspace_id: str) -> bool:
    workspace = (
        supabase.table("workspaces")
        .select("user_id")
        .eq("id", workspace_id)
        .single()
        .execute()
    )
    if workspace.data and workspace.data["user_id"] == user_id:
        return True

    membership = (
        supabase.table("workspace_users")
        .select("id")
        .eq("workspace_id", workspace_id)
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    return membership.data is not None
