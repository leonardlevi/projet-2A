from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

DOSSIER_DONNEES = RACINE / "data"
DOSSIER_BRUT = DOSSIER_DONNEES / "raw"
DOSSIER_TRAITE = DOSSIER_DONNEES / "processed"
DOSSIER_FIGURES = RACINE / "figures"
