import os
from datetime import datetime
from typing import Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

# Tools
from travel_agent_api.tools.flights_finder import flights_finder, FlightsInput
from travel_agent_api.tools.hotels_finder import hotels_finder, HotelsInput
from travel_agent_api.tools.chain_historical_expert import chain_historical_expert
from travel_agent_api.tools.chain_travel_plan import chain_travel_plan, TravelPlanInput
from travel_agent_api.utils.tracing import print_trace

load_dotenv()

FLIGHTS_OUTPUT = """
format: markdown
## Miglior Opzione
### Andata:
- Compagnia aerea: Ryanair
- Data di partenza: 2024-12-13
- Ora di partenza: 10:00
- Durata del volo: 1h 30m
### Ritorno:
- Compagnia aerea: Ryanair
- Data di ritorno: 2024-12-19
- Ora di ritorno: 14:30
- Durata del volo: 1h 30m
Inserisci il link di Google per la prenotazione se possibile.

#### Altri opzioni disponibili:
- Compagnia aerea: Ryanair
- Data di partenza: 2024-12-13
- Ora di partenza: 10:00
- Durata del volo: 1h 30m
- Compagnia aerea: Ryanair
- Data di ritorno: 2024-12-19
- Ora di ritorno: 14:30
- Durata del volo: 1h 30m
...
"""

HOTELS_OUTPUT = """
format: markdown
#### Hotel 1
Inserisci la foto dell'hotel se disponibile.
*Descrizione:* Camere e suite eleganti, a volte con vista sulla città, in hotel esclusivo con piscina panoramica e spa.
*Prezzo per notte:* €296 (prima delle tasse e spese: €260)
*Prezzo totale:* €2,660 (prima delle tasse e spese: €2,336)
*Check-in:* 15:00, Check-out: 12:00
*Valutazione complessiva:* 4.5 su 5
*Servizi Inclusi:* Spa, Piscina, Parcheggio gratuito

#### Hotel 2
Inserisci la foto dell'hotel se disponibile.
Descrizione: Hotel in stile Liberty con alloggi arredati in maniera artistica, ristorante elegante, bar e spa.
*Prezzo per notte:* €380 (prima delle tasse e spese: €333)
*Prezzo totale:* €3,418 (prima delle tasse e spese: €3,000)
*Check-in:* 15:00, Check-out: 12:00
*Valutazione complessiva:* 4.5 su 5
*Servizi Inclusi:* Spa, Piscina, Parcheggio gratuito
"""

TRAVEL_PLAN_OUTPUT = """
format: markdown
### Itinerario:
### Giorno 1 - 2024-12-13:
*Mattina:* Descrizione dell'attivita' da svolgere la mattina
*Pomeriggio:* Descrizione dell'attivita' da svolgere il pomeriggio
*Sera:* Descrizione dell'attivita' da svolgere la sera

### Giorno 2 - 2024-12-14:
*Mattina:* Descrizione dell'attivita' da svolgere la mattina
*Pomeriggio:* Descrizione dell'attivita' da svolgere il pomeriggio
*Sera:* Descrizione dell'attivita' da svolgere la sera
...
"""


