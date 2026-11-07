"""
Modulo 1: Fondamenti di Routing, Path Parameters e Query Parameters in FastAPI.
Replica esatta della prima parte della video-lezione.
"""
from enum import Enum
from fastapi import FastAPI

app = FastAPI(
    title="FastAPI Live - Modulo 1: Routing & Parametri",
    description="Esempi didattici di Path Parameters, Enum, File Paths e Query Parameters"
)

# 1. Endpoint Radice
@app.get("/")
async def root():
    """Endpoint base per verificare lo stato dell'API."""
    return {"message": "Hello World"}


# 2. Path Parameter con validazione del tipo (int)
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Esempio di path parameter tipizzato.
    FastAPI effettua la conversione e validazione automatica (se item_id non è intero -> 422).
    """
    return {"item_id": item_id}


# 3. Ordine dei Path Parameters (Percorsi statici vs dinamici)
# Nota didattica: /users/me DEVE essere dichiarato PRIMA di /users/{user_id}
@app.get("/users/me")
async def read_user_me():
    """Restituisce le informazioni dell'utente attualmente autenticato."""
    return {"user_id": "utente corrente"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    """Restituisce le informazioni di uno specifico utente in base all'ID."""
    return {"user_id": user_id}


# 4. Path Parameters con Valori Predefiniti (Enum)
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    """
    Accetta solo valori predefiniti definiti nell'Enum ModelName.
    In Swagger UI compare un menu a tendina con i valori consentiti.
    """
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


# 5. Path Parameters contenenti percorsi di file (convertitore :path)
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    """
    Permette di catturare percorsi completi inclusi caratteri slash '/'
    Esempio: /files/downloads/film/ilgladiatore.mov
    """
    return {"file_path": file_path}


# 6. Query Parameters: Paginazione e valori di default
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    """
    Parametri di query per paginazione con valori di default:
    - skip: elementi da saltare (default 0)
    - limit: massimo numero di elementi da restituire (default 10)
    """
    return fake_items_db[skip : skip + limit]


# 7. Query Parameters Opzionali e Conversione Booleana (short: bool)
@app.get("/items_details/{item_id}")
async def read_item_details(item_id: str, q: str | None = None, short: bool = False):
    """
    - item_id: path parameter obbligatorio
    - q: query parameter opzionale (default None)
    - short: query parameter booleano (converte 1, true, on, yes in True; altrimenti False)
    """
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item


# 8. Query Parameters Obbligatori (senza valore di default)
@app.get("/items_required/{item_id}")
async def read_user_item_required(item_id: str, needy: str):
    """
    - item_id: path parameter obbligatorio
    - needy: query parameter obbligatorio (senza default -> errore 422 se omesso)
    """
    return {"item_id": item_id, "needy": needy}


# 9. Più Path Parameters e Query Parameters combinati
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item_combined(
    user_id: int,
    item_id: str,
    q: str | None = None,
    short: bool = False
):
    """
    Dimostra la combinazione di più parametri di percorso e di query nella medesima funzione.
    """
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item
