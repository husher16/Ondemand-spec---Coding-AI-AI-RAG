# 🌟 Progetto Finale: Travel Agent AI

Questo repository contiene il **Progetto Finale della Specializzazione Coding AI** (Aulab).

Il progetto è composto da:
1. **`travel-agent-api/`**: Applicazione backend in **Python**, **FastAPI**, **LangChain** e **LangGraph**, dotata di agenti autonomi, 4 tools integrati (Google Flights, Google Hotels, Travel Plan, Historical Expert), tracing dettagliato dell'esecuzione, test automatizzati con `pytest` e documentazione Swagger.
2. **`web_TravelAgent/`**: Client frontend sviluppato con **Laravel** e **Livewire**, che fornisce un'interfaccia chat reattiva collegata in tempo reale con il backend FastAPI sulla porta `8080`.
3. **`docs/`**: Guide PDF originali del progetto che illustrano l'architettura, la configurazione e i casi d'uso.

---

## 🚀 Istruzioni Rapide di Avvio

### 1. Avviare il Backend Python (FastAPI + LangChain)
```bash
cd travel-agent-api
poetry install
poetry run uvicorn travel_agent_api.main:app --reload --port 8080
```
- Swagger UI disponibile su: `http://127.0.0.1:8080/docs`

### 2. Avviare il Frontend Web (Laravel Livewire)
In un altro terminale:
```bash
cd web_TravelAgent
php artisan serve
```
- Client web accessibile su: `http://127.0.0.1:8000`

Per ulteriori dettagli tecnici, architettura, tracing e test, fare riferimento al file [travel-agent-api/README.md](travel-agent-api/README.md).
