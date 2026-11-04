import os
import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI, AuthenticationError

# Carica eventuali variabili d'ambiente da un file .env
load_dotenv()

MODEL = "gpt-4o-2024-08-06"  # Oppure "gpt-4o-mini"


# =====================================================================
# ESEMPIO 1: Math Reasoning (Risoluzione di problemi matematici a step)
# =====================================================================

class MathReasoning(BaseModel):
    class Step(BaseModel):
        explanation: str
        output: str

    steps: list[Step]
    final_answer: str

    def print_solution(self):
        print("\n--- RISOLUZIONE PASSO DOPO PASSO ---")
        for i, step in enumerate(self.steps, 1):
            print(f"Passo {i}: {step.explanation}")
            print(f"Risultato: {step.output}\n")
        print(f"Questa e' la soluzione finale: {self.final_answer}")


MATH_TUTOR_PROMPT = (
    "Sei un utile tutor di matematica. Guida l'utente attraverso la soluzione passo dopo passo."
)


def run_math_reasoning_example(client: OpenAI, model: str = MODEL):
    print("=" * 60)
    print("ESEMPIO 1: Math Reasoning con Structured Output")
    print("=" * 60)

    question = "Come posso risolvere 8 x + 7 = -23?"
    print(f"Domanda: {question}\n")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": MATH_TUTOR_PROMPT},
            {"role": "user", "content": question},
        ],
        response_format=MathReasoning,
    )

    message = completion.choices[0].message
    if message.refusal:
        print(f"Richiesta rifiutata dal modello: {message.refusal}")
    else:
        math_solution: MathReasoning = message.parsed
        math_solution.print_solution()


# =====================================================================
# ESEMPIO 2: Article Summary (Estrazione strutturata da un articolo)
# =====================================================================

class Concept(BaseModel):
    title: str
    description: str


class ArticleSummary(BaseModel):
    invented_year: int
    summary: str
    inventors: list[str]
    description: str
    concepts: list[Concept]

    def print_summary(self):
        print("\n--- RIEPILOGO STRUTTURATO ARTICOLO ---")
        print(f"Anno di invenzione : {self.invented_year}")
        print(f"Inventori          : {', '.join(self.inventors)}")
        print(f"Sommario           : {self.summary}")
        print(f"Descrizione        : {self.description}")
        print("\nConcetti chiave:")
        for i, concept in enumerate(self.concepts, 1):
            print(f"  {i}. {concept.title}: {concept.description}")


SUMMARIZATION_PROMPT = """
Ti verrà fornito il contenuto di un articolo su un'invenzione.
Il tuo obiettivo sarà quello di riassumere l'articolo seguendo lo schema fornito.
Ecco una descrizione dei parametri:
- invented_year: anno in cui è stata inventata l'invenzione di cui si parla nell'articolo
- summary: riassunto in una frase che descrive l'invenzione
- inventors: array di stringhe che elencano i nomi completi degli inventori, se presenti, altrimenti solo il cognome
- concepts: array di concetti chiave relativi all'invenzione, ogni concetto contiene un titolo e una descrizione
- description: breve descrizione dell'invenzione
"""

SAMPLE_ARTICLE = """
Le Reti Neurali Convoluzionali (CNN) hanno rivoluzionato la visione artificiale moderna.
Nel 1989, Yann LeCun e i suoi collaboratori presso i Bell Labs hanno introdotto per la prima volta
l'architettura LeNet, combinando filtri convoluzionali e retropropagazione per il riconoscimento
di cifre scritte a mano. 
Le CNN utilizzano operazioni di convoluzione tramite filtri o kernel per estrarre mappe di caratteristiche
spaziali invarianti per traslazione, riducendo drasticamente il numero di parametri rispetto alle reti
densamente connesse. Seguono tipicamente strati di pooling (come il Max Pooling) per ridurre la dimensionalità
e aumentare il campo ricettivo, e infine strati fully-connected per la classificazione finale.
"""


def run_article_summary_example(client: OpenAI, model: str = MODEL):
    print("\n" + "=" * 60)
    print("ESEMPIO 2: Article Summarization con Structured Output")
    print("=" * 60)

    print("Testo dell'articolo analizzato:")
    print(SAMPLE_ARTICLE.strip())

    completion = client.beta.chat.completions.parse(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": SUMMARIZATION_PROMPT.strip()},
            {"role": "user", "content": SAMPLE_ARTICLE},
        ],
        response_format=ArticleSummary,
    )

    message = completion.choices[0].message
    if message.refusal:
        print(f"Richiesta rifiutata dal modello: {message.refusal}")
    else:
        article_summary: ArticleSummary = message.parsed
        article_summary.print_summary()


# =====================================================================
# DEMO LOCALE (Validazione Pydantic senza API call)
# =====================================================================

def run_local_validation_demo():
    print("Verifica della sintassi e della validazione Pydantic dei modelli in corso...\n")

    demo_math = MathReasoning(
        steps=[
            MathReasoning.Step(
                explanation="Sottrai 7 da entrambi i lati dell'equazione",
                output="8x = -30",
            ),
            MathReasoning.Step(
                explanation="Dividi entrambi i lati per 8",
                output="x = -30 / 8 = -3.75",
            ),
        ],
        final_answer="x = -3.75",
    )
    print("Test validazione Esempio 1 (MathReasoning):")
    demo_math.print_solution()

    demo_article = ArticleSummary(
        invented_year=1989,
        summary="Architettura di deep learning basata su filtri convoluzionali per l'elaborazione di immagini.",
        inventors=["Yann LeCun"],
        description="Le CNN estraggono feature spaziali gerarchiche attraverso strati di convoluzione e pooling.",
        concepts=[
            Concept(title="Convoluzione", description="Applicazione di kernel per estrarre mappe di feature."),
            Concept(title="Pooling", description="Riduzione della dimensionalità spaziale delle feature maps."),
        ],
    )
    print("\nTest validazione Esempio 2 (ArticleSummary):")
    demo_article.print_summary()
    print("\n[OK] Struttura Pydantic e modelli validati con successo.")


# =====================================================================
# MAIN ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    is_placeholder = (
        not api_key
        or "inserisci" in api_key.lower()
        or "your_openai_api_key" in api_key.lower()
    )

    if is_placeholder:
        print("[AVVISO] Chiave OPENAI_API_KEY non configurata o placeholder rilevato.")
        print("Per eseguire le chiamate reali all'API OpenAI:")
        print("1. Inserisci la tua API key reale nel file .env (OPENAI_API_KEY=sk-...)")
        print("2. Esegui nuovamente: python structured_outputs.py\n")
        run_local_validation_demo()
    else:
        try:
            client = OpenAI(api_key=api_key)
            run_math_reasoning_example(client)
            run_article_summary_example(client)
        except AuthenticationError as e:
            print(f"\n[ERRORE DI AUTENTICAZIONE OPENAI]: {e}")
            print("Verifica che la chiave OPENAI_API_KEY inserita nel file .env sia corretta e valida.\n")
            run_local_validation_demo()
