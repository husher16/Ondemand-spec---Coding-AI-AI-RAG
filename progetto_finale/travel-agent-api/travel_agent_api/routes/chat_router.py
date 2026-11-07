import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from travel_agent_api.services.agent_service import Agent
from travel_agent_api.utils.tracing import print_trace

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    """Modello per la richiesta di chat inviata dal frontend Laravel o da Swagger UI."""
    messages: list = Field(..., description="Elenco dei messaggi della conversazione")

    model_config = {
        "json_schema_extra": {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "Vorrei organizzare un viaggio a Roma per 2 persone dal 15 al 20 maggio"
                    }
                ]
            }
        }
    }


# Alias per mantenere piena compatibilità con la nomenclatura della documentazione originale
ChatComplentionRequest = ChatCompletionRequest


@router.post("/travel-agent", summary="Elaborazione richiesta Travel Agent")
def chat_completion(request: ChatCompletionRequest):
    """
    Endpoint per la gestione delle richieste di chat.
    Processa i messaggi ricevuti e restituisce una risposta dall'agente di viaggio.

    Args:
        request (ChatCompletionRequest): La richiesta contenente i messaggi della conversazione

    Returns:
        list: La lista dei messaggi aggiornata elaborata dall'agente di viaggio

    Raises:
        HTTPException: In caso di errori durante l'elaborazione della richiesta
    """
    start_time = time.time()

    # Tracing da specifica aula
    print("*" * 80)
    print("chat_completion")
    print(f"Messaggi ricevuti: {len(request.messages)}")
    print("*" * 80)

    print_trace("chat_completion_received", {
        "messages_count": len(request.messages),
        "last_message": request.messages[-1] if request.messages else "Nessuno"
    })

    try:
        agent = Agent()
        response = agent.run(messages=request.messages)

        elapsed = round(time.time() - start_time, 2)
        print_trace("chat_completion_completed", {
            "elapsed_seconds": elapsed,
            "response_messages_count": len(response)
        })

        return response
    except Exception as e:
        print(f"Errore durante l'elaborazione chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Errore interno durante l'elaborazione della richiesta: {str(e)}"
        )
