"""
Modulo 2: Request Body e Validazione Dati con Modelli Pydantic.
Replica esatta della seconda parte della video-lezione.
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="FastAPI Live - Modulo 2: Request Body & Pydantic",
    description="Esempi didattici di Request Body (POST/PUT) con modelli Pydantic e calcolo campi derivati"
)


# 1. Definizione dello Schema Dati con Pydantic BaseModel
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.get("/")
async def root():
    return {"message": "Hello World - Request Body Module"}


# 2. Creazione di Risorse tramite POST e Request Body
@app.post("/items/")
async def create_item(item: Item):
    """
    Riceve un payload JSON validato automaticamente da Pydantic:
    - Se price non è float/int valido -> errore 422 con dettaglio preciso del campo.
    - Converte il modello in dizionario tramite .model_dump().
    - Se presente il campo tax, calcola price_with_tax aggiungendolo alla risposta.
    """
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


# 3. Combinazione Simultanea di: Path Parameter + Request Body + Query Parameter
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, q: str | None = None):
    """
    FastAPI riconosce automaticamente il ruolo di ciascun parametro:
    - item_id: dichiarato nel percorso URL -> Path Parameter
    - item: eredita da BaseModel -> Request Body (JSON)
    - q: tipo primitivo non presente nel percorso -> Query Parameter opzionale
    """
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
