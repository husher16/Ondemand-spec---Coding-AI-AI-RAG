import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import chromadb
from config import Config
from custom_embedding import CustomEmbeddingFunction

class Database:
    def __init__(self):
        # Inizializza la funzione di embedding personalizzata
        self.local_ef = CustomEmbeddingFunction()
        
        # Inizializza il client persistente di ChromaDB
        self.client = chromadb.PersistentClient(path=Config.PERSISTENT_DIR)

        # ✅ Ora ChromaDB accetta correttamente la funzione di embedding
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            embedding_function=self.local_ef  # ✅ Funziona perché è un oggetto con __call__()
        )

    def add_documents(self, documents, metadatas, ids):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_text, n_results=1):
        return self.collection.query(query_texts=[query_text], n_results=n_results)

    def get_tracked_files(self):
        """Get all unique files and their metadata from the database"""
        result = self.collection.get()
        tracked_files = {}

        if result and result["metadatas"]:
            for metadata in result["metadatas"]:
                if metadata["source"] not in tracked_files:
                    tracked_files[metadata["source"]] = {
                        "hash": metadata["hash"],
                        "last_modified": metadata["last_modified"],
                        "source": metadata["source"],
                    }

        return tracked_files

    def remove_document_by_source(self, source):
        """Remove all entries for a specific source file"""
        result = self.collection.get(where={"source": source})
        if result and result["ids"]:
            self.collection.delete(ids=result["ids"])

    def get_stats(self):
        result = self.collection.get()
        valori_distinti = set(d["source"] for d in result["metadatas"])
        numero_files = len(valori_distinti)

        stats = {
            "numero_totale_documenti": self.collection.count(),
            "nome_collezione": self.collection.name,
        }
        return f"""
            Nome Collezione: {stats['nome_collezione']} 
            Numero totale Frammenti: {stats['numero_totale_documenti']}
            Numero Files Elaborati: {numero_files}
        """
