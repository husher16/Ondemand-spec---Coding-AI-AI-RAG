import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from travel_agent_api.routes import chat_router
from travel_agent_api.utils.tracing import print_trace

load_dotenv()

app = FastAPI(
    title="Travel Agent API",
    description="Assistente di Viaggio Intelligente basato su FastAPI, LangChain e LangGraph",
    version="1.0.0"
)

# Configurazione CORS per consentire al client Laravel (Livewire) di comunicare con il backend
origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",  # Vite dev server
    "http://localhost:5173",
    "*"                       # Permetti test agevoli in locale
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusione del router per la chat dell'agente
app.include_router(
    chat_router.router,
    tags=["Chat"],
    prefix="/chat"
)


@app.get("/", tags=["Info"])
def root():
    """Endpoint informativo di benvenuto con lo stato del servizio."""
    return {
        "status": "online",
        "service": "Travel Agent API",
        "version": "1.0.0",
        "documentation": "/docs",
        "chat_endpoint": "/chat/travel-agent"
    }


@app.get("/health", tags=["Monitoring"])
def health():
    """Endpoint di healthcheck e diagnostica di configurazione."""
    api_mode = os.getenv("API_MODE", "prod")
    has_openai = bool(os.getenv("OPENAI_API_KEY") and "YOUR_" not in os.getenv("OPENAI_API_KEY"))
    has_serpapi = bool(os.getenv("SERPAPI_API_KEY") and "YOUR_" not in os.getenv("SERPAPI_API_KEY"))

    print_trace("Healthcheck_Check", {
        "api_mode": api_mode,
        "openai_configured": has_openai,
        "serpapi_configured": has_serpapi
    })

    return {
        "status": "healthy",
        "api_mode": api_mode,
        "config": {
            "openai_api_key_configured": has_openai,
            "serpapi_api_key_configured": has_serpapi
        }
    }
