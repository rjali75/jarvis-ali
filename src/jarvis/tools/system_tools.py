"""Outils systeme : lancer des applications sur le PC."""
import os
import shutil
import subprocess
from pathlib import Path

from jarvis.tools.registry import tool


# Mapping de noms naturels vers les commandes de lancement
KNOWN_APPS = {
    "spotify": "spotify",
    "musique": "spotify",
    "music": "spotify",
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "navigateur": "chrome",
    "browser": "chrome",
    "steam": "steam",
    "discord": "discord",
    "vscode": "code",
    "vs code": "code",
    "code": "code",
    "notepad": "notepad",
    "bloc-notes": "notepad",
    "calc": "calc",
    "calculatrice": "calc",
    "calculator": "calc",
    "explorer": "explorer",
    "explorateur": "explorer",
    "paint": "mspaint",
    "powershell": "powershell",
    "cmd": "cmd",
    "terminal": "cmd",
}


def _find_start_menu_shortcut(name: str) -> str | None:
    """Cherche un raccourci .lnk dans les Menus Demarrer Windows."""
    start_dirs = []
    if "APPDATA" in os.environ:
        start_dirs.append(Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs")
    if "PROGRAMDATA" in os.environ:
        start_dirs.append(Path(os.environ["PROGRAMDATA"]) / "Microsoft/Windows/Start Menu/Programs")

    name_lower = name.lower()
    for start_dir in start_dirs:
        if not start_dir.exists():
            continue
        try:
            for lnk in start_dir.rglob("*.lnk"):
                if name_lower in lnk.stem.lower():
                    return str(lnk)
        except Exception:
            continue
    return None


@tool
def open_app(app_name: str) -> str:
    """Lance une application sur le PC Windows.

    Sait lancer la plupart des apps installees (Spotify, Discord, Steam, Chrome,
    Firefox, Edge, VS Code, Notepad, Calculatrice, Paint, Explorer, etc.)
    en cherchant d'abord dans le PATH, puis dans le Menu Demarrer si besoin.

    Pour "lance ma musique" -> spotify. Pour "ouvre le web" -> chrome.
    Tu peux aussi passer un nom d'app non liste, on tentera de la trouver.
    """
    name = app_name.lower().strip()
    command = KNOWN_APPS.get(name, name)

    # Tentative 1 : app dans le PATH
    if shutil.which(command):
        try:
            subprocess.Popen(f'start "" "{command}"', shell=True)
            return f"'{app_name}' lance."
        except Exception:
            pass

    # Tentative 2 : raccourci dans le Menu Demarrer
    shortcut = _find_start_menu_shortcut(command)
    if shortcut:
        try:
            os.startfile(shortcut)
            return f"'{app_name}' lance via raccourci Menu Demarrer."
        except Exception as e:
            return f"Raccourci trouve mais erreur au lancement : {e}"

    # Tentative 3 : essai en aveugle (peut marcher pour les handlers de protocole)
    try:
        subprocess.Popen(f'start "" "{command}"', shell=True)
        return f"Tentative de lancement de '{app_name}'. Si rien ne se passe, l'app n'est pas installee."
    except Exception as e:
        return f"Impossible de lancer '{app_name}': {e}"


@tool
def list_known_apps() -> str:
    """Liste les applications que Jarvis sait lancer par nom naturel."""
    unique_commands = sorted(set(KNOWN_APPS.values()))
    return "Apps connues : " + ", ".join(unique_commands)