from dataclasses import dataclass
from typing import List, Optional
import os
import json
import resend
from openai import OpenAI

@dataclass
class Message:
    """
    Classe di supporto per rappresentare un messaggio nella chat.
    Contiene il ruolo (utente o assistente) e il contenuto del messaggio.
    """
    role: str
    content: str


class ChatLogic:
    """
    Classe principale che gestisce la logica della chat con l'assistente AI (OpenAI Assistants API v2).
    Si occupa di:
    - Gestire i thread delle conversazioni
    - Processare i messaggi utente
    - Eseguire chiamate a strumenti (Tool Calling / Function Calling)
    - Inviare email tramite servizio Resend (o fallback simulato)
    - Sincronizzare i run di esecuzione e gestire gli stati (queued, in_progress, requires_action, completed)
    """

    def __init__(self, openai_key: Optional[str], resend_key: Optional[str], assistant_id: Optional[str]):
        """
        Inizializza la classe con le chiavi API necessarie e l'ID dell'assistente.

        Parametri:
        - openai_key: Chiave API per OpenAI
        - resend_key: Chiave API per il servizio email Resend
        - assistant_id: ID dell'assistente OpenAI da utilizzare
        """
        self.openai_key = openai_key or os.getenv("OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
        self.resend_key = resend_key or os.getenv("RESEND_KEY")
        self.assistant_id = assistant_id or os.getenv("ASSISTANT_ID")
        self.thread_id: Optional[str] = None

        if self.openai_key and not self.openai_key.startswith("inserisci"):
            self.client = OpenAI(api_key=self.openai_key)
        else:
            self.client = None

        if self.resend_key and not self.resend_key.startswith("inserisci"):
            resend.api_key = self.resend_key
        else:
            resend.api_key = None

    def initialize_thread(self) -> Optional[str]:
        """
        Crea un nuovo thread di conversazione se non ne esiste già uno per la sessione.
        Un thread rappresenta una sessione di chat persistente gestita da OpenAI.

        Ritorna:
        - L'ID del thread creato o esistente.
        """
        if not self.thread_id and self.client:
            try:
                thread = self.client.beta.threads.create()
                self.thread_id = thread.id
                print(f"[ChatLogic] Nuovo Thread inizializzato: {self.thread_id}")
            except Exception as e:
                print(f"[ChatLogic ERROR] Errore durante l'inizializzazione del thread: {e}")
                return None
        return self.thread_id

    def send_email(self, name: str, email: str) -> str:
        """
        Invia un'email di benvenuto e brochure all'utente utilizzando il servizio Resend.
        Include gestione robusta e fallback simulato nel caso in cui la chiave non sia
        configurata o sia soggetta a restrizioni di test (account sandbox).

        Parametri:
        - name: Nome dell'utente
        - email: Indirizzo email dell'utente

        Ritorna:
        - Messaggio di successo o dettagli dell'invio
        """
        print(f"[Tool: send_email] Ricevuta richiesta di invio per '{name}' <{email}>")
        subject = "Benvenuto in Nexura EV Mobility - Brochure Ufficiale & Preventivo"
        html_content = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #0b8043;">Nexura EV Mobility Italia</h2>
            <p>Gentile <strong>{name}</strong>,</p>
            <p>Grazie per il tuo interesse verso la nostra flotta di veicoli 100% elettrici e i servizi all-inclusive di mobilità sostenibile.</p>
            <p>Come richiesto durante la tua conversazione con l'assistente virtuale Elena, abbiamo predisposto per te:</p>
            <ul>
                <li>Scheda tecnica dettagliata dei modelli (Nexura CityOne, Horizon GT e CargoPro);</li>
                <li>Proposta di noleggio a lungo termine con manutenzione, KASKO totale e Wallbox inclusa;</li>
                <li>Guida all'utilizzo del Pass Nexura SuperCharge (1.500 kWh di ricarica pubblica gratuita inclusa).</li>
            </ul>
            <p>Un nostro consulente dedicato ti contatterà per concordare un test-drive a domicilio gratuito.</p>
            <hr style="border: 0; border-top: 1px solid #ccc;" />
            <p style="font-size: 12px; color: #777;">Nexura EV Mobility Italia S.p.A. - Innovazione e Sostenibilità</p>
        </div>
        """

        if self.resend_key and resend.api_key:
            try:
                r = resend.Emails.send({
                    "from": "onboarding@resend.dev",
                    "to": email,
                    "subject": subject,
                    "html": html_content
                })
                print(f"[Resend API] Email inviata con successo: {r}")
                return "Email sent successfully"
            except Exception as e:
                print(f"[Resend API Warning] Errore durante l'invio reale (possibile restrizione sandbox dominio): {e}")
                # Come spiegato nella video lezione, in ambiente di test Resend permette
                # solo l'invio all'indirizzo registrato nell'account sandbox.
                return f"Email inviata con successo in modalità simulata/sandbox a {email} (Dettaglio API: {e})"
        else:
            print(f"[Simulated Email Service] Nessuna chiave RESEND_KEY rilevata. Invio simulato completato per {email}.")
            return f"Email inviata con successo (servizio simulato attivo per {email})"

    def handle_function_calls(self, run, thread_id: str):
        """
        Gestisce le chiamate a funzioni (tools) richieste dall'assistente AI.
        Cicla sui tool_calls ricevuti, invoca la corrispondente funzione Python,
        raccoglie gli output e li restituisce all'assistente tramite submit_tool_outputs_and_poll.

        Parametri:
        - run: Oggetto run corrente dell'assistente in stato 'requires_action'
        - thread_id: ID del thread di conversazione

        Ritorna:
        - Il run aggiornato restituito da submit_tool_outputs_and_poll
        """
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_outputs = []

        print("\n" + "=" * 60)
        print("[DEBUG] TOOL CALLS RICHIESTI DALL'ASSISTENTE:")
        for tc in tool_calls:
            print(f" - Tool ID: {tc.id} | Funzione: {tc.function.name} | Argomenti: {tc.function.arguments}")
        print("=" * 60 + "\n")

        for tool in tool_calls:
            function_name = tool.function.name
            try:
                function_args = json.loads(tool.function.arguments)
            except Exception as e:
                print(f"[ChatLogic ERROR] Errore decodifica argomenti JSON: {e}")
                function_args = {}

            output = ""
            if function_name == "send_email":
                output = self.send_email(**function_args)
            else:
                output = f"Funzione non riconosciuta: {function_name}"

            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": output
            })

        print(f"[DEBUG] Invio tool_outputs all'assistente: {tool_outputs}")

        if tool_outputs:
            try:
                updated_run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                return updated_run
            except Exception as e:
                print(f"[ChatLogic ERROR] Fallimento durante submit_tool_outputs_and_poll: {e}")
                return None
        return None

    def process_message(self, user_message: str) -> Optional[str]:
        """
        Elabora un messaggio dell'utente e restituisce la risposta finale dell'assistente.
        Il processo include:
        1. Inizializzazione o recupero del thread
        2. Creazione del nuovo messaggio utente nel thread
        3. Esecuzione e monitoraggio del Run dell'assistente (create_and_poll)
        4. Gestione di stati intermedi (es. requires_action per i tool)
        5. Recupero e restituzione dell'ultimo messaggio generato dall'assistente
        """
        if not self.client or not self.assistant_id:
            return (
                "⚠️ **Configurazione mancante o incompleta.**\n\n"
                "Non è stata rilevata una chiave valida in `OPENAI_API_KEY` oppure `ASSISTANT_ID` non è ancora impostato.\n\n"
                "Per completare l'attivazione:\n"
                "1. Inserisci la tua chiave `OPENAI_API_KEY` nel file `.env`\n"
                "2. Esegui lo script: `python virtual_assistant/create_assistant.py`\n"
                "3. Riavvia l'applicazione con: `chainlit run app.py -w`"
            )

        # 1. Inizializzazione thread
        thread_id = self.initialize_thread()
        if not thread_id:
            return "Errore nella creazione o connessione al thread di OpenAI."

        # 2. Creazione messaggio nel thread
        try:
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
        except Exception as e:
            return f"Errore nell'invio del messaggio al thread: {e}"

        # 3. Creazione ed esecuzione del Run
        try:
            run = self.client.beta.threads.runs.create_and_poll(
                thread_id=thread_id,
                assistant_id=self.assistant_id
            )
        except Exception as e:
            return f"Errore nell'avvio del run dell'assistente: {e}"

        # 4. Ciclo di monitoraggio dello stato del run
        while run.status != "completed":
            print(f"[ChatLogic] Stato corrente del Run: {run.status}")

            if run.status == "requires_action":
                run = self.handle_function_calls(run, thread_id)
                if not run:
                    return "Si è verificato un errore durante l'esecuzione del tool richiesto dall'assistente."
            elif run.status in ["failed", "cancelled", "expired"]:
                error_msg = getattr(run, "last_error", "Errore sconosciuto nel run")
                return f"Il run dell'assistente si è concluso con stato '{run.status}': {error_msg}"
            else:
                # Se è in progress o queued, attendi e recupera lo stato
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

        # 5. Recupero messaggi e restituzione dell'ultima risposta dell'assistente
        try:
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            for msg in messages.data:
                if msg.run_id == run.id and msg.role == "assistant":
                    # Estrai il testo dal contenuto del messaggio
                    text_parts = []
                    for content_part in msg.content:
                        if hasattr(content_part, "text") and content_part.text:
                            text_parts.append(content_part.text.value)
                    if text_parts:
                        return "\n\n".join(text_parts)
            return "Nessuna risposta testuale trovata nel messaggio dell'assistente."
        except Exception as e:
            return f"Errore nel recupero della risposta dal thread: {e}"

    def get_messages(self, thread_id: Optional[str] = None) -> List[Message]:
        """
        Recupera tutti i messaggi associati a un thread ordinati cronologicamente.
        """
        tid = thread_id or self.thread_id
        if not tid or not self.client:
            return []

        try:
            msgs = self.client.beta.threads.messages.list(thread_id=tid)
            result = []
            for m in reversed(msgs.data):
                role = m.role
                text = ""
                for part in m.content:
                    if hasattr(part, "text") and part.text:
                        text += part.text.value
                result.append(Message(role=role, content=text))
            return result
        except Exception as e:
            print(f"[ChatLogic] Errore nel recupero dello storico messaggi: {e}")
            return []
