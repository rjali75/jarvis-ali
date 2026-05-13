"""Gestion de la conversation avec memoire et compaction automatique."""
from groq import Groq


class Conversation:
    """Gere une conversation continue avec memoire et compaction automatique."""

    # Seuil de compaction : au-dela de N messages (hors system), on compacte
    COMPACT_THRESHOLD = 12
    # Nombre de messages recents a garder tels quels apres compaction
    KEEP_RECENT = 4

    def __init__(self, client: Groq, system_prompt: str, model: str, temperature: float = 0.7):
        self.client = client
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]
        self.compaction_count = 0

    def send(self, user_message: str) -> str:
        """Envoie un message et retourne la reponse, en gardant l'historique."""
        self.messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
        )

        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply

    def reset(self):
        """Reset la conversation, garde juste le system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]
        self.compaction_count = 0

    def should_compact(self) -> bool:
        """True si la conversation depasse le seuil et merite d'etre compactee."""
        return len(self.messages) - 1 > self.COMPACT_THRESHOLD

    def compact(self) -> bool:
        """Compacte la conversation : resume les vieux messages, garde les recents.
        Retourne True si une compaction a eu lieu."""
        non_system = self.messages[1:]
        if len(non_system) <= self.KEEP_RECENT:
            return False

        to_summarize = non_system[:-self.KEEP_RECENT]
        to_keep = non_system[-self.KEEP_RECENT:]

        # Construire le texte de la conversation a resumer
        conversation_text = "\n".join(
            f"{'Ali' if msg['role'] == 'user' else 'Jarvis'}: {msg['content']}"
            for msg in to_summarize
        )

        # Demander un resume au LLM
        summary_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Tu resumes des conversations de maniere concise et factuelle."
                },
                {
                    "role": "user",
                    "content": (
                        "Resume cette conversation entre Ali et son assistant Jarvis. "
                        "Garde les faits importants : ce qu'Ali a partage sur lui, "
                        "ses preferences, les decisions ou conclusions importantes. "
                        "Sois concis (max 200 mots), ecrit a la 3e personne.\n\n"
                        f"Conversation:\n{conversation_text}"
                    )
                }
            ],
            temperature=0.3,
        )
        summary = summary_response.choices[0].message.content

        # Reconstruire l'historique : system + faux echange (user/assistant) qui injecte le resume + recents
        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Resume de notre conversation jusqu'a present, pour memoire :"},
            {"role": "assistant", "content": summary},
            *to_keep
        ]
        self.compaction_count += 1
        return True

    @property
    def turn_count(self) -> int:
        """Nombre d'echanges user/assistant (le system prompt ne compte pas)."""
        return (len(self.messages) - 1) // 2

    @property
    def message_count(self) -> int:
        """Nombre total de messages dans la conversation (hors system)."""
        return len(self.messages) - 1