# Progetto Didattico FastAPI: Replica Live Lesson 🚀

Questo repository contiene la replica completa, fedele e approfondita del progetto didattico presentato nella video-lezione **"FastAPI - Lezione 09: Introduzione a FastAPI"** (`fastapi.mp4`, durata ~85 minuti).

---

## 1. Analisi Dettagliata della Video-Lezione

La lezione introduce l'ecosistema **FastAPI** come moderno framework ad alte prestazioni per Python basato su **Starlette**, **Pydantic** e lo standard ASGI con **Uvicorn**, focalizzandosi sull'inferenza automatica dei tipi e la generazione istantanea della documentazione interattiva OpenAPI (**Swagger UI** a `/docs` e **ReDoc** a `/redoc`).

Il percorso didattico affrontato nel video si articola in tre stadi evolutivi:

### 1. Fondamenti di Routing, Path Parameters e Query Parameters (`main_old.py`)
- **Root Endpoint**: inizializzazione dell'app e definizione di `@app.get("/")`.
- **Path Parameters**: dichiarazione di parametri dinamici tipizzati (`item_id: int`) con conversione e validazione automatica (errore HTTP `422 Unprocessable Entity` se il tipo non corrisponde).
- **Ordine di precedenza degli Endpoint**: i percorsi statici devono sempre precedere quelli dinamici (es. `@app.get("/users/me")` prima di `@app.get("/users/{user_id}")` per evitare che la stringa `"me"` venga catturata come ID utente).
- **Valori Predefiniti con Enum**: utilizzo di `class ModelName(str, Enum)` per limitare i valori ammessi nell'URL a un set controllato (`alexnet`, `resnet`, `lenet`), con generazione automatica del menu a tendina in Swagger UI.
- **Parametri per percorsi file**: utilizzo del convertitore `:path` (`/files/{file_path:path}`) per gestire percorsi completi contenenti slash.
- **Query Parameters**:
  - Paginazione con valori di default (`skip: int = 0`, `limit: int = 10`).
  - Parametri opzionali (`q: str | None = None`).
  - Conversione automatica di tipi booleani (`short: bool = False`), interpretando in modo robusto valori truthy (`1`, `true`, `on`, `yes`).
  - Parametri obbligatori (`needy: str`, senza valore di default).
  - Combinazione multipla di Path e Query parameters (`/users/{user_id}/items/{item_id}`).

### 2. Request Body e Validazione con Pydantic (`main_rb.py`)
- Creazione di schemi dati estendendo `pydantic.BaseModel` (`Item`).
- Gestione di richieste HTTP `POST` con parsing automatico del body JSON.
- Manipolazione dei campi con `.model_dump()` e calcolo di attributi derivati (es. `price_with_tax = price + tax`).
- Combinazione simultanea all'interno dello stesso endpoint (`PUT /items/{item_id}`):
  - **Path Parameter**: `item_id: int`
  - **Request Body**: `item: Item`
  - **Query Parameter**: `q: str | None = None`

### 3. Validazioni Avanzate e Sicurezza con Modelli Query (`main.py`)
- Sintassi moderna con `typing.Annotated`.
- **Validazioni su Query Parameters con `Query`**:
  - Lunghezza minima e massima (`min_length=3`, `max_length=50`).
  - Espressioni regolari per validazione stringhe (`pattern="^fixedquery$"`).
- **Validazioni su Path Parameters con `Path`**:
  - Restrizioni numeriche (`ge=1`, `le=1000`) e metadati (`title`, `description`).
- **Modelli Pydantic per Query Parameters (`FilterParams`)**:
  - Raggruppamento di parametri correlati (`limit`, `offset`, `order_by`, `tags: list[str]`).
  - **Protezione di sicurezza con `model_config = {"extra": "forbid"}`**: blocco preventivo di qualsiasi parametro query non autorizzato, scatenando un errore 422 (*"Extra inputs are not permitted"*) per evitare injection o comportamenti anomali.

---

## 2. Struttura del Progetto

