from datetime import datetime
from typing import Dict, List, Optional


class CourseInfoTool:
    """
    Tool per ottenere informazioni dettagliate sui corsi dell'Accademia AI & Tech.
    """

    def __init__(self):
        # Simulazione del database corsi
        self.courses: Dict[str, Dict[str, any]] = {
            "python_ai": {
                "name": "Python & AI Foundations",
                "description": "Fondamenti di Python moderno, calcolo numerico con NumPy/Pandas e basi di machine learning.",
                "duration": "4 settimane",
                "price": 299.99,
            },
            "deep_learning": {
                "name": "Deep Learning & Computer Vision",
                "description": "Reti neurali convoluzionali (CNN), Vision Transformers e classificazione/segmentazione con PyTorch.",
                "duration": "6 settimane",
                "price": 449.99,
            },
            "rag_agents": {
                "name": "Agenti AI & Sistemi RAG Avanzati",
                "description": "Progettazione di pipeline RAG, database vettoriali, multi-agent frameworks e function calling.",
                "duration": "5 settimane",
                "price": 399.99,
            },
            "llm_engineering": {
                "name": "LLM Engineering & Fine-Tuning",
                "description": "Tecniche avanzate di prompt engineering, LoRA/QLoRA fine-tuning, quantizzazione e serving.",
                "duration": "4 settimane",
                "price": 429.99,
            },
            "mlops_cloud": {
                "name": "MLOps & Cloud AI Infrastructure",
                "description": "Deployment scalabile, Docker/Kubernetes, CI/CD per modelli AI e monitoraggio delle performance.",
                "duration": "5 settimane",
                "price": 379.99,
            },
        }

    def get_info(self, course_name: str) -> str:
        """
        Restituisce i dettagli del corso specificato.
        """
        key = course_name.lower().strip().replace(" ", "_").replace("-", "_")
        course = self.courses.get(key)

        # Ricerca per sottostringa se non trovato esattamente
        if not course:
            for k, val in self.courses.items():
                if key in k or key in val["name"].lower():
                    course = val
                    break

        if not course:
            disponibili = ", ".join([f"'{v['name']}'" for v in self.courses.values()])
            return (
                f"Corso '{course_name}' non trovato. "
                f"Ecco i corsi attualmente disponibili: {disponibili}."
            )

        return (
            f"Corso: {course['name']}\n"
            f"Descrizione: {course['description']}\n"
            f"Durata: {course['duration']}\n"
            f"Prezzo: €{course['price']:.2f}"
        )


class ScheduleTool:
    """
    Tool per consultare le prossime edizioni e date delle classi in partenza.
    """

    def __init__(self):
        # Simulazione database delle edizioni dei corsi
        self.classes: List[Dict[str, any]] = [
            {
                "course_name": "Python & AI Foundations",
                "start_date": "2025-06-01",
                "end_date": "2025-06-28",
                "spots_available": 12,
            },
            {
                "course_name": "Agenti AI & Sistemi RAG Avanzati",
                "start_date": "2025-06-15",
                "end_date": "2025-07-20",
                "spots_available": 8,
            },
            {
                "course_name": "Deep Learning & Computer Vision",
                "start_date": "2025-07-01",
                "end_date": "2025-08-10",
                "spots_available": 6,
            },
            {
                "course_name": "LLM Engineering & Fine-Tuning",
                "start_date": "2025-07-15",
                "end_date": "2025-08-15",
                "spots_available": 10,
            },
            {
                "course_name": "MLOps & Cloud AI Infrastructure",
                "start_date": "2025-08-01",
                "end_date": "2025-09-05",
                "spots_available": 15,
            },
        ]

    def get_classes(
        self,
        course_name: Optional[str] = None,
        start_date: Optional[str] = None,
    ) -> str:
        """
        Filtra e restituisce le classi in partenza in base al nome corso e/o alla data iniziale.
        """
        filtered = self.classes

        if course_name:
            cn = course_name.lower().strip()
            filtered = [
                c for c in filtered if cn in c["course_name"].lower()
            ]

        if start_date:
            filtered = [c for c in filtered if c["start_date"] >= start_date]

        if not filtered:
            return (
                "Nessuna classe trovata per i criteri specificati. "
                f"Tutte le classi programmate: {self.classes}"
            )

        result = "Prossime classi disponibili:\n"
        for c in filtered:
            result += (
                f"- {c['course_name']}: dal {c['start_date']} al {c['end_date']}, "
                f"Posti disponibili: {c['spots_available']}\n"
            )
        return result


class BookingTool:
    """
    Tool per la gestione e prenotazione di consulenze 1-to-1 con i docenti/mentor dell'accademia.
    """

    def __init__(self):
        # Simulazione degli slot disponibili dei docenti
        self.available_slots: List[Dict[str, str]] = [
            {
                "teacher_id": "T001",
                "teacher_name": "Prof. Alan Turing",
                "specialty": "Algoritmi & Deep Learning",
                "date": "2025-06-05",
                "time": "14:00",
            },
            {
                "teacher_id": "T002",
                "teacher_name": "Dott.ssa Ada Lovelace",
                "specialty": "Agenti AI & RAG",
                "date": "2025-06-08",
                "time": "15:30",
            },
            {
                "teacher_id": "T003",
                "teacher_name": "Ing. Claude Shannon",
                "specialty": "LLM Engineering & MLOps",
                "date": "2025-06-10",
                "time": "16:30",
            },
            {
                "teacher_id": "T002",
                "teacher_name": "Dott.ssa Ada Lovelace",
                "specialty": "Agenti AI & RAG",
                "date": "2025-06-12",
                "time": "11:00",
            },
        ]

    def book_consultation(
        self,
        date: str,
        time: str,
        teacher_id: Optional[str] = None,
    ) -> str:
        """
        Verifica la disponibilità ed effettua la prenotazione di una videochiamata con un docente.
        """
        available = [
            slot
            for slot in self.available_slots
            if slot["date"] == date and slot["time"] == time
        ]

        if teacher_id:
            available = [
                slot for slot in available if slot["teacher_id"] == teacher_id
            ]

        if not available:
            disp_str = "\n".join(
                [
                    f"- {s['teacher_name']} ({s['specialty']}): {s['date']} ore {s['time']} [ID: {s['teacher_id']}]"
                    for s in self.available_slots
                ]
            )
            return (
                "Mi dispiace, nessuna disponibilità trovata per la data e l'ora specificate.\n"
                f"Ecco gli slot attualmente disponibili:\n{disp_str}"
            )

        slot = available[0]
        # Rimuoviamo lo slot per simulare la prenotazione avvenuta
        self.available_slots.remove(slot)

        return (
            f"Prenotazione confermata con {slot['teacher_name']} ({slot['specialty']}) "
            f"per il {slot['date']} alle ore {slot['time']}."
        )
