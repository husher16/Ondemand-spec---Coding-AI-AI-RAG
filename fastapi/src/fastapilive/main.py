"""
Modulo 3: Validazioni Avanzate con Annotated, Query, Path e Modelli Pydantic (FilterParams).
Replica esatta dell'ultima parte della video-lezione.
"""
from typing import Annotated
from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field

app = FastAPI(
    title="FastAPI Live - Modulo 3: Validazioni Avanzate",
    description="Validazioni numeriche, regex su stringhe e raggruppamento query params con FilterParams (extra='forbid')"
)


# 1. Validazione dei Query Parameters con Query e Annotated
# min_length, max_length, espressione regolare (pattern)
@app.get("/items_query_validation/")
async def read_items_query(
    q: Annotated[
        str | None,
        Query(
            min_length=3,
            max_length=50,
            pattern="^fixedquery$",
            description="Query string con validazione di lunghezza minima, massima e pattern esatto"
        )
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


# 2. Validazione dei Path Parameters con Path e Annotated
# Restrizioni numeriche: ge=1 (greater than or equal to 1), le=1000 (less than or equal to 1000)
@app.get("/items/{item_id}")
async def read_items_path(
    item_id: Annotated[
        int,
        Path(
            title="The ID of the item to get",
            description="Identificativo numerico dell'elemento compreso tra 1 e 1000",
            ge=1,
            le=1000
        )
    ]
):
    return {"item_id": item_id}


# 3. Modelli Pydantic per Query Parameters con Field e extra="forbid"
class FilterParams(BaseModel):
    """
    Raggruppa parametri di query correlati all'interno di un unico modello Pydantic.
    La configurazione model_config = {'extra': 'forbid'} rifiuta con errore 422
    qualsiasi parametro non esplicitamente dichiarato, aumentando la sicurezza dell'API.
    """
    model_config = {"extra": "forbid"}

    limit: int = Field(100, gt=0, le=100, description="Massimo numero di risultati da restituire (tra 1 e 100)")
    offset: int = Field(0, ge=0, description="Offset di paginazione (>= 0)")
    order_by: str = Field("created_at", description="Campo su cui ordinare i risultati")
    tags: list[str] = Field(default_factory=list, description="Lista di tag di filtro")


@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    """
    Riceve tutti i parametri di query validati tramite il modello FilterParams.
    Esempio: /items/?limit=10&offset=0&order_by=created_at&tags=python&tags=fastapi
    Se viene inviato un parametro extra (es. ?unknown=123) -> errore 422 'Extra inputs are not permitted'.
    """
    return filter_query
