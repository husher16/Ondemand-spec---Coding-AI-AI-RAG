import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
# utils.py
from config import Config
from openai import OpenAI

client = OpenAI(base_url=Config.AI_API_URL, api_key=Config.AI_API_KEY)


class LLMHelper:

    @staticmethod
    def chat(messages):
        return client.chat.completions.create(
            model=Config.LLM_MODEL, messages=messages, stream=True
        )

    @staticmethod
    async def get_candidate_name(context):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL_LOW,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                      Dato il seguente contesto individua il nome e cognome del candidato e ritorna solo il nome e cognome del candidato. Quello che sto per fornirti e' il curriculum vite del candidato: {context}
                      """,
                }
            ],
        )
        return response.choices[0].message.content

    @staticmethod
    async def get_db_stats(context):
        response = client.chat.completions.create(
            model=Config.LLM_MODEL_LOW,
            messages=[
                {
                    "role": "user",
                    "content": f"""
                      Il tuo compito è quello di descrivere in modo testuale, ma sintetico, le statistiche legate al database dei frammenti indicizzati da questo sistema. Ecco le informazioni necessarie per le statistiche da fornire: {context}
                      """,
                }
            ],
        )
        return response.choices[0].message.content
    
    @staticmethod
    def classify_intent(user_question):
        """
        Chiede all'LLM di classificare l'intenzione dell'utente.
        Ritorna solo "search_cv" o "info_cv".
        """

        intent_prompt = f"""
        Sei un assistente AI che aiuta a elaborare domande sugli annunci di lavoro.
        Classifica la seguente richiesta dell'utente in una delle due categorie:
        - "search_cv": Se l'utente sta cercando un candidato con determinate competenze.
        - "info_cv": Se l'utente sta chiedendo informazioni su un candidato già trovato.

        Domanda dell'utente: "{user_question}"
        
        Rispondi solo con "search_cv" o "info_cv", senza aggiungere altro testo.
        """
        response = client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[{"role": "user", "content": intent_prompt}]
        )
        return response.choices[0].message.content.strip().lower()
    
    @staticmethod
    def create_prompt(context, question, context_lines):
        return f"""
        Sei un assistente esperto nella selezione del personale. Devi analizzare il seguente contesto e rispondere alla domanda dell'utente nel modo più chiaro ed efficace possibile.

        📌 **CONTENUTO DEL DOCUMENTO ANALIZZATO:** 
        [[[
        {context}
        ]]]

        📌 **DOMANDA DELL'UTENTE:**  
        [[[ {question} ]]]

        🔹 **Se l'utente sta cercando un CV:**  
        - Conferma che nel file individuato è presente un candidato adatto.  
        - Spiega perché è adatto, citando le competenze e le esperienze rilevanti.  
        - Assicurati di indicare **il nome del file** in cui si trova il profilo.  

        🔹 **Se l'utente sta chiedendo informazioni su un CV già individuato:**  
        - Rispondi in modo conciso e diretto, fornendo **solo l'informazione richiesta**.  
        - Evita dettagli superflui o ripetizioni.  

        🔹 **In entrambi i casi:**  
        - Usa il seguente contesto aggiuntivo per individuare il **nome del candidato** o altre informazioni utili:  
        [[[ {context_lines} ]]]  
        - Assicurati che il testo sia scritto in **italiano corretto** e senza errori.  

        """

    # @staticmethod
    # def create_prompt(context, question, context_lines):
    #     return f"""
    #         Dato il seguente contesto: 
    #         [[[
    #         {context}
    #         ]]].
    #         Rispondi alla domanda dell'utente: [[[ {question}]]] .
    #         Se: si sta cercando un cv
    #         - spiega che nel file individuato c'e' il profilo piu' adatto. 
    #         - Argomenta la scelta utilizzando il contenuto del testo individuato nel contesto.
    #         - Assicurati di nominare il Nome dei file.
    #         Se: si stanno chiedendo info su un cv già esistente
    #         - resituisci solo l'informazione chiesta senza aggiungere info inutili. 
    #         In ogni caso:
    #         - Assicurati di indicare il nome del candidato o altre info richieste avendo: [[[ {context_lines} ]]].
    #         - Assicurati di usare correttamente la lingua italiana senza commettere errori. 
    #         Chiudi sempre con una barzelletta!!!
    #     """
