from fastapi import APIRouter, HTTPException, Path, Query, status

from app.schemas.reservation import ReservationCreate, ReservationRead

router = APIRouter(prefix="/reservations", tags=["reservations"])

RESERVATIONS: dict[int, dict] = {}
_next_id = 1


@router.post("", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(payload: ReservationCreate):
    global _next_id
    reservation = {"id": _next_id, **payload.model_dump(), "statut": "active"}
    RESERVATIONS[_next_id] = reservation
    _next_id += 1
    return reservation


@router.get("", response_model=list[ReservationRead], status_code=status.HTTP_200_OK)
def list_reservations(
    item_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    reservations = list(RESERVATIONS.values())
    if item_id is not None:
        reservations = [
            reservation
            for reservation in reservations
            if reservation["item_id"] == item_id
        ]
    return reservations[:limit]


@router.get(
    "/{reservation_id}",
    response_model=ReservationRead,
    status_code=status.HTTP_200_OK,
)
def get_reservation(reservation_id: int = Path(ge=1)):
    reservation = RESERVATIONS.get(reservation_id)
    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Réservation {reservation_id} introuvable",
        )
    return reservation


@router.post(
    "/{reservation_id}/annuler",
    response_model=ReservationRead,
    status_code=status.HTTP_200_OK,
)
def cancel_reservation(reservation_id: int = Path(ge=1)):
    reservation = RESERVATIONS.get(reservation_id)
    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Réservation {reservation_id} introuvable",
        )
    if reservation["statut"] == "annulee":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Réservation {reservation_id} déjà annulée",
        )
    reservation["statut"] = "annulee"
    return reservation