import os
import json
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI
import chainlit as cl

# Import dei tool definiti in tools.py
# Gestisce sia l'esecuzione diretta come modulo chainlit sia l'import da root
try:
    from tools.tools import CourseInfoTool, ScheduleTool, BookingTool
except ImportError:
    from tools import CourseInfoTool, ScheduleTool, BookingTool

# Caricamento variabili d'ambiente
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
MODEL = "gpt-4o"

course_tool = CourseInfoTool()
schedule_tool = ScheduleTool()
booking_tool = BookingTool()

# Definizione dei Tool in formato JSON Schema per OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_course_info",
            "description": "Ottiene informazioni dettagliate su un corso specifico (prezzo, durata, programma).",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {
                        "type": "string",
                        "description": "Nome del corso (es. 'Python & AI Foundations', 'Agenti AI & Sistemi RAG Avanzati', 'Deep Learning').",
                    }
                },
                "required": ["course_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_classes",
            "description": "Ottiene le date delle prossime classi in partenza e i posti disponibili.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {
                        "type": "string",
                        "description": "Filtro opzionale per nome del corso.",
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Data minima di inizio in formato YYYY-MM-DD.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_consultation",
            "description": "Prenota una sessione di orientamento o consulenza tecnica 1-to-1 con un docente.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Data desiderata in formato YYYY-MM-DD (es. 2025-06-08).",
                    },
                    "time": {
                        "type": "string",
                        "description": "Orario desiderato in formato HH:MM (es. 15:30).",
                    },
                    "teacher_id": {
                        "type": "string",
                        "description": "ID del docente opzionale (es. T001, T002, T003).",
                    },
                },
                "required": ["date", "time"],
            },
        },
    },
]


def handle_tool_call(tool_call) -> str:
    """
    Esegue localmente la funzione Python invocata dal modello e ne restituisce il risultato come stringa.
    """
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    print("*" * 80)
    print(f"Esecuzione tool: {function_name}")
    print(f"Argomenti ricevuti: {function_args}")
    print("*" * 80)

    result = "Nessuna azione eseguita."
    if function_name == "get_course_info":
        result = course_tool.get_info(**function_args)
    elif function_name == "get_upcoming_classes":
        result = schedule_tool.get_classes(**function_args)
    elif function_name == "book_consultation":
        result = booking_tool.book_consultation(**function_args)

    print(f"Risultato tool: {result}")
    print("*" * 80)
    return str(result)


def is_valid_key(key: Optional[str]) -> bool:
    if not key:
        return False
    k = key.strip().lower()
    return not ("inserisci" in k or "your_openai" in k or len(k) < 10)


# =====================================================================
# CHAINLIT EVENT HANDLERS
# =====================================================================

@cl.on_chat_start
def on_chat_start():
    today = datetime.today().strftime("%Y-%m-%d")
    system_prompt = (
        f"Sei un assistente virtuale per la 'AI & Tech Innovation Academy'. "
        f"La data odierna è {today}. "
        "Aiuti gli studenti e i professionisti a scoprire i corsi dell'accademia, verificare le prossime "
        "classi disponibili e prenotare videochiamate 1-to-1 con i docenti e mentor tecnici. "
        "Usa i tool a tua disposizione quando l'utente richiede informazioni specifiche o prenotazioni. "
        "Sii sempre cortese, chiaro, conciso e professionale."
    )
    cl.user_session.set("messages", [{"role": "system", "content": system_prompt}])


@cl.on_message
async def main(message: cl.Message):
    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": message.content})

    # Verifica presenza chiave OpenAI
    if not is_valid_key(OPENAI_KEY):
        mock_reply = (
            "**[AVVISO - Modalità Demo]**\n"
            "Non è stata configurata una chiave `OPENAI_API_KEY` valida nel file `.env`.\n\n"
            "Tuttavia, l'architettura dei Tool è attiva e testabile!\n"
            "- Corso info: " + course_tool.get_info("rag_agents") + "\n\n"
            "- Prossime classi:\n" + schedule_tool.get_classes() + "\n"
            "Per abilitare la chat conversazionale con GPT-4o, inserisci la tua API key in `.env`."
        )
        await cl.Message(author="assistant", content=mock_reply).send()
        return

    client = OpenAI(api_key=OPENAI_KEY)

    try:
        # Prima chiamata con tool abilitati
        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls

        # Se il modello ha deciso di chiamare uno o più tool
        if tool_calls:
            # Aggiungiamo la risposta del modello (con i tool_calls) alla cronologia
            messages.append(response_message)

            # Eseguiamo ogni tool richiesto
            for tool_call in tool_calls:
                function_response = handle_tool_call(tool_call)
                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": function_response,
                    }
                )

            # Seconda chiamata per ottenere la risposta finale arricchita dai risultati dei tool
            second_response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            final_message = second_response.choices[0].message
            messages.append(final_message)
            cl.user_session.set("messages", messages)

            await cl.Message(
                author="assistant",
                content=final_message.content or "Operazione completata.",
            ).send()

        else:
            # Risposta diretta senza invocazione di tool
            messages.append(response_message)
            cl.user_session.set("messages", messages)

            await cl.Message(
                author="assistant",
                content=response_message.content or "",
            ).send()

    except Exception as e:
        error_msg = f"Si è verificato un errore durante l'interazione con OpenAI: {e}"
        await cl.Message(author="assistant", content=error_msg).send()
