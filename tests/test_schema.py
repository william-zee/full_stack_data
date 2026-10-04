from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.reservation import ReservationCreate


def test_dates_inversees_sont_refusees_par_le_schema() -> None:
    with pytest.raises(ValidationError, match="date_fin"):
        ReservationCreate(item_id=1, date_debut=date(2026, 9, 5), date_fin=date(2026, 9, 1)) 

from datetime import date
import pytest
from pydantic import ValidationError

from app.schemas.item import ItemUpdate
from app.schemas.reservation import ReservationCreate


def test_reservation_valide_est_acceptee() -> None:
    reservation = ReservationCreate(
        item_id=1,
        date_debut=date(2026, 9, 1),
        date_fin=date(2026, 9, 5),
    )
    assert reservation.date_fin > reservation.date_debut


def test_item_update_sans_champ_est_vide() -> None:
    assert ItemUpdate().model_dump(exclude_unset=True) == {}