import requests

from src.config import DOSSIER_BRUT


def telecharger(url, nom_fichier):
    chemin = DOSSIER_BRUT / nom_fichier
    if chemin.exists():
        return chemin
    DOSSIER_BRUT.mkdir(parents=True, exist_ok=True)
    reponse = requests.get(url, timeout=60)
    reponse.raise_for_status()
    chemin.write_bytes(reponse.content)
    return chemin
