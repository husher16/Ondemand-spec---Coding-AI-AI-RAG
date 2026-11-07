# 🌍 Travel Agent API - Assistente di Viaggio Intelligente

Benvenuti nel repository del **Travel Agent API**, il progetto finale sviluppato per la **Specializzazione Coding AI**.

Il sistema è un assistente di viaggio conversazionale autonomo basato su architettura **ReAct (Reasoning + Acting)** sviluppato con **FastAPI**, **LangChain**, **LangGraph** e **OpenAI GPT-4o**, integrato con **SerpApi** (Google Flights e Google Hotels) e predisposto per dialogare in tempo reale con il frontend **Laravel Livewire**.

---

## 📋 Indice dei Contenuti
- [Caratteristiche Principali](#-caratteristiche-principali)
- [Architettura del Sistema](#-architettura-del-sistema)
- [Struttura del Progetto](#-struttura-del-progetto)
- [Installazione e Setup](#-installazione-e-setup)
  - [Prerequisiti](#prerequisiti)
  - [Gestione Dipendenze con Poetry](#gestione-dipendenze-con-poetry)
  - [Configurazione Variabili d'Ambiente (.env)](#configurazione-variabili-dambiente-env)
- [Personalizzazioni e Refactoring](#-personalizzazioni-e-refactoring)
  - [1. Tracing Dettagliato dell'Esecuzione](#1-tracing-dettagliato-dellesecuzione)
  - [2. Compatibilità Doppio Formato (Laravel & Swagger)](#2-compatibilit%C3%A0-doppio-formato-laravel--swagger)
  - [3. Gestione Modalità Operativa (API_MODE: test / prod)](#3-gestione-modalit%C3%A0-operativa-api_mode-test--prod)
  - [4. Endpoint di Healthcheck e Diagnostica](#4-endpoint-di-healthcheck-e-diagnostica)
  - [5. Resilienza e Fallback degli Strumenti](#5-resilienza-e-fallback-degli-strumenti)
- [Tools dell'Agente](#-tools-dellagente)
- [Avvio dei Servizi](#-avvio-dei-servizi)
  - [Avvio Backend FastAPI](#avvio-backend-fastapi)
  - [Avvio Frontend Laravel](#avvio-frontend-laravel)
- [Esecuzione dei Test Automatizzati](#-esecuzione-dei-test-automatizzati)
- [Esempi di Utilizzo e Prompt di Test](#-esempi-di-utilizzo-e-prompt-di-test)

---

## 🚀 Caratteristiche Principali

1. **Ricerca Voli Intelligente**: Integrazione con le API di Google Flights tramite SerpApi per ricercare voli andata/ritorno, orari, compagnie aeree e prezzi migliori.
2. **Ricerca Hotel**: Integrazione con Google Hotels via SerpApi con filtraggio per numero di stelle, date di soggiorno, ospiti e servizi inclusi.
3. **Pianificazione Itinerari Strutturati**: Generazione di itinerari di viaggio dettagliati giorno per giorno (mattina, pomeriggio, sera) con output rigorosamente validato tramite Pydantic.
4. **Esperto Storico e Culturale**: Approfondimenti storici e curiosità culturali sulle città visitate per arricchire l'esperienza di viaggio.
5. **Interfaccia Web Interattiva**: Integrazione completa con il client frontend Laravel Livewire (`web_TravelAgent`).

---

## 🏛️ Architettura del Sistema

```
+-------------------------------------------------------------------+
|               Frontend Client (Laravel Livewire)                  |
|                     http://localhost:8000                         |
+----------------------------------+--------------------------------+
                                   | HTTP POST /chat/travel-agent
                                   v
+-------------------------------------------------------------------+
|               FastAPI Backend (Porta 8080)                        |
|                                                                   |
|   [CORS Middleware] ---> [Chat Router: /chat/travel-agent]       |
|                                   |                               |
|                         [Agent Service]                           |
|                    (LangGraph ReAct Executor)                     |
|                                   |                               |
|       +---------------------------+---------------------------+   |
|       |                           |                           |   |
|       v                           v                           v   |
|  [flights_finder]           [hotels_finder]        [chain_...]   |
|  (Google Flights)          (Google Hotels)        (Plan/History)  |
|       |                           |                           |   |
|       +-------------+-------------+                           |   |
|                     |                                         |   |
+---------------------|-----------------------------------------|---+
                      v                                         v
            +-------------------+                     +-------------------+
            |      SerpApi      |                     |      OpenAI       |
            |  (Google Search)  |                     |     (GPT-4o)      |
            +-------------------+                     +-------------------+
```

---

## 📂 Struttura del Progetto

```text
travel-agent-api/
├── app / travel_agent_api/           # Modulo applicativo principale
│   ├── __init__.py
│   ├── main.py                       # Inizializzazione FastAPI, CORS e routing
│   ├── routes/                       # Endpoint API
│   │   ├── __init__.py
│   │   └── chat_router.py            # POST /chat/travel-agent con schema request
│   ├── services/                     # Logica di orchestrazione
│   │   ├── __init__.py
│   │   └── agent_service.py          # Agente ReAct con LangGraph e prompt di sistema
│   ├── tools/                        # Strumenti operativi dell'agente
│   │   ├── __init__.py
│   │   ├── flights_finder.py         # Tool ricerca voli (SerpApi)
│   │   ├── hotels_finder.py          # Tool ricerca hotel (SerpApi)
│   │   ├── chain_travel_plan.py      # Tool piano di viaggio strutturato (LLM)
│   │   └── chain_historical_expert.py# Tool esperto storico/culturale (LLM)
│   └── utils/
│       ├── __init__.py
│       └── tracing.py                # Utilità per tracing a video con timestamp
├── tests/                            # Test automatizzati (Pytest)
│   ├── __init__.py
│   ├── test_agent.py                 # Test normalizzazione messaggi e logica agente
│   ├── test_api.py                   # Test endpoint FastAPI (/health, /chat/...)
│   └── test_tools.py                 # Test dei 4 tool in modalità isolata
├── docs/                             # Guide PDF e documentazione ufficiale del corso
│   ├── 01. Travel Agent - Introduzione.pdf
│   ├── 02. Travel Agent - Setup del progetto.pdf
│   ├── 03. Travel Agent - API di base.pdf
│   ├── 04. Travel Agent - Tools.pdf
│   ├── 05. Travel Agent - Servizio Agent.pdf
│   └── 06. Travel Agent - Esecuzione.pdf
├── .env.example                      # Template variabili d'ambiente
├── .env                              # Variabili locali (non tracciate su Git)
├── .gitignore                        # Regole di esclusione Git
├── poetry.lock                       # Lock file dipendenze Poetry
├── pyproject.toml                    # Configurazione progetto e dipendenze
└── README.md                         # Documentazione del progetto
```

---

## 🛠️ Installazione e Setup

### Prerequisiti
- **Python**: Versione `>= 3.10` (testato su Python 3.13)
- **Poetry**: Versione `2.x` (o compatibile)

### Gestione Dipendenze con Poetry

Entra nella directory del progetto ed installa le dipendenze:

```bash
cd travel-agent-api
poetry install
```

Per attivare l'ambiente virtuale:
```bash
poetry shell
```

### Configurazione Variabili d'Ambiente (`.env`)

Crea il file `.env` copiando il template fornito:

```bash
cp .env.example .env
```

Configura i valori nel file `.env`:

```ini
# Chiavi API dei servizi esterni
OPENAI_API_KEY="la_tua_openai_api_key"
SERPAPI_API_KEY="la_tua_serpapi_api_key"

# Modalità Operativa:
# - 'test': Utilizza dati mock realistici e logica simulata senza consumare crediti
# - 'prod': Esegue chiamate reali a OpenAI GPT-4o e SerpApi Google Search
API_MODE="test"
```

> [!TIP]
> Impostando `API_MODE="test"` puoi avviare, testare ed esplorare l'intero stack applicativo (incluso il frontend Laravel) anche senza aver ancora configurato una carta di credito o una chiave SerpApi a pagamento!

---

## ✨ Personalizzazioni e Refactoring

Durante lo sviluppo sono state introdotte diverse migliorie architetturali per rendere il sistema più robusto, manutenibile e trasparente:

### 1. Tracing Dettagliato dell'Esecuzione
Per soddisfare pienamente la richiesta di tracciamento dell'esecuzione:
- Sono state inserite le linee di separazione a 80 asterischi (`*` * 80) e il nome della funzione in tutti i punti nevralgici (`chat_completion`, `flights_finder`, `hotels_finder`, `chain_travel_plan`, `chain_historical_expert`).
- È stato introdotto il modulo `travel_agent_api.utils.tracing` con `print_trace()`, che visualizza:
  - Timestamp esatto di ogni invocazione
  - Parametri in ingresso validati
  - Modalità operativa attiva (`test` o `prod`)
  - Tempo di risposta impiegato dal backend (in secondi)
  - Conteggio e tipologia di messaggi scambiati

### 2. Compatibilità Doppio Formato (Laravel & Swagger)
Il client frontend in Laravel Livewire invia i messaggi nel formato:
```json
[{"type": "human", "content": "Vorrei info su Parigi"}]
```
Mentre la documentazione Swagger UI / OpenAI usa comunemente:
```json
[{"role": "user", "content": "Vorrei info su Parigi"}]
```
Nel metodo `Agent._normalize_messages()`, tutti i messaggi vengono convertiti trasparentemente, garantendo che sia l'interfaccia web Laravel che i test da Swagger UI (`/docs`) funzionino perfettamente senza generare errori di parsing.

### 3. Gestione Modalità Operativa (`API_MODE: test / prod`)
Come suggerito nella dispensa didattica (sezione *2.4 Modalità Test/Produzione*):
- In modalità `test` (o se le chiavi non sono ancora inserite), i tool restituiscono dati realistici strutturati fedelmente secondo gli schemi di output attesi (`FLIGHTS_OUTPUT`, `HOTELS_OUTPUT`, `TRAVEL_PLAN_OUTPUT`).
- In modalità `prod`, vengono effettuate le chiamate reali via rete a OpenAI e SerpApi.

### 4. Endpoint di Healthcheck e Diagnostica
Sono stati aggiunti due endpoint di utilità per verificare istantaneamente lo stato del backend:
- `GET /`: informazioni sul servizio e link alla documentazione OpenAPI.
- `GET /health`: stato di integrità dell'API e verifica rapida se le chiavi `OPENAI_API_KEY` e `SERPAPI_API_KEY` sono valorizzate.

### 5. Resilienza e Fallback degli Strumenti
Nei tool `flights_finder` e `hotels_finder`, in caso di errore temporaneo di connessione o quota esaurita su SerpApi, il sistema esegue un fallback morbido con avviso nel tracing invece di causare un crash 500 dell'intera conversazione.

---

## 🧰 Tools dell'Agente

| Tool | Scopo | Parametri Principali | Output |
| :--- | :--- | :--- | :--- |
| `flights_finder` | Ricerca voli con Google Flights via SerpApi | `departure_airport`, `arrival_airport`, `outbound_date`, `return_date`, `adults`, `children` | Dizionario con `best_flights`, tariffe, vettori, link di prenotazione |
| `hotels_finder` | Ricerca strutture ricettive via SerpApi | `q` (località), `check_in_date`, `check_out_date`, `adults`, `hotel_class` | Lista di strutture con prezzi per notte/totali, recensioni e foto |
| `chain_travel_plan` | Genera itinerari giorno per giorno | `destination`, `start_date`, `end_date`, `travel_style`, `budget`, `activities` | Oggetto `TravelPlanOutput` con attività divise in Mattina, Pomeriggio, Sera |
| `chain_historical_expert` | Fornisce contenuti storici e artistici | `input_text` (argomento / monumento) | Testo descrittivo approfondito e arricchito con emoji |

---

## 🚀 Avvio dei Servizi

### Avvio Backend FastAPI

Avvia il server FastAPI sulla porta `8080`:

```bash
poetry run uvicorn travel_agent_api.main:app --reload --port 8080
```

Il backend sarà disponibile su:
- **API Base**: `http://127.0.0.1:8080/`
- **Documentazione Swagger UI**: `http://127.0.0.1:8080/docs`
- **Documentazione ReDoc**: `http://127.0.0.1:8080/redoc`

### Avvio Frontend Laravel

In una nuova finestra del terminale:

```bash
cd ../web_TravelAgent
php artisan serve
```

E in un altro terminale (per gli asset grafici di Vite):
```bash
cd ../web_TravelAgent
npm run dev
```

Accedi all'interfaccia utente nel browser su:
👉 **`http://127.0.0.1:8000`**

---

## 🧪 Esecuzione dei Test Automatizzati

Il progetto include una suite completa di test con **pytest** che verifica l'isolamento dei tool, la serializzazione dell'agente e la risposta degli endpoint FastAPI:

```bash
# Esecuzione standard
poetry run pytest

# Esecuzione con visualizzazione completa dei log di tracing a console
poetry run pytest -s
```

Tutti i test vengono eseguiti con successo:
```text
tests/test_agent.py ..                                                   [ 20%]
tests/test_api.py ....                                                   [ 60%]
tests/test_tools.py ....                                                 [100%]

============================= 10 passed in 1.13s ==============================
```

---

## 💬 Esempi di Utilizzo e Prompt di Test

Puoi testare l'assistente inserendo questi prompt direttamente nella chat del frontend o su Swagger UI (`/docs`):

### 1. Ricerca Voli (`flights_finder`)
> *"Cerco voli da FCO (Roma) a CDG (Parigi) per due adulti e un bambino, partenza 5 luglio 2024 e ritorno 12 luglio 2024."*

### 2. Ricerca Hotel (`hotels_finder`)
> *"Cerco un hotel 4 stelle nel centro di Roma per due adulti dal 15 al 20 maggio 2024."*

### 3. Pianificazione Itinerario (`chain_travel_plan`)
> *"Vorrei organizzare un viaggio a Venezia dal 15 al 20 giugno 2024. Siamo una coppia, cerchiamo un'esperienza culturale con focus sull'arte e la cucina locale. Budget di 2000€, no restrizioni alimentari."*

### 4. Approfondimento Storico e Culturale (`chain_historical_expert`)
> *"Raccontami la storia dell'antica Roma, concentrandoti in particolare sull'influenza che ha avuto sulla moderna civiltà italiana."*

---

## 👨‍💻 Autore
- **Danut Frunza** - Specializzazione Coding AI (Aulab)
