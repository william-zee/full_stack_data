from typing import Annotated
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app.api_client import ApiError, api_client

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/items/{item_id}/reservations", response_class=HTMLResponse)
def reserver(
    request: Request,
    item_id: int,
    date_debut: Annotated[str, Form()],
    date_fin: Annotated[str, Form()]
) -> Response:
    try:
        api_client.create_reservation({
            "item_id": item_id,
            "date_debut": date_debut,
            "date_fin": date_fin
        })
    except ApiError as exc:
        if exc.status_code == 422:
            # En cas de refus du backend, on recharge les données pour la vue
            item = api_client.get_item(item_id)
            reservations = api_client.list_reservations(item_id)
            
            # Extraction propre des messages d'erreur depuis le JSON du backend
            erreurs = []
            if isinstance(exc.detail, list):
                erreurs = [err.get("msg", str(err)) for err in exc.detail]
            else:
                erreurs = [str(exc.detail)]
            
            # On renvoie un code 422 au navigateur
            return templates.TemplateResponse(
                request,
                "items/detail.html",
                {
                    "item": item,
                    "reservations": reservations,
                    "erreurs_resa": erreurs,
                    "saisie_resa": {"date_debut": date_debut, "date_fin": date_fin}
                },
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        raise  # Toute autre erreur (500, etc.) est levée au gestionnaire global

    # Succès : redirection 303 avec paramètre de confirmation
    return RedirectResponse(f"/items/{item_id}?resa=ok", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/reservations/{reservation_id}")
def annuler_reservation(
    request: Request,
    reservation_id: int,
    item_id: Annotated[int, Form()],
    statut: Annotated[str, Form()]
) -> Response:
    """Traduit la soumission POST du HTML en une requête PATCH pour l'API."""
    if statut == "annulee":
        try:
            api_client.cancel_reservation(reservation_id)
        except ApiError as exc:
            if exc.status_code == 409:
                # La réservation était déjà annulée. Redirection sans page d'erreur.
                return RedirectResponse(f"/items/{item_id}?erreur=409", status_code=status.HTTP_303_SEE_OTHER)
            raise
    
    return RedirectResponse(f"/items/{item_id}?annulation=ok", status_code=status.HTTP_303_SEE_OTHER)