class Agent:
    def __init__(self):
        self.current_datetime = datetime.now()
        self.api_mode = os.getenv("API_MODE", "prod").lower()
        self.openai_key = os.getenv("OPENAI_API_KEY", "")

        self.tools = [
            chain_historical_expert,
            flights_finder,
            hotels_finder,
            chain_travel_plan,
        ]

        # Inizializza l'agente se la chiave OpenAI è presente
        if self._is_prod_ready():
            self.model = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
            self.agent_executor = create_react_agent(self.model, self.tools)
        else:
            self.model = None
            self.agent_executor = None

    def _is_prod_ready(self) -> bool:
        """Verifica se l'ambiente ha una configurazione valida per OpenAI in produzione."""
        return (
            self.api_mode != "test"
            and bool(self.openai_key)
            and "YOUR_OPENAI_API_KEY" not in self.openai_key
            and "inserisci" not in self.openai_key
        )

    def _normalize_messages(self, messages: list[Any]) -> list[dict[str, str]]:
        """
        Normalizza i messaggi in ingresso supportando sia il formato del client Laravel
        ({'type': 'human', 'content': '...'}) che quello standard Swagger / OpenAI
        ({'role': 'user', 'content': '...'}).
        """
        normalized = []
        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content", "")
                role = msg.get("role")
                msg_type = msg.get("type")

                if msg_type == "human" or role in ("user", "human"):
                    normalized.append({"role": "user", "content": content})
                elif msg_type == "ai" or role in ("assistant", "ai"):
                    normalized.append({"role": "assistant", "content": content})
                elif msg_type == "system" or role == "system":
                    normalized.append({"role": "system", "content": content})
                else:
                    normalized.append({"role": "user", "content": content})
            elif isinstance(msg, BaseMessage):
                if isinstance(msg, HumanMessage):
                    normalized.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    normalized.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    normalized.append({"role": "system", "content": msg.content})
        return normalized

    def _generate_mock_agent_response(self, user_text: str) -> str:
        """
        Genera una risposta simulata strutturata coerente con i prompt delle lezioni,
        utile per testare l'integrazione frontend e il tracing senza consumare token OpenAI.
        """
        text_lower = user_text.lower()

        if any(w in text_lower for w in ["volo", "voli", "aereo", "flight", "fco", "cdg", "mxp", "bcn"]):
            return (
                "✈️ Certamente! Ecco le migliori soluzioni di volo individuate per il tuo viaggio:\n\n"
                + FLIGHTS_OUTPUT
            )
        elif any(w in text_lower for w in ["hotel", "albergo", "stelle", "dormire", "alloggio", "camera"]):
            return (
                "🏨 Ecco le migliori strutture alberghiere selezionate per te:\n\n"
                + HOTELS_OUTPUT
            )
        elif any(w in text_lower for w in ["itinerario", "programma", "piano", "organizzare", "viaggio"]):
            return (
                "🗺️ Ho preparato un itinerario dettagliato per il tuo viaggio:\n\n"
                + TRAVEL_PLAN_OUTPUT
            )
        elif any(w in text_lower for w in ["storia", "cultura", "rinascimento", "roma", "firenze", "monumenti"]):
            hist = chain_historical_expert.invoke({"input_text": user_text})
            return f"🏛️ Informazioni storiche e culturali per te:\n\n{hist}"
        else:
            return (
                f"👋 Ciao! Sono il tuo **Travel Assistant** AI intelligente. 🌍✈️\n\n"
                f"Posso aiutarti a:\n"
                f"- 🛫 **Cercare voli** convenienti e orari comodi\n"
                f"- 🏨 **Trovare hotel** perfetti per le tue esigenze e budget\n"
                f"- 📅 **Pianificare itinerari** giorno per giorno personalizzati\n"
                f"- 🏛️ **Fornirti curiosità storiche e culturali** sulle tue destinazioni preferite\n\n"
                f"Come posso aiutarti a pianificare la tua prossima avventura?"
            )

    def run(self, messages: list) -> list[dict[str, Any]]:
        """
        Elabora la conversazione e genera la risposta dell'agente.
        Supporta sia esecuzione con LLM reale (GPT-4o) sia modalità di test/mock per sviluppo locale.
        """
        print_trace("Agent.run_started", {"input_messages_count": len(messages)})

        SYSTEM_PROMPT = f"""
Sei un travel planner. Il tuo compito e' organizzare il viaggio per l'utente.
Aggiungi delle emojis per rendere il tuo output piu' interessante.
La data di oggi e' {self.current_datetime.strftime('%Y-%m-%d %H:%M:%S')}

Usa le seguenti istruzioni per creare un output:

Esempio Ouput Voli:
{FLIGHTS_OUTPUT}

Esempio Output Hotel:
{HOTELS_OUTPUT}

Esempio di Output Viaggio:
{TRAVEL_PLAN_OUTPUT}
"""
        normalized_history = self._normalize_messages(messages)

        # Se siamo in ambiente di produzione con chiavi configurate
        if self._is_prod_ready() and self.agent_executor is not None:
            conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}] + normalized_history
            print("[Agent] Invocazione ReAct agent con LLM OpenAI...")
            response = self.agent_executor.invoke({"messages": conversation_history})
            raw_messages = response["messages"][1:]

            # Converti in dizionari compatibili con FastAPI e Laravel
            formatted_messages = []
            for m in raw_messages:
                if hasattr(m, "model_dump"):
                    formatted_messages.append(m.model_dump())
                elif isinstance(m, dict):
                    formatted_messages.append(m)
                else:
                    formatted_messages.append({"type": getattr(m, "type", "ai"), "content": str(m)})
            return formatted_messages

        # Modalità test/mock
        print("[Agent] Modalità TEST attiva: risposta simulata con tracing.")
        last_user_msg = ""
        for m in reversed(normalized_history):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        ai_reply = self._generate_mock_agent_response(last_user_msg)

        # Restituiamo la cronologia con il nuovo messaggio AI nel formato atteso dal frontend
        response_messages = []
        for m in messages:
            if isinstance(m, dict):
                response_messages.append(m)
            elif hasattr(m, "model_dump"):
                response_messages.append(m.model_dump())

        response_messages.append({
            "type": "ai",
            "content": ai_reply,
            "additional_kwargs": {},
            "response_metadata": {}
        })

        return response_messages
