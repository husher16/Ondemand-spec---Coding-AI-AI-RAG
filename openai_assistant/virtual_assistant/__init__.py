import os
from pathlib import Path
from dotenv import load_dotenv
import chainlit as cl

# Gestione import robusta sia per esecuzione come package che come modulo diretto
try:
    from .chat_logic import ChatLogic
except ImportError:
    from chat_logic import ChatLogic

# Caricamento delle variabili d'ambiente dal file .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configurazione delle chiavi API e ID necessari
OPENAI_KEY = os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
RESEND_KEY = os.getenv("RESEND_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")


@cl.on_chat_start
async def on_chat_start():
    """
    Inizializza una nuova sessione di chat:
    - Istanzia l'oggetto ChatLogic con le credenziali di ambiente e l'ID dell'assistente
    - Salva l'istanza in cl.user_session per preservare il thread e lo stato della conversazione
    - Invia un messaggio introduttivo accogliente all'utente
    """
    chat_logic = ChatLogic(
        openai_key=OPENAI_KEY,
        resend_key=RESEND_KEY,
        assistant_id=ASSISTANT_ID
    )
    cl.user_session.set("chat_logic", chat_logic)

    welcome_message = (
        "🚗⚡ **Benvenuto in Nexura EV Mobility Italia!**\n\n"
        "Sono **Elena**, la tua consulente virtuale per la mobilità elettrica a emissioni zero. "
        "Posso fornirti informazioni dettagliate su:\n"
        "- 📋 **Catalogo Veicoli Elettrici**: specifiche tecniche, autonomie e prestazioni (*CityOne*, *Horizon GT*, *CargoPro*);\n"
        "- 💶 **Piani di Noleggio a Lungo Termine**: tariffe mensili, anticipo zero e coperture KASKO incluse;\n"
        "- 🔌 **Infrastruttura di Ricarica**: installazione Wallbox domestica gratuita e Nexura SuperCharge Card;\n"
        "- 📩 **Invio Brochure e Preventivi**: posso inviarti tutta la documentazione via email in tempo reale!\n\n"
        "*Come posso aiutarti oggi?*"
    )
    await cl.Message(author="Elena - Nexura Assistant", content=welcome_message).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Gestisce ogni nuovo messaggio ricevuto dall'utente nella chat Chainlit:
    1. Estrae il testo del messaggio dell'utente
    2. Recupera l'istanza ChatLogic dalla sessione
    3. Elabora il messaggio chiamando chat_logic.process_message()
    4. Invia la risposta finale dell'assistente nella chat
    """
    user_message = message.content

    # Recupera l'istanza di ChatLogic dalla sessione
    chat_logic: ChatLogic = cl.user_session.get("chat_logic")

    if not chat_logic:
        await cl.Message(
            author="System",
            content="Errore di sessione: ChatLogic non inizializzato. Ricarica la pagina."
        ).send()
        return

    # Processa il messaggio tramite l'assistente OpenAI (gestisce thread, run e function calls)
    response = chat_logic.process_message(user_message)

    # Invia la risposta finale dell'assistente
    await cl.Message(
        author="Elena - Nexura Assistant",
        content=response or "Nessuna risposta disponibile."
    ).send()
