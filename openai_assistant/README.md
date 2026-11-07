# Progetto OpenAI Assistant: Nexura EV Mobility Italia 🚗⚡

Questo repository contiene la replica e l'approfondimento completo del progetto didattico presentato nella video-lezione **"OpenAI Assistant"** (`openai_assistant.mp4`), applicato a un dominio aziendale su misura: **Nexura EV Mobility Italia**, società specializzata nel noleggio a lungo termine di veicoli 100% elettrici, soluzioni per flotte aziendali e infrastrutture di ricarica intelligente.

---

## 1. Analisi Dettagliata della Video-Lezione

Dall'analisi del video (`openai_assistant.mp4`, durata ~20 minuti), emergono i seguenti pilastri concettuali e architetturali:

1. **Evoluzione da Orchestrazione Manuale a Managed Agents**:
   - Nelle lezioni precedenti, i pattern RAG (Retrieval-Augmented Generation) e Function Calling richiedevano un'orchestrazione manuale (gestione autonoma degli embedding, salvataggio su ChromaDB locale, loop di dispatch manuale).
   - Con le **OpenAI Assistants API (v2)**, OpenAI fornisce un framework unificato ad alto livello in cui il modello, gli strumenti esterni (Tools), la memoria di contesto (Threads) e le basi di conoscenza documentali (Vector Stores & File Search) sono integrati all'interno di una singola entità gestita.

2. **Gestione dello Stato tramite Threads**:
   - Non è più necessario salvare e serializzare lo storico dei messaggi in memoria o su database relazionali: l'oggetto **Thread** mantiene la cronologia completa della conversazione sul server OpenAI in modo sicuro e persistente.
   - In Chainlit, l'istanza `ChatLogic` viene salvata all'interno di `cl.user_session`, consentendo a ciascun utente connesso di conservare il proprio `thread_id` per tutta la durata della sessione.

3. **Knowledge Base e Vector Stores Automatici**:
   - L'assistente sfrutta la risorsa `file_search`.
   - I file di testo o PDF del dominio applicativo vengono caricati tramite `client.beta.vector_stores.file_batches.upload_and_poll`, che esegue automaticamente chunking, calcolo degli embedding e indicizzazione vettoriale.
   - Il vector store viene quindi associato all'assistente tramite `tool_resources={"file_search": {"vector_store_ids": [...]}}`.

