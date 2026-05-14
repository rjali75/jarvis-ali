"""Tool registry: decorateur @tool qui auto-extrait les metadonnees d'une fonction."""
import inspect
from typing import Callable

# Registre global : nom du tool -> {function, schema}
_TOOLS: dict[str, dict] = {}


def tool(func: Callable) -> Callable:
    """Decorateur qui enregistre une fonction comme outil pour Jarvis.

    Auto-extrait :
    - Le nom (depuis func.__name__)
    - La description (depuis le docstring)
    - Les parametres (depuis les annotations de type)
    """
    name = func.__name__
    docstring = (func.__doc__ or "").strip()
    description = docstring.split("\n")[0] if docstring else f"Fonction {name}"

    # Extraire les parametres et leur type
    sig = inspect.signature(func)
    properties = {}
    required = []

    type_map = {int: "integer", str: "string", float: "number", bool: "boolean"}

    for param_name, param in sig.parameters.items():
        param_type = param.annotation
        json_type = type_map.get(param_type, "string")
        properties[param_name] = {"type": json_type, "description": param_name}

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    schema = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }
    }

    _TOOLS[name] = {"function": func, "schema": schema}
    return func


def get_schemas() -> list[dict]:
    """Retourne les schemas JSON de tous les outils enregistres."""
    return [t["schema"] for t in _TOOLS.values()]


def execute_tool(name: str, arguments: dict) -> str:
    """Execute un outil par son nom avec les arguments donnes. Retourne le resultat en str."""
    if name not in _TOOLS:
        return f"Erreur: outil '{name}' inconnu"

    func = _TOOLS[name]["function"]
    try:
        result = func(**arguments)
        return str(result) if result is not None else "Fait."
    except Exception as e:
        return f"Erreur lors de l'execution de {name}: {e}"


def list_tools() -> list[str]:
    """Retourne la liste des noms d'outils disponibles."""
    return list(_TOOLS.keys())