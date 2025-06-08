from typing import List
from app.db.supabase_client import supabase
from app.schemas.tag_schema import TagCreate, Tag
from app.services.workspaces_service import user_has_access_to_workspace


def create_tag_service(tag: TagCreate, user_id: str) -> Tag:
    if not user_has_access_to_workspace(user_id, tag.workspaceId):
        raise Exception("Usuário não tem acesso a este workspace.")

    data = tag.dict()
    data["userId"] = user_id

    response = supabase.table("tags").insert(data).execute()
    if response.status_code != 201:
        raise Exception("Erro ao criar tag")
    return Tag(**response.data[0])


def get_tags_by_workspace(workspace_id: str, user_id: str) -> List[Tag]:
    if not user_has_access_to_workspace(user_id, workspace_id):
        raise Exception("Usuário não tem acesso a este workspace.")

    response = (
        supabase.table("tags").select("*").eq("workspaceId", workspace_id).execute()
    )
    if response.status_code != 200:
        raise Exception("Erro ao buscar tags")
    return [Tag(**item) for item in response.data]

def update_tag_service(tag_id: str, tag: TagCreate, user_id: str) -> Tag:
    # Busca a tag atual
    tag_resp = supabase.table("tags").select("*").eq("id", tag_id).single().execute()
    if not tag_resp.data:
        raise Exception("Tag não encontrada.")

    tag_data = tag_resp.data

    # Valida acesso ao workspace
    if not user_has_access_to_workspace(user_id, tag_data["workspaceId"]):
        raise Exception("Usuário não tem acesso a este workspace.")

    # Prepara os dados para atualizar, mantendo o userId original
    data = tag.dict()
    data["userId"] = tag_data["userId"]

    response = supabase.table("tags").update(data).eq("id", tag_id).execute()
    if response.status_code != 200:
        raise Exception("Erro ao atualizar tag")
    return Tag(**response.data[0])


def delete_tag(tag_id: str, user_id: str) -> dict:
    tag = (
        supabase.table("tags").select("workspaceId").eq("id", tag_id).single().execute()
    )
    if not tag.data:
        raise Exception("Tag não encontrada.")

    workspace_id = tag.data["workspaceId"]
    if not user_has_access_to_workspace(user_id, workspace_id):
        raise Exception("Usuário não tem acesso a este workspace.")

    response = supabase.table("tags").delete().eq("id", tag_id).execute()
    if response.status_code != 200:
        raise Exception("Erro ao deletar tag.")
    return {"detail": "Tag deletada com sucesso"}
