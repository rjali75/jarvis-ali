"""Jarvis - Phase 0: premier contact avec un LLM."""
import os
from dotenv import load_dotenv
from groq import Groq
from rich.console import Console
from rich.markdown import Markdown

load_dotenv()
console = Console()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """Tu es Jarvis, l'assistant personnel d'Ali.
Tu es concis, un peu sarcastique, et tu réponds en français par défaut.
Ali est étudiant en BUT Informatique. Il code, joue au basket, et construit des trucs."""


def ask(user_message: str) -> str:
    """Pose une question au LLM et retourne la réponse."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    console.print("[bold cyan]Jarvis v0.0.1[/bold cyan] - tape 'exit' pour quitter\n")
    while True:
        user_input = console.input("[bold green]Toi:[/bold green] ")
        if user_input.lower() in ("exit", "quit", "q"):
            console.print("[dim]A plus, BOSS.[/dim]")
            break
        reply = ask(user_input)
        console.print(f"\n[bold magenta]Jarvis:[/bold magenta]")
        console.print(Markdown(reply))
        console.print()