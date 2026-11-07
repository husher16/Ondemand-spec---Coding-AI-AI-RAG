import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
from openai import OpenAI

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Caricamento delle variabili d'ambiente dal file .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_KEY = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")

# Definizione dei Tools a disposizione dell'assistente:
# 1. Funzione personalizzata (Function Calling) per invio email
# 2. Strumento nativo File Search (RAG vettoriale gestito da OpenAI)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Invia un'email di benvenuto, brochure tecnica e proposta di noleggio personalizzata al potenziale cliente che ne fa esplicita richiesta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nome e cognome del potenziale cliente"
                    },
                    "email": {
                        "type": "string",
                        "description": "Indirizzo email valido del potenziale cliente"
                    }
                },
                "required": ["name", "email"]
            }
        }
    },
    {
        "type": "file_search"
    }
]

def create_new_assistant():
    """
    Crea e configura programmaticamente l'assistente virtuale su OpenAI:
    - Imposta il nome, il modello e le istruzioni di sistema (System / Developer Prompt)
    - Crea un Vector Store dedicato per i documenti aziendali
    - Carica e indicizza i file della knowledge base (kb/)
    - Collega il Vector Store all'assistente tramite tool_resources
    - Salva l'ASSISTANT_ID generato nel file .env
    """
    if not OPENAI_KEY or OPENAI_KEY.startswith("inserisci"):
        print("\n[ERRORE] Chiave OPENAI_API_KEY non configurata o non valida nel file .env!")
        print(f"Percorso file .env: {env_path}")
        print("Inserisci una chiave API OpenAI valida prima di eseguire questo script.\n")
        return None

    client = OpenAI(api_key=OPENAI_KEY)

    print("[INFO] Inizio procedura di creazione e configurazione assistente OpenAI...")

    # Step 1: Creazione dell'assistente base con istruzioni dettagliate
    instructions = """
Il tuo nome è Elena.
Sei la consulente virtuale senior e specialista della mobilità elettrica per l'azienda Nexura EV Mobility Italia.
Il tuo obiettivo è assistere i clienti (privati, professionisti con Partita IVA e gestori di flotte aziendali) a scoprire i vantaggi dei nostri veicoli 100% elettrici, dei piani di noleggio a lungo termine "Guida Senza Pensieri" e dei servizi di ricarica.

Linee guida operative:
1. Utilizza SEMPRE le informazioni fornite nei documenti aziendali della tua Knowledge Base (catalogo veicoli, tariffe, politiche e incentivi) per rispondere in modo preciso, autorevole e veritiero.
2. Mantieni un tono professionale, empatico, accogliente e orientato alla consulenza consulenziale.
3. Se un cliente chiede dettagli su modelli, autonomie, potenze di ricarica, canoni o installazione della Wallbox domestica, rispondi con chiarezza citando i dati ufficiali.
4. Quando un cliente manifesta interesse per una brochure, scheda tecnica o preventivo, chiedi cortesemente il suo NOME e il suo INDIRIZZO EMAIL.
5. Quando il cliente condivide il proprio INDIRIZZO EMAIL e il proprio NOME, INVIA loro l'email chiamando immediatamente il tool 'send_email'.
6. RICORDA DI INVIARE L'EMAIL SOLO ED ESCLUSIVAMENTE QUANDO SEI IN POSSESSO DI ENTRAMBI I DATI (NOME ED EMAIL).
7. Dopo aver invocato il tool, rassicura il cliente confermando che il materiale informativo è stato spedito e offriti per ulteriori chiarimenti o per organizzare un test-drive gratuito.
"""

    model_name = os.getenv("OPENAI_MODEL", "gpt-4o")

    print(f"1. Creazione assistente '{model_name}'...")
    assistant = client.beta.assistants.create(
        name="Elena - Nexura EV Mobility Assistant",
        instructions=instructions.strip(),
        tools=TOOLS,
        model=model_name,
        temperature=0.3
    )
    print(f"   [OK] Assistente creato con ID: {assistant.id}")

    # Step 2: Creazione del Vector Store
    print("2. Creazione del Vector Store dedicato su OpenAI...")
    vector_store = client.beta.vector_stores.create(
        name="Nexura EV Mobility Knowledge Base"
    )
    print(f"   [OK] Vector Store creato con ID: {vector_store.id}")

    # Step 3: Preparazione e caricamento dei file della Knowledge Base
    base_dir = Path(__file__).resolve().parent.parent
    kb_dir = base_dir / "kb"
    file_paths = [
        kb_dir / "catalogo_veicoli_e_tariffe.txt",
        kb_dir / "politiche_servizi_e_incentivi.txt"
    ]

    print("3. Caricamento e indicizzazione file della knowledge base...")
    file_streams = []
    for fp in file_paths:
        if fp.exists():
            print(f"   - Apertura file: {fp.name}")
            file_streams.append(open(fp, "rb"))
        else:
            print(f"   [AVVISO] File non trovato: {fp}")

    if not file_streams:
        print("[ERRORE] Nessun file trovato nella cartella kb/. Interruzione.")
        return assistant

    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=file_streams
    )

    for fs in file_streams:
        fs.close()

    print(f"   [OK] File batch status: {file_batch.status} ({file_batch.file_counts.completed} file indicizzati)")

    # Step 4: Collegamento del Vector Store all'assistente tramite tool_resources
    print("4. Collegamento del Vector Store all'assistente...")
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store.id]
            }
        }
    )
    print("   [OK] Assistente aggiornato con successo.")

    # Step 5: Salvataggio automatico dell'ASSISTANT_ID nel file .env
    try:
        set_key(str(env_path), "ASSISTANT_ID", assistant.id)
        print("5. [OK] ASSISTANT_ID salvato automaticamente nel file .env!")
    except Exception as e:
        print(f"   [AVVISO] Impossibile salvare automaticamente nel file .env ({e}).")
        print(f"   Aggiungi manualmente nel file .env: ASSISTANT_ID={assistant.id}")

    print("\n" + "=" * 60)
    print("PROCEDURA COMPLETATA CON SUCCESSO!")
    print(f"Nome Assistente: {assistant.name}")
    print(f"ID Assistente  : {assistant.id}")
    print(f"Vector Store ID: {vector_store.id}")
    print("Puoi ora avviare Chainlit con il comando:")
    print("  chainlit run app.py -w")
    print("=" * 60 + "\n")

    return assistant


if __name__ == "__main__":
    create_new_assistant()