```text
fastapi/
│
├── src/
│   └── fastapilive/
│       ├── __init__.py
│       ├── main_old.py            # Modulo 1: Routing base, Path parameters, Enums, File paths, Query params
│       ├── main_rb.py             # Modulo 2: Request Body con Pydantic (POST / PUT con calcolo tasse)
│       └── main.py                # Modulo 3: Validazioni con Annotated, Query, Path e FilterParams (extra='forbid')
│
├── main.py                        # Master Application unificata che integra tutti gli endpoint della lezione
├── test_api.py                    # Suite di test automatizzati (TestClient) con 12 casi di verifica
├── requirements.txt               # Dipendenze (fastapi, uvicorn, pydantic, httpx, pytest)
├── .gitignore                     # Esclusione di .venv, __pycache__, video *.mp4 ed env
└── README.md                      # Questa documentazione
```

---

## 3. Installazione e Avvio

### Prerequisiti
Tutte le dipendenze necessarie sono già installate nell'ambiente Python. Se necessario:
```powershell
pip install -r requirements.txt
```

### Avvio dell'Applicazione Unificata
```powershell
cd C:\Users\hushe\specializzazione\Esercizi\fastapi
uvicorn main:app --reload
```
Una volta avviato, visita:
- **Swagger UI Interattivo**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Avvio dei Singoli Moduli Didattici (come nel video)
- **Modulo 1 (Routing & Parametri)**:
  ```powershell
  uvicorn src.fastapilive.main_old:app --reload
  ```
- **Modulo 2 (Request Body & Pydantic)**:
  ```powershell
  uvicorn src.fastapilive.main_rb:app --reload
  ```
- **Modulo 3 (Validazioni Avanzate & FilterParams)**:
  ```powershell
  uvicorn src.fastapilive.main:app --reload
  ```

---

## 4. Esecuzione dei Test Automatizzati

È inclusa una suite completa di test unitari e di integrazione che verifica il corretto funzionamento di ogni endpoint e i relativi status code (`200 OK`, `422 Unprocessable Entity`):

```powershell
python test_api.py
```
oppure con pytest:
```powershell
pytest test_api.py -v
```

Output atteso:
```text
============================================================
AVVIO SUITE DI TEST FASTAPI...
============================================================
[OK] test_root passed
[OK] test_users_order_precedence passed
[OK] test_models_enum passed
[OK] test_file_path_converter passed
[OK] test_items_pagination passed
[OK] test_boolean_query_conversion passed
[OK] test_required_query_param passed
[OK] test_create_item_post passed
[OK] test_update_item_put passed
[OK] test_query_validation passed
[OK] test_path_validation passed
[OK] test_filter_params_and_extra_forbid passed
============================================================
TUTTI I TEST SUPERATI CON SUCCESSO!
============================================================
```

---

## 5. Mappa degli Endpoint Implementati

| Metodo | Percorso | Modulo | Descrizione |
|---|---|---|---|
| `GET` | `/` | 1 | Root endpoint con messaggio di benvenuto e link alla documentazione |
| `GET` | `/users/me` | 1 | Endpoint statico per l'utente corrente (precedenza su `{user_id}`) |
| `GET` | `/users/{user_id}` | 1 | Endpoint dinamico con path parameter stringa |
| `GET` | `/models/{model_name}` | 1 | Path parameter vincolato a Enum (`alexnet`, `resnet`, `lenet`) |
| `GET` | `/files/{file_path:path}` | 1 | Path parameter con convertitore di percorso file completo |
| `GET` | `/items/list` | 1 | Query parameters con paginazione (`skip`, `limit`) |
| `GET` | `/items/details/{item_id}` | 1 | Query parameter con conversione booleana automatica (`short`) |
| `GET` | `/items/required/{item_id}` | 1 | Query parameter obbligatorio (`needy`) |
| `GET` | `/users/{user_id}/items/{item_id}` | 1 | Combinazione multipla di Path e Query parameters |
| `POST` | `/items/` | 2 | Creazione risorsa con Pydantic `Item` e calcolo di `price_with_tax` |
| `PUT` | `/items/update/{item_id}` | 2 | Combinazione simultanea di Path Parameter + Request Body + Query |
| `GET` | `/items/validate_query/` | 3 | Query validation con `Annotated` e `Query` (`min_length`, regex `pattern`) |
| `GET` | `/items/validate_path/{item_id}` | 3 | Path validation con `Annotated` e `Path` (`ge=1`, `le=1000`) |
| `GET` | `/items/filter/` | 3 | Modello Pydantic `FilterParams` per query params con `extra='forbid'` |
