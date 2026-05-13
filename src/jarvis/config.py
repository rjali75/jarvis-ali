"""Configuration globale de Jarvis."""
import os
from dotenv import load_dotenv

load_dotenv()

# Modèle LLM utilise (Groq)
MODEL = "llama-3.3-70b-versatile"

# Parametres de generation
TEMPERATURE = 0.7

# Cle API (lue depuis .env)
GROQ_API_KEY = os.environ["GROQ_API_KEY"]