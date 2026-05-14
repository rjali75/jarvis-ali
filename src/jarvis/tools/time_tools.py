"""Outils temporels."""
from datetime import datetime
from jarvis.tools.registry import tool


@tool
def get_current_time() -> str:
    """Retourne la date et l'heure actuelle."""
    return datetime.now().strftime("%H:%M:%S le %d/%m/%Y")