import os
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
try:
    from langchain_core.prompts import ChatPromptTemplate
except ImportError:
    from langchain.prompts import ChatPromptTemplate
from travel_agent_api.utils.tracing import print_trace


@tool
def chain_historical_expert(input_text: str) -> str:
    """
    Questo tool utilizza un modello di intelligenza artificiale per fornire contenuti
    approfonditi su un argomento storico specifico.

    Args:
        input_text (str): Il testo dell'argomento per il quale si vuole ottenere il contenuto.

    Returns:
        str: Il contenuto generato dal modello.
    """
    api_mode = os.getenv("API_MODE", "prod").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")

    # Tracing da specifica
    print("*" * 80)
    print("chain_historical_expert")
    print(f"Query: {input_text}")
    print("*" * 80)

    print_trace("chain_historical_expert_invoked", {
        "query": input_text,
        "mode": api_mode
    })

    if api_mode == "test" or not openai_key or "YOUR_OPENAI_API_KEY" in openai_key or "inserisci" in openai_key:
        print("[chain_historical_expert] Modalità TEST o chiave mancante: risposta mock.")
        return (
            f"🏛️ **Guida Storica e Culturale**: {input_text}\n\n"
            "Questa destinazione vanta una storia millenaria ricca di arte, tradizioni e architettura straordinaria. "
            "Passeggiando per le sue piazze e monumenti è possibile ammirare secoli di stratificazione storica, "
            "dalle radici classiche e medievali fino al Rinascimento e all'era moderna. 🎨✨\n\n"
            "💡 *Consiglio culturale*: Visita i musei al mattino presto per apprezzare le collezioni con calma e "
            "non dimenticare di esplorare i quartieri storici a piedi!"
        )

    try:
        model = ChatOpenAI(model_name="gpt-4o", temperature=0.7)
        system_prompt = """
You are an historical expert.
Your mission is to provide in-depth content on the topic,
answer questions, and act as an assistant.
Use emojis to make your answers more engaging and friendly.
Always strive to be approachable and helpful, offering the
most accurate and useful information possible to users.
"""
        prompt = ChatPromptTemplate([
            ("system", "{system_prompt}"),
            ("user", "{input}")
        ])

        chain = prompt | model
        result = chain.invoke({
            "input": input_text,
            "system_prompt": system_prompt
        })
        return result.content if hasattr(result, "content") else str(result)
    except Exception as e:
        print(f"[chain_historical_expert] Errore esecuzione chain: {e}. Risposta fallback.")
        return f"🏛️ Informazioni storiche su {input_text}: destinazione di grande fascino artistico e culturale! ✨"
