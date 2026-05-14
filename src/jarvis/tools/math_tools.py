"""Outils mathematiques."""
import numexpr as ne

from jarvis.tools.registry import tool


@tool
def calculate(expression: str) -> str:
    """Evalue une expression mathematique de maniere precise et securisee.

    Supporte :
    - Operations basiques : +, -, *, /, ** (puissance)
    - Fonctions : sqrt, sin, cos, tan, log, exp, abs
    - Constantes : pi, e

    Exemples d'utilisation :
    - calculate("2 + 3 * 4") -> 14
    - calculate("sqrt(144)") -> 12
    - calculate("sin(pi/2)") -> 1.0
    - calculate("(15% de 250)") NE MARCHE PAS, utiliser calculate("0.15 * 250")
    - calculate("log(1000) / log(10)") -> 3 (pour log base 10)

    Utilise cet outil DES QU'IL Y A UN CALCUL, meme simple. Ne calcule jamais a la main.
    """
    try:
        result = ne.evaluate(expression)
        # numexpr retourne un array numpy meme pour un scalaire
        result_value = result.item() if hasattr(result, "item") else result
        return f"{expression} = {result_value}"
    except Exception as e:
        return f"Erreur de calcul pour '{expression}' : {e}"