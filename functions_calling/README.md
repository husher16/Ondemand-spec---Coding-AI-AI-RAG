# Progetto Function Calling - AI & Tech Innovation Academy

Questo progetto replica l'architettura di **OpenAI Function Calling / Tools** e l'interfaccia **Chainlit** presentata nella video-lezione, applicata al dominio dell'**Accademia di Intelligenza Artificiale e Sviluppo Software**.

---

## Architettura del Progetto

1. **`tools/tools.py`**:
   - `CourseInfoTool`: Ricerca dettagliata sui corsi di specializzazione (prezzo, durata, programma).
   - `ScheduleTool`: Consultazione delle date di avvio delle classi e verifica posti disponibili.
   - `BookingTool`: Controllo disponibilità e prenotazione videochiamate 1-to-1 con docenti e mentor tecnici.

2. **`tools/__init__.py`**:
   - Definizione del catalogo dei tool in formato OpenAI JSON Schema (`TOOLS`).
   - Funzione di dispatch `handle_tool_call` per l'esecuzione locale.
   - Gestione sessione e ciclo di conversazione con Chainlit (`@cl.on_chat_start`, `@cl.on_message`).
   - Ciclo agentico: invocazione tool -> esecuzione codice Python -> invio output tool a OpenAI -> generazione risposta finale all'utente.

3. **`app.py`**:
   - Entry point standard per Chainlit.

4. **`main.py`**:
   - Script per eseguire test diagnostici locali dei tool o simulare la chat completa da terminale.

---

## Configurazione ed Esecuzione

### 1. Attivazione del Virtual Environment
```powershell
cd C:\Users\hushe\specializzazione\Esercizi\functions_calling
.\.venv\Scripts\Activate.ps1
```

### 2. Configurazione Variabili d'Ambiente
Copia il file `.env.example` in `.env` e imposta la tua chiave OpenAI:
```ini
OPENAI_API_KEY=sk-...
```

### 3. Esecuzione Test Locale da Terminale
```powershell
.\.venv\Scripts\python main.py
```

### 4. Avvio dell'Interfaccia Grafica Web (Chainlit)
Come mostrato nella video-lezione:
```powershell
.\.venv\Scripts\chainlit run app.py -w
```
oppure:
```powershell
.\.venv\Scripts\chainlit run tools/__init__.py -w
```
L'interfaccia sarà accessibile nel browser su `http://localhost:8000`.
