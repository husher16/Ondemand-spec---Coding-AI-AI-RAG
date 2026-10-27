import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # chromadb
    DOCUMENTS_DIR = "resumes"
    COLLECTION_NAME = "CVs"
    PERSISTENT_DIR = "data/chromadb"
    
    # Embeddings
    # 📌 Scelta del provider di embedding: "openai", "local", "ollama"
    EMBEDDING_PROVIDER = "openai"  # Cambia in "openai" o "ollama" se necessario

    # 📌 Nome del modello
    MODEL_NAME = "text-embedding-3-small"  # Cambia in "text-embedding-3-small" per OpenAI, "nomic-embed-text" per Ollama, all-MiniLM-L6-v2

    # 📌 Percorso locale per i modelli (solo se EMBEDDING_PROVIDER="local")
    MODEL_PATH = "modelli/mio_modello"

    # 📌 Configurazione OpenAI (solo se EMBEDDING_PROVIDER="openai")
    OPENAI_EMBEDDINGS_KEY = os.getenv("OPENAI_API_KEY", "")
   
    # Completamento
    ### ollama
    # LLM_MODEL = "llama3.2"  # "deepseek-r1:1.5b"  # "llama3.2" #  "deepseek-r1:1.5b" deepseek-r1:8b
    # LLM_MODEL_LOW = "llama3.2"  # "deepseek-r1:1.5b"  # "llama3.2" #  "deepseek-r1:1.5b"
    # AI_API_URL = "http://localhost:11434/v1"
    # AI_API_KEY = "ollama"
    ### openai
    LLM_MODEL = "gpt-4o"
    LLM_MODEL_LOW = "gpt-4o-mini"
    AI_API_URL = "https://api.openai.com/v1/"
    AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
