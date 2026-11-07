"""
Applicazione FastAPI unificata - Replica completa della video-lezione FastAPI.
Combina tutti i concetti e gli endpoint visti nei 3 moduli didattici:
1. Routing di base, Path Parameters, Enum, Path file e Query Parameters
2. Request Body con modelli Pydantic (POST / PUT con calcolo tasse)
3. Validazioni avanzate (Annotated, Query, Path e FilterParams con extra='forbid')

Avvio server:
    uvicorn main:app --reload
Documentazione interattiva:
    http://127.0.0.1:8000/docs (Swagger UI)
    http://127.0.0.1:8000/redoc (ReDoc)
"""
import sys
from pathlib import Path
from enum import Enum
from typing import Annotated
from fastapi import FastAPI, Query, Path as FastPath
from pydantic import BaseModel, Field

# Assicura che la directory src sia nel PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

app = FastAPI(
    title="FastAPI Corso Completo - Live Lesson Replica",
    description="""
    ## Progetto didattico FastAPI sviluppato durante la video-lezione.
    
    ### Moduli Inclusi:
    - **Modulo 1**: Routing fondamentale, Path Parameters tipizzati, ordine dei percorsi, Enum e Query Parameters.
    - **Modulo 2**: Gestione del Request Body con modelli Pydantic, conversioni `.model_dump()` e combinazione Path + Body + Query.
    - **Modulo 3**: Validazioni avanzate con `Annotated`, vincoli stringa (regex/lunghezza), vincoli numerici (`ge`, `le`) e raggruppamento con `FilterParams` (`extra='forbid'`).
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ==============================================================================
# MODULO 1: ROUTING, PATH PARAMETERS & QUERY PARAMETERS
# ==============================================================================

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/", tags=["Modulo 1 - Fondamenti"])
async def root():
    return {
        "message": "Benvenuto nella replica ufficiale della video-lezione FastAPI!",
        "docs": "/docs",
        "redoc": "/redoc"
    }


# Ordine critico: /users/me prima di /users/{user_id}
@app.get("/users/me", tags=["Modulo 1 - Fondamenti"])
async def read_user_me():
    return {"user_id": "utente corrente autenticato"}


@app.get("/users/{user_id}", tags=["Modulo 1 - Fondamenti"])
async def read_user(user_id: str):
    return {"user_id": user_id}


# Path parameter con Enum
@app.get("/models/{model_name}", tags=["Modulo 1 - Fondamenti"])
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}


# Path parameter con convertitore di percorso file
@app.get("/files/{file_path:path}", tags=["Modulo 1 - Fondamenti"])
async def read_file(file_path: str):
    return {"file_path": file_path}


# Query parameters con paginazione
@app.get("/items/list", tags=["Modulo 1 - Fondamenti"])
async def list_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


# Query parameters con conversione booleana automatica
@app.get("/items/details/{item_id}", tags=["Modulo 1 - Fondamenti"])
async def read_item_details(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item


# Query parameter obbligatorio (senza default)
@app.get("/items/required/{item_id}", tags=["Modulo 1 - Fondamenti"])
async def read_item_required(item_id: str, needy: str):
    return {"item_id": item_id, "needy": needy}


# Combinazione di più path e query parameters
@app.get("/users/{user_id}/items/{item_id}", tags=["Modulo 1 - Fondamenti"])
async def read_user_item_combined(user_id: int, item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item


# ==============================================================================
# MODULO 2: REQUEST BODY & PYDANTIC MODELS
# ==============================================================================

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.post("/items/", tags=["Modulo 2 - Request Body"])
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items/update/{item_id}", tags=["Modulo 2 - Request Body"])
async def update_item(item_id: int, item: Item, q: str | None = None):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result


# ==============================================================================
# MODULO 3: VALIDAZIONI AVANZATE CON ANNOTATED, QUERY, PATH E FILTERPARAMS
# ==============================================================================

@app.get("/items/validate_query/", tags=["Modulo 3 - Validazioni Avanzate"])
async def read_items_query_validation(
    q: Annotated[
        str | None,
        Query(
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            description="Query string con vincolo di lunghezza (3-50) e regex esatta"
        )
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/validate_path/{item_id}", tags=["Modulo 3 - Validazioni Avanzate"])
async def read_items_path_validation(
    item_id: Annotated[
        int,
        FastPath(
            title="The ID of the item to get",
            description="Identificativo compreso tra 1 e 1000",
            ge=1,
            le=1000
        )
    ]
):
    return {"item_id": item_id}


class FilterParams(BaseModel):
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100, description="Numero di elementi da estrarre (1-100)")
    offset: int = Field(0, ge=0, description="Offset iniziale")
    order_by: str = Field("created_at", description="Campo di ordinamento")
    tags: list[str] = Field(default_factory=list, description="Tag di filtro")


@app.get("/items/filter/", tags=["Modulo 3 - Validazioni Avanzate"])
async def read_items_with_filter_model(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
