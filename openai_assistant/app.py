"""
Entry point per l'interfaccia web Chainlit del progetto OpenAI Assistant.

Esecuzione:
    chainlit run app.py -w
"""
import sys
from pathlib import Path

# Assicura che la directory del progetto sia nel PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from virtual_assistant import on_chat_start, main

__all__ = ["on_chat_start", "main"]
