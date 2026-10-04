from typing import Any
from fastapi.testclient import TestClient

def test_annuler_une_reservation_deja_annulee_renvoie_409(client: TestClient, item_velo: dict[str, Any]) -> None:
    # Given : une réservation existe et a déjà été annulée.
    creation = client.post("/reservations", json={
        "item_id": item_velo["id"],
        "date_debut": "2026-11-01",
        "date_fin": "2026-11-05",
    })
    reservation_id = creation.json()["id"]
    client.post(f"/reservations/{reservation_id}/annuler")

    # When : on demande une seconde annulation.
    response = client.post(f"/reservations/{reservation_id}/annuler")

    # Then : l'API refuse avec un conflit, et la réservation reste annulée.
    assert response.status_code == 409
    assert client.get(f"/reservations/{reservation_id}").json()["statut"] == "annulee" 


from datetime import date
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.routers import reservations


def test_reservation_dans_le_passe_est_refusee(
    client: TestClient, item_velo: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given : "aujourd'hui" est fixé, quel que soit le jour où la suite tourne.
    monkeypatch.setattr(reservations, "aujourd_hui", lambda: date(2026, 9, 10))

    response = client.post("/reservations", json={
        "item_id": item_velo["id"], "date_debut": "2026-09-01", "date_fin": "2026-09-05",
    })

    assert response.status_code == 422 
from typing import Any
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.routers import reservations


def test_annulation_envoie_une_notification(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, reservation_active: dict[str, Any]
) -> None:
    notifier = Mock()
    monkeypatch.setattr(reservations, "envoyer_notification_annulation", notifier)

    response = client.post(f"/reservations/{reservation_active['id']}/annuler")

    assert response.status_code == 200
    notifier.assert_called_once_with(reservation_id=reservation_active["id"])
def test_annulation_reussit_meme_si_la_notification_echoue(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, reservation_active: dict[str, Any]
) -> None:
    notifier = Mock(side_effect=ConnectionError("serveur mail injoignable"))
    monkeypatch.setattr(reservations, "envoyer_notification_annulation", notifier)

    response = client.post(f"/reservations/{reservation_active['id']}/annuler")

    assert response.status_code == 200