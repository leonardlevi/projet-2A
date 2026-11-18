import requests

from src.config import DOSSIER_BRUT

URL_OVERPASS = "https://overpass-api.de/api/interpreter"

REQUETE_FASTFOODS = """
[out:json][timeout:300];
area["ISO3166-1"="FR"][admin_level=2]->.france;
nwr["amenity"="fast_food"](area.france);
out center;
"""


def telecharger(url, nom_fichier):
    chemin = DOSSIER_BRUT / nom_fichier
    if chemin.exists():
        return chemin
    DOSSIER_BRUT.mkdir(parents=True, exist_ok=True)
    reponse = requests.get(url, timeout=60)
    reponse.raise_for_status()
    chemin.write_bytes(reponse.content)
    return chemin


def telecharger_fastfoods():
    chemin = DOSSIER_BRUT / "osm_fastfoods_france.json"
    if chemin.exists():
        return chemin
    DOSSIER_BRUT.mkdir(parents=True, exist_ok=True)
    entetes = {"User-Agent": "projet-etudiant-python"}
    reponse = requests.post(
        URL_OVERPASS, data={"data": REQUETE_FASTFOODS}, headers=entetes, timeout=400
    )
    reponse.raise_for_status()
    chemin.write_bytes(reponse.content)
    return chemin
