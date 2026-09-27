from fastapi import APIRouter, HTTPException, Path, Query, Response, status
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

FAKE_DB: dict[int, dict] = {}
_next_id = 1


@router.get("", response_model=list[ItemRead], status_code=status.HTTP_200_OK)
def list_items(
    q: str | None = Query(default=None, description="Recherche textuelle dans le titre"),
    disponible: bool | None = Query(default=None, description="Filtrer par disponibilité"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
):
    items = list(FAKE_DB.values())
    if q is not None:
        items = [item for item in items if q.lower() in item["titre"].lower()]
    if disponible is not None:
        items = [item for item in items if item["disponible"] is disponible]
    return items[skip : skip + limit]


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate):
    global _next_id
    item = {"id": _next_id, **payload.model_dump()}
    FAKE_DB[_next_id] = item
    _next_id += 1
    return item


@router.get("/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
def get_item(item_id: int = Path(ge=1)):
    item = FAKE_DB.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} introuvable")
    return item


@router.put("/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
def replace_item(payload: ItemCreate, item_id: int = Path(ge=1)):
    if item_id not in FAKE_DB:
        raise HTTPException(status_code=404, detail=f"Item {item_id} introuvable")
    updated_item = {"id": item_id, **payload.model_dump()}
    FAKE_DB[item_id] = updated_item
    return updated_item


@router.patch("/{item_id}", response_model=ItemRead, status_code=status.HTTP_200_OK)
def update_item(payload: ItemUpdate, item_id: int = Path(ge=1)):
    item = FAKE_DB.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} introuvable")
    donnees = payload.model_dump(exclude_unset=True)
    item.update(donnees)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int = Path(ge=1)):
    if item_id not in FAKE_DB:
        raise HTTPException(status_code=404, detail=f"Item {item_id} introuvable")
    del FAKE_DB[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
