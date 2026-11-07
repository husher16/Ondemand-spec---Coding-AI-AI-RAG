"""
Script da riga di comando per testare l'assistente virtuale direttamente da terminale.

Utilizzo:
    python main.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

from virtual_assistant.chat_logic import ChatLogic

def run_cli():
    print("=" * 60)
    print("[NEXURA EV MOBILITY] Test Assistente Virtuale (CLI)")
    print("=" * 60)

    openai_key = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    resend_key = os.getenv("RESEND_KEY")
    assistant_id = os.getenv("ASSISTANT_ID")

    print("Stato Configurazione:")
    print(f" - OPENAI_API_KEY : {'Presente' if openai_key and not openai_key.startswith('inserisci') else 'Non configurata'}")
    print(f" - RESEND_KEY     : {'Presente' if resend_key and not resend_key.startswith('inserisci') else 'Non configurata (modalita simulata attiva)'}")
    print(f" - ASSISTANT_ID   : {assistant_id or 'Non configurato'}")
    print("=" * 60)

    if not openai_key or openai_key.startswith("inserisci"):
        print("\nAttenzione: OPENAI_API_KEY non e impostata nel file .env.")
        print("Per creare l'assistente ed effettuare chiamate reali:")
        print("  1. Inserisci la tua API key nel file .env")
        print("  2. Esegui: python virtual_assistant/create_assistant.py")
        print("  3. Riavvia questo script oppure avvia: chainlit run app.py -w\n")
        return

    if not assistant_id:
        print("\nASSISTANT_ID non trovato nel file .env.")
        print("Esegui prima lo script di creazione dell'assistente:")
        print("  python virtual_assistant/create_assistant.py\n")
        return

    chat_logic = ChatLogic(
        openai_key=openai_key,
        resend_key=resend_key,
        assistant_id=assistant_id
    )

    print("\nInizializzazione sessione e thread...")
    tid = chat_logic.initialize_thread()
    print(f"Thread attivo: {tid}")
    print("Digita 'esci' o 'quit' per terminare la chat.\n")

    while True:
        try:
            user_input = input("Utente > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["esci", "quit", "exit"]:
                print("Chiusura sessione...")
                break

            print("\nElena sta elaborando...")
            response = chat_logic.process_message(user_input)
            print(f"\nElena > {response}\n")

        except KeyboardInterrupt:
            print("\nSessione interrotta.")
            break
        except Exception as e:
            print(f"\n[Errore]: {e}\n")

if __name__ == "__main__":
    run_cli()