4. **Ciclo di Vita del Run e Invocazione Tool (Function Calling)**:
   - Quando viene inviato un messaggio nel thread, si avvia un'esecuzione con `client.beta.threads.runs.create_and_poll()`.
   - Il run attraversa vari stati (`queued`, `in_progress`, `requires_action`, `completed`).
   - Se il modello riconosce l'intenzione di invocare una funzione (es. inviare un'email), entra nello stato **`requires_action`**:
     1. Il codice client intercetta i `tool_calls`.
     2. Esegue la funzione Python locale (nel video, l'integrazione con le API di **Resend**).
     3. Restituisce il risultato ad OpenAI tramite `submit_tool_outputs_and_poll()`.
   - Una volta completato (`completed`), si recuperano i messaggi con `threads.messages.list()` per estrarre la risposta dell'assistente.

5. **Principio dell'Information Radiator (Configurazione Programmatica)**:
   - Il docente sottolinea l'importanza di creare l'assistente **via codice** (`create_assistant.py`) piuttosto che limitarsi a configurarlo manualmente dal Playground web di OpenAI. Questo garantisce versionamento, riproducibilità e consistenza tra ambienti.

---

## 2. Dominio del Progetto: Nexura EV Mobility Italia

L'assistente virtuale si chiama **Elena** ed è la consulente commerciale e tecnica per **Nexura EV Mobility Italia**.

### Funzionalità Implementate:
- **RAG Aziendale**: Risponde accuratamente su autonomia, capacità delle batterie, potenze di ricarica (800V, Ultra-DC), canoni mensili, servizi inclusi (KASKO, manutenzione, pneumatici) e installazione gratuita della Wallbox domestica intelligente con bilanciamento carichi.
- **Function Calling (Invio Email)**: Quando l'utente richiede un preventivo, brochure o scheda tecnica e fornisce il proprio nome e indirizzo email, l'assistente attiva automaticamente la funzione `send_email` per trasmettere la documentazione ufficiale.
- **Supporto Ibrido Resend / Mock**: Integrazione con la libreria `resend` con gestione trasparente dei vincoli dell'account sandbox (come evidenziato nel video) e fallback simulato nel caso non sia ancora presente una chiave API.

---

## 3. Struttura del Progetto

```text
openai_assistant/
│
├── kb/                                          # Knowledge Base aziendale (documenti di dominio)
│   ├── catalogo_veicoli_e_tariffe.txt           # Schede tecniche (CityOne, Horizon GT, CargoPro) e canoni
│   └── politiche_servizi_e_incentivi.txt        # Dettagli ricarica, Wallbox, requisiti e onboarding
│
├── virtual_assistant/                           # Modulo logico dell'assistente
│   ├── __init__.py                              # Handlers interfaccia Chainlit (@cl.on_chat_start, @cl.on_message)
│   ├── chat_logic.py                            # Classe ChatLogic: gestione Thread, Run, Tools ed Email
│   └── create_assistant.py                      # Provisioning programmatico assistente, Vector Store e file batch
│
├── .chainlit/                                   # Configurazione interfaccia Chainlit
│   └── config.toml
│
├── app.py                                       # Entry point principale per avviare Chainlit
├── main.py                                      # Script di collaudo da linea di comando (CLI)
├── chainlit.md                                  # Landing page informativa della chat
├── requirements.txt                             # Dipendenze Python (openai, chainlit, resend, python-dotenv)
├── .env.example                                 # Modello per le variabili d'ambiente
├── .env                                         # File variabili d'ambiente locali (chiavi API e ASSISTANT_ID)
└── README.md                                    # Questa documentazione
```

---

## 4. Guida all'Installazione e Configurazione

### Prerequisiti
- Python 3.10+ (consigliato Python 3.12 o 3.13 già presente nel sistema)
- Una chiave API OpenAI valida (`sk-...`)
- *(Opzionale)* Una chiave API Resend gratuita su [resend.com](https://resend.com)

### 1. Configurazione del file `.env`
Apri il file `C:\Users\hushe\specializzazione\Esercizi\openai_assistant\.env` e inserisci le tue credenziali:

```ini
OPENAI_API_KEY=sk-tuachiaveopenai...
OPENAI_MODEL=gpt-4o

# Opzionale: chiave Resend per invio email reale
RESEND_KEY=re_tuachiaveresend...

# Lascia ASSISTANT_ID vuoto: verrà compilato in automatico dallo script!
ASSISTANT_ID=
```

### 2. Creazione dell'Assistente e del Vector Store
Esegui lo script programmatico:

```powershell
cd C:\Users\hushe\specializzazione\Esercizi\openai_assistant
python virtual_assistant/create_assistant.py
```

**Cosa fa lo script:**
1. Crea l'assistente "Elena" su OpenAI con le istruzioni di sistema e la definizione del tool `send_email` e `file_search`.
2. Crea un **Vector Store** dedicato intitolato `"Nexura EV Mobility Knowledge Base"`.
3. Carica i file da `kb/`, attende il completamento dell'indicizzazione (`upload_and_poll`).
4. Collega il Vector Store all'assistente tramite `tool_resources`.
5. Salva automaticamente il nuovo `ASSISTANT_ID` generato all'interno del file `.env`.

---

## 5. Avvio e Utilizzo dell'Applicazione

### Modalità Grafica Web (Chainlit)
Avvia il server Chainlit con ricaricamento a caldo:

```powershell
chainlit run app.py -w
```

Apri il browser all'indirizzo `http://localhost:8000`.

### Modalità Console (CLI Debugger)
Per verificare rapidamente il funzionamento o testare la logica direttamente da terminale:

```powershell
python main.py
```

---

## 6. Esempi di Conversazione e Scenari di Test

### Scenario 1: Domande su modelli e tariffe (RAG File Search)
> **Utente**: *"Quali modelli di auto elettriche avete a disposizione e quali sono i prezzi di noleggio?"*  
> **Elena**: Consulta i file nella Knowledge Base e illustra i dettagli di **Nexura CityOne** (289 €/mese), **Nexura Horizon GT** (499 €/mese + IVA) e il furgone **CargoPro** (410 €/mese).

### Scenario 2: Domande tecniche e Wallbox domestica (RAG File Search)
> **Utente**: *"Se noleggio la Horizon GT per 36 mesi, posso ricaricarla a casa? La Wallbox è a pagamento?"*  
> **Elena**: Spiega che per contratti da 36 mesi o più, la Wallbox intelligente *Nexura PowerHome 22* con sensore salvacontatore Dynamic Load Management è **inclusa a costo zero**, con installazione e certificazione di conformità (DiCo) comprese.

### Scenario 3: Richiesta di preventivo e attivazione Tool Invio Email (Function Calling)
> **Utente**: *"Mi sembra un'ottima offerta. Vorrei ricevere la brochure completa e un preventivo ufficiale."*  
> **Elena**: Chiede gentilmente all'utente di fornire il proprio **nome** e l'**indirizzo email**.  
> **Utente**: *"Certamente, mi chiamo Marco Rossi e la mia email è marco.rossi@example.com"*  
> **Elena**: 
> 1. Riconosce la presenza di nome ed email.
> 2. Entra in stato `requires_action` e chiama il tool `send_email(name="Marco Rossi", email="marco.rossi@example.com")`.
> 3. Esegue la funzione (tramite Resend o mock sandbox).
> 4. Restituisce all'utente il messaggio finale di conferma con i dettagli del contatto e la disponibilità per un test-drive gratuito a domicilio.
