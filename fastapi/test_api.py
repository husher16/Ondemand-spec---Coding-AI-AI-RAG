"""
Suite di test automatizzati per verificare tutti gli endpoint implementati nella lezione FastAPI.
Utilizza il TestClient ufficiale di Starlette/FastAPI.

Esecuzione:
    pytest test_api.py -v
    oppure
    python test_api.py
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    print("[OK] test_root passed")


def test_users_order_precedence():
    # /users/me deve avere la precedenza su /users/{user_id}
    res_me = client.get("/users/me")
    assert res_me.status_code == 200
    assert res_me.json() == {"user_id": "utente corrente autenticato"}

    res_user = client.get("/users/mario")
    assert res_user.status_code == 200
    assert res_user.json() == {"user_id": "mario"}
    print("[OK] test_users_order_precedence passed")


def test_models_enum():
    res_alexnet = client.get("/models/alexnet")
    assert res_alexnet.status_code == 200
    assert res_alexnet.json()["message"] == "Deep Learning FTW!"

    # Modello non valido -> 422 Unprocessable Entity
    res_invalid = client.get("/models/unsupported_model")
    assert res_invalid.status_code == 422
    print("[OK] test_models_enum passed")


def test_file_path_converter():
    file_path = "downloads/film/ilgladiatore.mov"
    response = client.get(f"/files/{file_path}")
    assert response.status_code == 200
    assert response.json() == {"file_path": file_path}
    print("[OK] test_file_path_converter passed")


def test_items_pagination():
    response = client.get("/items/list?skip=1&limit=1")
    assert response.status_code == 200
    assert response.json() == [{"item_name": "Bar"}]
    print("[OK] test_items_pagination passed")


def test_boolean_query_conversion():
    # short=true -> non deve comparire description
    res_short = client.get("/items/details/box?short=1")
    assert res_short.status_code == 200
    assert "description" not in res_short.json()

    # short=false -> description presente
    res_long = client.get("/items/details/box?short=false")
    assert res_long.status_code == 200
    assert "description" in res_long.json()
    print("[OK] test_boolean_query_conversion passed")


def test_required_query_param():
    # Parametro obbligatorio presente
    res_ok = client.get("/items/required/item123?needy=important_value")
    assert res_ok.status_code == 200
    assert res_ok.json() == {"item_id": "item123", "needy": "important_value"}

    # Parametro mancante -> 422
    res_fail = client.get("/items/required/item123")
    assert res_fail.status_code == 422
    print("[OK] test_required_query_param passed")


def test_create_item_post():
    payload = {
        "name": "Cappello",
        "description": "Ripara bene dal sole",
        "price": 15.0,
        "tax": 3.30
    }
    response = client.post("/items/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Cappello"
    assert data["price_with_tax"] == 18.30
    print("[OK] test_create_item_post passed")


def test_update_item_put():
    payload = {
        "name": "Cappellino",
        "description": "Edizione estiva",
        "price": 10.0,
        "tax": 2.20
    }
    response = client.put("/items/update/5?q=colore_blu", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == 5
    assert data["name"] == "Cappellino"
    assert data["q"] == "colore_blu"
    print("[OK] test_update_item_put passed")


def test_query_validation():
    # q deve rispettare pattern ^fixedquery$
    res_ok = client.get("/items/validate_query/?q=fixedquery")
    assert res_ok.status_code == 200

    # q non rispetta il pattern -> 422
    res_fail = client.get("/items/validate_query/?q=randomquery")
    assert res_fail.status_code == 422
    print("[OK] test_query_validation passed")


def test_path_validation():
    # item_id compreso tra 1 e 1000
    res_ok = client.get("/items/validate_path/100")
    assert res_ok.status_code == 200
    assert res_ok.json() == {"item_id": 100}

    # item_id < 1 -> 422
    res_zero = client.get("/items/validate_path/0")
    assert res_zero.status_code == 422

    # item_id > 1000 -> 422
    res_high = client.get("/items/validate_path/1001")
    assert res_high.status_code == 422
    print("[OK] test_path_validation passed")


def test_filter_params_and_extra_forbid():
    # Parametri corretti
    url = "/items/filter/?limit=20&offset=5&order_by=price&tags=fastapi&tags=python"
    res_ok = client.get(url)
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["limit"] == 20
    assert data["offset"] == 5
    assert data["order_by"] == "price"
    assert data["tags"] == ["fastapi", "python"]

    # Parametro non autorizzato -> 422 (extra='forbid')
    res_extra = client.get("/items/filter/?unauthorized_param=malicious")
    assert res_extra.status_code == 422
    assert "extra inputs are not permitted" in res_extra.text.lower()
    print("[OK] test_filter_params_and_extra_forbid passed")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AVVIO SUITE DI TEST FASTAPI...")
    print("=" * 60)
    test_root()
    test_users_order_precedence()
    test_models_enum()
    test_file_path_converter()
    test_items_pagination()
    test_boolean_query_conversion()
    test_required_query_param()
    test_create_item_post()
    test_update_item_put()
    test_query_validation()
    test_path_validation()
    test_filter_params_and_extra_forbid()
    print("=" * 60)
    print("TUTTI I TEST SUPERATI CON SUCCESSO!")
    print("=" * 60 + "\n")
