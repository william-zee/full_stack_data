# app/routers/items.py
from typing import Annotated
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.api_client import ApiError, api_client

router = APIRouter()


templates = Jinja2Templates(directory="app/templates")

MESSAGES_CREATION = {
    422: "Les données saisies ne sont pas valides.",
}



@router.get("/items", response_class=HTMLResponse)
def list_items_page(request: Request) -> HTMLResponse:
    items = api_client.list_items()
    return templates.TemplateResponse(request, "items/list.html", {"items": items})



@router.get("/items/new", response_class=HTMLResponse)
def new_item_form(request: Request) -> Response:
    return templates.TemplateResponse(request, "items/form.html", {})


@router.post("/items", response_class=HTMLResponse)
def create_item(
    request: Request,
    titre: Annotated[str, Form()],
    tarif_jour: Annotated[float, Form()],
    description: Annotated[str, Form()] = "",
    disponible: Annotated[bool, Form()] = False,
) -> Response:
    
    desc_val = None if not description.strip() else description

    try:
        new_item = api_client.create_item({
            "titre": titre,
            "description": desc_val,
            "tarif_jour": tarif_jour,
            "disponible": disponible
        })
    except ApiError as exc:
        if exc.status_code not in MESSAGES_CREATION:
            raise

        return templates.TemplateResponse(
            request,
            "items/form.html",
            {
                "erreur": MESSAGES_CREATION[exc.status_code],
                "saisie": {
                    "titre": titre,
                    "description": description,
                    "tarif_jour": tarif_jour,
                    "disponible": disponible,
                },
            },
            status_code=exc.status_code,
        )

    
    return RedirectResponse(f"/items/{new_item['id']}", status_code=303)


@router.get("/items/{item_id}", response_class=HTMLResponse)
def item_detail_page(request: Request, item_id: int) -> HTMLResponse:
    item = api_client.get_item(item_id)
    reservations = api_client.list_reservations(item_id)
    
    return templates.TemplateResponse(
        request, 
        "items/detail.html", 
        {
            "item": item,
            "reservations": reservations
        }
    )