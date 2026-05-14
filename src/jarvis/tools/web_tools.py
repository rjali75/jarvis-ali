"""Outils de recherche web via Tavily (designe pour les agents IA)."""
from tavily import TavilyClient

from jarvis.config import TAVILY_API_KEY
from jarvis.tools.registry import tool


@tool
def web_search(query: str) -> str:
    """Cherche sur le web et retourne les meilleurs resultats.

    A utiliser ABSOLUMENT pour :
    - L'actualite recente (sports, news, evenements en cours)
    - Des informations factuelles dont tu n'es pas sur
    - Des definitions de termes recents
    - Des questions sur des personnes, lieux, evenements specifiques
    - Tout ce qui depasse ta date de cutoff

    Ne reponds jamais "je ne sais pas" sans avoir essaye cet outil avant.
    """
    if not TAVILY_API_KEY:
        return "Erreur : la cle TAVILY_API_KEY n'est pas configuree."

    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query, max_results=5, search_depth="basic")

        results = response.get("results", [])
        if not results:
            return f"Aucun resultat pour '{query}'."

        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "Sans titre")
            content = r.get("content", "")[:300]
            url = r.get("url", "")
            formatted.append(f"{i}. {title}\n   {content}\n   Source: {url}")

        # Tavily fournit aussi un "answer" synthetique parfois
        answer = response.get("answer")
        if answer:
            formatted.insert(0, f"Reponse rapide : {answer}\n")

        return "\n\n".join(formatted)
    except Exception as e:
        return f"Erreur de recherche : {e}"