import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import os
import chromadb
from chromadb.api.types import EmbeddingFunction
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import openai
import ollama  # 📌 Importa Ollama per il supporto agli embedding locali su GPU
from config import Config

class CustomEmbeddingFunction(EmbeddingFunction):
    """
    Classe per generare embedding compatibili con ChromaDB.
    Supporta:
    - OpenAI (API)
    - Modelli locali (SentenceTransformer)
    - Modelli su Ollama (GPU locale)
    """
    def __init__(self):
        self.provider = Config.EMBEDDING_PROVIDER
        self.model_name = Config.MODEL_NAME
        self.model_path = Config.MODEL_PATH

        if self.provider == "openai":
            self._setup_openai()
        elif self.provider == "local":
            self._setup_local_model()
        elif self.provider == "ollama":
            self._setup_ollama()
        else:
            raise ValueError(f"❌ ERRORE: EMBEDDING_PROVIDER '{self.provider}' non supportato!")

    def _setup_openai(self):
        """📌 Configura OpenAI Embeddings."""
        print(f"✅ Usando OpenAI Embeddings: {self.model_name}")
        openai.api_key = Config.OPENAI_EMBEDDINGS_KEY
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=Config.OPENAI_EMBEDDINGS_KEY,
            model_name=self.model_name
        )

    def _setup_local_model(self):
        """📌 Scarica e carica un modello locale se necessario."""
        if os.path.exists(self.model_path):
            print(f"✅ Modello locale '{self.model_name}' trovato, caricamento in corso...")
            self.embedding_function = SentenceTransformer(self.model_path)
        else:
            print(f"⏳ Scaricamento di '{self.model_name}' in corso...")
            self.embedding_function = SentenceTransformer(self.model_name)
            self.embedding_function.save_pretrained(self.model_path)
            print(f"✅ Modello salvato in '{self.model_path}'.")

    def _setup_ollama(self):
        """📌 Configura il supporto a Ollama per gli embedding."""
        print(f"✅ Usando modello Ollama: {self.model_name}")

    def __call__(self, texts):
        """
        Metodo richiesto da ChromaDB per generare embedding.
        - OpenAI: Chiama `OpenAIEmbeddingFunction`
        - Locale: Usa `SentenceTransformer`
        - Ollama: Usa `ollama.embeddings()`
        """
        if self.provider == "openai":
            return self.embedding_function(texts)

        if self.provider == "local":
            return self.embedding_function.encode(texts).tolist()

        if self.provider == "ollama":
            return [ollama.embeddings(model=self.model_name, prompt=text)["embedding"] for text in texts]
