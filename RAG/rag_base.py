"""
RAG Base - Riproduzione del codice visto nella lezione.
Utilizza ChromaDB come database vettoriale e OpenAI per embedding e generazione della risposta.
"""

import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI

# 1. Carica le variabili d'ambiente (per OPENAI_API_KEY)
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key or openai_key.startswith("inserisci"):
    print("[ATTENZIONE] OPENAI_API_KEY non impostata nel file .env. Verrà eseguita solo la parte di lettura documenti.")

# 2. Lettura dei documenti (curriculum da resumes/)
documents_dir = "resumes"
documents = []
metadatas = []
ids = []
doc_id = 0

print(f"Lettura documenti dalla cartella '{documents_dir}'...")
for filename in os.listdir(documents_dir):
    if filename.endswith(".txt"):
        file_path = os.path.join(documents_dir, filename)
        with open(file_path, "r", encoding="utf-8") as file:
            # Suddivisione del documento in frammenti (chunks) separati da '###'
            chunks = file.read().replace("\n", " ").split("###")
            for chunk in chunks:
                if not chunk.isspace() and chunk != "":
                    documents.append(chunk.strip())
                    metadatas.append({"source": filename})
                    ids.append(str(doc_id))
                    doc_id += 1

print(f"Totale frammenti (chunks) caricati: {len(documents)}")
if documents:
    print(f"Esempio metadato [0]: {metadatas[0]}")
    print(f"Esempio frammento [0]: {documents[0][:100]}...\n")

if openai_key and not openai_key.startswith("inserisci"):
    # 3. Funzione di Embedding con OpenAI
    openai_ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=openai_key,
        model_name="text-embedding-3-small"
    )

    # 4. Inizializzazione ChromaDB e creazione Collection
    chroma_client = chromadb.Client()
    collection = chroma_client.get_or_create_collection(
        name="CVs",
        embedding_function=openai_ef
    )

    # 5. Indicizzazione dei documenti nel Vector Store
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Documenti salvati nella collection 'CVs' di ChromaDB.")

    # 6. Vector Similarity Search
    user_question = "mi serve qualcuno per promuovere il mio prodotto"
    print(f"\nDomanda utente: '{user_question}'")
    
    results = collection.query(
        query_texts=[user_question],
        n_results=2
    )
    
    print("\nRisultati della ricerca semantica:")
    for i in range(len(results["ids"][0])):
        print(f" - ID: {results['ids'][0][i]}")
        print(f"   Fonte: {results['metadatas'][0][i]['source']}")
        print(f"   Testo: {results['documents'][0][i][:120]}...\n")

    # 7. Preparazione del prompt con il contesto recuperato (RAG)
    context = f"CONTESTO: Nome file {results['metadatas'][0][0]['source']} ecco il paragrafo piu' significativo: {results['documents'][0][0]}"
    
    prompt = f"""Dato il seguente contesto {context} rispondi alla domanda dell'utente {user_question}
spiegando che nel file individuato c'e' il profilo piu' adatto.
Argomenta la scelta utilizzando il contenuto del testo individuato nel contesto"""

    # 8. Generazione della risposta con il modello LLM
    print("Invocazione del modello LLM (gpt-4o)...")
    client = OpenAI(api_key=openai_key)
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "developer",
                "content": "Sei un assistente HR, specializzato nella ricerca di profili professionali"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("\n=== RISPOSTA GENERATA (RAG) ===")
    print(completion.choices[0].message.content)
