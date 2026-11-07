import datetime
from typing import Any, Optional


def print_trace(step_name: str, details: Optional[dict[str, Any]] = None, divider: str = "*", width: int = 80) -> None:
    """
    Stampa un blocco di tracing visivo per monitorare il flusso di esecuzione dell'agente.
    Include timestamp, nome dello step/tool e dettagli opzionali.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(divider * width)
    print(f"[{now}] TRACE: {step_name}")
    if details:
        for key, value in details.items():
            print(f"   * {key}: {value}")
    print(divider * width)
