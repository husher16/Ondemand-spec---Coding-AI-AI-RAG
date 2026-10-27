import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
import re
import numpy as np
from custom_embedding import CustomEmbeddingFunction
from sklearn.metrics.pairwise import cosine_similarity

#
# 📌 Spiegazione Generale:
# Questo codice implementa un sistema di "semantic chunking", ovvero un modo intelligente di dividere un testo lungo in parti più piccole (chunk)
# che hanno senso semantico. Usa modelli OpenAI o locali per calcolare gli embedding e individuare i punti di separazione in base al significato del testo.
#

class SemanticChunking:
    def __init__(self, breakpoint_percentile=95, buffer_size=1):
        """
        Inizializza il sistema di chunking semantico.
        - breakpoint_percentile: Percentile per determinare i punti di separazione.
        - buffer_size: Numero di frasi da considerare per il contesto.
        """
        self.embedding_function = CustomEmbeddingFunction()  # 📌 Riutilizziamo CustomEmbeddingFunction
        self.breakpoint_percentile = breakpoint_percentile
        self.buffer_size = buffer_size

    def _process_sentences(self, text):
        """
        Divide il testo in frasi e crea una lista con il loro contesto.
        """
        sentences = [
            {"sentence": s, "index": i}
            for i, s in enumerate(re.split(r"(?<=[.?!])\s+", text))
        ]

        # 📌 Combina ogni frase con il suo contesto
        for i, current in enumerate(sentences):
            context_range = range(
                max(0, i - self.buffer_size),
                min(len(sentences), i + self.buffer_size + 1),
            )
            current["combined_sentence"] = " ".join(
                sentences[j]["sentence"] for j in context_range
            )

        return sentences

    def _calculate_distances(self, sentences):
        """
        Calcola gli embedding per tutte le frasi combinate,
        utilizzando CustomEmbeddingFunction per supportare sia OpenAI che modelli locali.
        """
        embeddings = self.embedding_function(
            [s["combined_sentence"] for s in sentences]
        )

        # 📌 Calcola le distanze coseno tra frasi consecutive
        distances = []
        for i in range(len(sentences) - 1):
            distance = 1 - cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
            distances.append(distance)

        return distances

    def chunk_text(self, text):
        """
        Divide il testo in chunk basati sulla similarità semantica.
        """
        # 📌 Processa le frasi
        sentences = self._process_sentences(text)
        print("SENTENCES:", sentences[:2])

        # 📌 Calcola le distanze tra le frasi
        distances = self._calculate_distances(sentences)
        print("DISTANCES:", distances[:2])

        # 📌 Determina i punti di divisione basati sul percentile
        threshold = np.percentile(distances, self.breakpoint_percentile)
        split_points = [i for i, d in enumerate(distances) if d > threshold]
        print("SPLIT POINTS: ", split_points)

        # 📌 Crea i chunk finali
        chunks = []
        start = 0
        for point in split_points + [len(sentences) - 1]:
            chunk = " ".join(s["sentence"] for s in sentences[start : point + 1])
            print("CHUNK: ", chunk)
            chunks.append(chunk)
            start = point + 1

        return chunks
