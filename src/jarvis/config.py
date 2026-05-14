"""Configuration globale de Jarvis."""
import os
from dotenv import load_dotenv

load_dotenv()

# Modele LLM utilise (Groq)
MODEL = "openai/gpt-oss-120b"

# Parametres de generation
TEMPERATURE = 0.7

# Cles API (lues depuis .env)
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")  # optionnelle (None si absente)