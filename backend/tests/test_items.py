from fastapi.testclient import TestClient
from conftest import Storage



def test_creer_un_item_nominal(client: TestClient) -> None:
    payload = {
        "titre": "Marteau",
        "description": "Un marteau standard",
        "tarif_jour": 5.0,
        "disponible": True,
    }

    response = client.post("/items", json=payload)

    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["titre"] == "Marteau"

# def test_lister_avec_skip_saute_les_premiers(client: TestClient, storage: Storage) -> None:
#     # Given : cinquante items, insérés sans passer par cinquante requêtes HTTP.
#     for i in range(1, 51):
#         storage.items[i] = {"id": i, "titre": f"Item {i}", "description": None,
#                             "tarif_jour": 5.0, "disponible": True}

#     response = client.get("/items", params={"skip": 40, "limit": 20})

#     assert [item["id"] for item in response.json()] == list(range(41, 51))


# def test_item_update_sans_champ_est_vide() -> None:
#     assert ItemUpdate().model_dump(exclude_unset=True) == {}