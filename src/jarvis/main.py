"""Jarvis - point d'entree de l'application."""
from groq import Groq
from rich.console import Console
from rich.markdown import Markdown

from jarvis.config import GROQ_API_KEY, MODEL, TEMPERATURE
from jarvis.conversation import Conversation
from jarvis.personality import SYSTEM_PROMPT

console = Console()


def main():
    client = Groq(api_key=GROQ_API_KEY)
    conversation = Conversation(client, SYSTEM_PROMPT, MODEL, TEMPERATURE)

    console.print("[bold cyan]Jarvis v0.1.2[/bold cyan] - Phase 1 complete")
    console.print("[dim]Commandes: 'exit' | '/reset' | '/compact' | '/stats'[/dim]\n")

    while True:
        try:
            user_input = console.input("[bold green]Toi:[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]A plus, BOSS.[/dim]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("exit", "quit", "q"):
            console.print("[dim]A plus, BOSS.[/dim]")
            break

        if cmd == "/reset":
            conversation.reset()
            console.print("[yellow]Memoire effacee. On repart de zero.[/yellow]\n")
            continue

        if cmd == "/compact":
            console.print("[dim]Compaction manuelle...[/dim]")
            if conversation.compact():
                console.print("[yellow]Historique compacte.[/yellow]\n")
            else:
                console.print("[dim]Pas assez de messages pour compacter.[/dim]\n")
            continue

        if cmd == "/stats":
            console.print(
                f"[dim]Messages: {conversation.message_count} | "
                f"Tours: {conversation.turn_count} | "
                f"Compactions effectuees: {conversation.compaction_count}[/dim]\n"
            )
            continue

        try:
            reply = conversation.send(user_input)
        except Exception as e:
            console.print(f"[red]Erreur: {e}[/red]\n")
            continue

        # Auto-compaction si on depasse le seuil
        if conversation.should_compact():
            console.print("[dim italic]Compaction automatique en cours...[/dim italic]")
            conversation.compact()
            console.print("[dim italic]Historique compacte.[/dim italic]")

        console.print(
            f"\n[bold magenta]Jarvis:[/bold magenta] "
            f"[dim](tour {conversation.turn_count}, {conversation.message_count} msgs)[/dim]"
        )
        console.print(Markdown(reply))
        console.print()


if __name__ == "__main__":
    main()