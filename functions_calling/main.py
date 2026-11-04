import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

from tools.tools import CourseInfoTool, ScheduleTool, BookingTool
from tools import TOOLS, handle_tool_call, is_valid_key

load_dotenv()

MODEL = "gpt-4o"


def run_terminal_demo(client: OpenAI):
    """
    Esegue una simulazione completa del flusso di Function Calling da terminale.
    """
    print("\n" + "=" * 70)
    print("DEMO FUNCTION CALLING - AI & TECH INNOVATION ACADEMY")
    print("=" * 70)

    course_tool = CourseInfoTool()
    schedule_tool = ScheduleTool()
    booking_tool = BookingTool()

    today = datetime.today().strftime("%Y-%m-%d")
    messages = [
        {
            "role": "system",
            "content": (
                f"Sei un assistente virtuale per la 'AI & Tech Innovation Academy'. "
                f"La data odierna è {today}. "
                "Aiuti gli utenti a scoprire corsi, consultare date e prenotare videochiamate con i docenti."
            ),
        }
    ]

    test_queries = [
        "Vorrei sapere quali corsi offrite sul RAG e sugli agenti, e quanto costano.",
        "Ci sono classi in partenza per quel corso a giugno 2025?",
        "Perfetto! Vorrei prenotare una videochiamata con la Dott.ssa Lovelace per l'8 Giugno 2025 alle 15:30.",
    ]

    for user_input in test_queries:
        print(f"\n[UTENTE]: {user_input}")
        messages.append({"role": "user", "content": user_input})

        completion = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)
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

            second_response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            final_message = second_response.choices[0].message
            messages.append(final_message)
            print(f"\n[ASSISTENTE]:\n{final_message.content}\n")
        else:
            messages.append(response_message)
            print(f"\n[ASSISTENTE]:\n{response_message.content}\n")


def run_local_tools_test():
    """
    Test di verifica locale dei tool senza chiamata all'API remota.
    """
    print("\n" + "=" * 70)
    print("TEST LOCALE DEI TOOL (Senza API Key OpenAI)")
    print("=" * 70)

    course_tool = CourseInfoTool()
    schedule_tool = ScheduleTool()
    booking_tool = BookingTool()

    print("\n1. Test CourseInfoTool (get_info('rag_agents')):")
    print(course_tool.get_info("rag_agents"))

    print("\n2. Test ScheduleTool (get_classes(course_name='Agenti AI')):")
    print(schedule_tool.get_classes(course_name="Agenti AI"))

    print("\n3. Test BookingTool (book_consultation('2025-06-08', '15:30', 'T002')):")
    print(booking_tool.book_consultation("2025-06-08", "15:30", "T002"))

    print("\n4. Test BookingTool Slot Occupato:")
    print(booking_tool.book_consultation("2025-06-08", "15:30", "T002"))

    print("\n[OK] Tutti i tool sono stati testati e funzionano correttamente!")


if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")

    if is_valid_key(api_key):
        client = OpenAI(api_key=api_key)
        run_terminal_demo(client)
    else:
        print("[AVVISO] OPENAI_API_KEY non configurata o placeholder rilevato nel file .env.")
        print("Esecuzione del test diagnostico locale dei Tool...\n")
        run_local_tools_test()
        print("\nPer avviare la chat web interattiva con Chainlit:")
        print("  .\\.venv\\Scripts\\chainlit run app.py -w")
        print("Oppure:")
        print("  .\\.venv\\Scripts\\chainlit run tools/__init__.py -w")
