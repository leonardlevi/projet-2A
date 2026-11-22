# Données

- `raw/` : fichiers bruts, tels qu'ils ont été téléchargés. Ils sont conservés dans le dépôt pour que le projet se relance sans dépendre des sites d'origine.
- `processed/departements.csv` : la table finale utilisée par le rapport, une ligne par département métropolitain (96 lignes).

Le code qui télécharge et nettoie les sources est dans `src/collecte.py` et `src/nettoyage.py`.

## Sources

### Obésité : EpiCov (DREES)

- **Fichier :** `raw/epicov_v2.csv`
- **Adresse :** https://data.drees.solidarites-sante.gouv.fr (jeu de données `indicateurs-epicov`)
- **Période :** vague 2 de l'enquête, octobre à décembre 2020
- **Maille :** département de résidence
- **Nettoyage :** on garde la part de personnes obèses (indice de masse corporelle), avec son intervalle de confiance à 95 %, multipliée par 100 pour avoir des pourcentages.
- **Limites :** c'est une enquête sur un échantillon, donc l'estimation de chaque département est imprécise (l'intervalle de confiance fait environ 3 points de chaque côté). Les réponses sont probablement déclaratives, et la période (2020) est particulière.

### Accès aux médecins : APL (DREES)

- **Fichier :** `raw/apl_medecins.xlsx` (feuille « APL 2022 »)
- **Adresse :** https://data.drees.solidarites-sante.gouv.fr (jeu de données `530_l-accessibilite-potentielle-localisee-apl`)
- **Année :** 2022
- **Maille d'origine :** commune
- **Nettoyage :** le département est déduit du code de la commune, puis on calcule la moyenne de l'APL des communes pondérée par leur population standardisée.
- **Limites :** la moyenne cache les écarts à l'intérieur d'un département (une commune isolée et une ville du même département comptent chacune selon leur population).

### Pauvreté et niveau de vie : Filosofi (INSEE)

- **Fichier :** `raw/filosofi_2021.zip`
- **Adresse :** https://www.insee.fr/fr/statistiques/7756729
- **Année :** 2021
- **Maille :** département
- **Nettoyage :** on garde deux mesures, le taux de pauvreté à 60 % de la médiane (`PR_MD60`) et le niveau de vie médian (`MED_SL`).
- **Limites :** le taux de pauvreté n'est pas fourni pour la Guadeloupe.

### Population : estimations de population (INSEE)

- **Fichier :** `raw/population_dep_2025.xlsx` (feuille « 2021 »)
- **Adresse :** https://www.insee.fr/fr/statistiques/8331297
- **Année utilisée :** 2021
- **Maille :** département
- **Nettoyage :** on garde la population totale et la part des 60 ans et plus, calculée à partir des tranches d'âge.

### Densité : API geo.api.gouv.fr

- **Fichier :** `raw/communes_geo_api.json`
- **Adresse :** https://geo.api.gouv.fr/communes
- **Maille d'origine :** commune
- **Nettoyage :** on additionne la population et la surface (en hectares) des communes de chaque département, puis `densité = population / (surface / 100)`, en habitants par km².
- **Limites :** la population de cette API correspond à la dernière version disponible, pas forcément à 2021.

### Régions : API geo.api.gouv.fr

- **Fichier :** `raw/departements_regions.json`
- **Adresse :** https://geo.api.gouv.fr/departements
- **Utilité :** relie chaque département à sa région (code INSEE). Elle sert aux effets fixes de la régression et au graphique par région.

### Restaurants et salles de sport : BPE (INSEE)

- **Fichier :** `raw/bpe_2025.zip`
- **Adresse :** https://api.insee.fr/melodi/file/DS_BPE/DS_BPE_2025_CSV_FR (base permanente des équipements 2025)
- **Année :** 2025
- **Maille :** département
- **Nettoyage :** on garde deux types d'équipements, `A504` (restaurants et restauration rapide) et `F120` (salles de remise en forme), et on compte les équipements de chaque département.
- **Limites :** le code `A504` mélange restaurants classiques et restauration rapide. On ne peut donc pas séparer les fast-foods avec cette source.

### Fast-foods : OpenStreetMap

- **Fichier :** `raw/osm_fastfoods_france.json`
- **Adresse :** https://overpass-api.de (requête dans `src/collecte.py`)
- **Date d'extraction :** 16 novembre 2026
- **Nettoyage :** la requête récupère tous les points `amenity=fast_food` de France, puis on les rattache à leur département avec les contours (jointure spatiale).
- **Limites :** OpenStreetMap est rempli par des bénévoles, donc la couverture peut varier d'un département à l'autre. Le résultat change avec le temps : le fichier est conservé tel quel pour que l'analyse reste identique. Le serveur Overpass est parfois lent ou en erreur, ce qui est une autre raison de garder le fichier.

### Contours des départements

- **Fichier :** `raw/departements.geojson`
- **Adresse :** https://github.com/gregoiredavid/france-geojson
- **Utilité :** rattacher les fast-foods à leur département, et dessiner les cartes. Il ne couvre que la France métropolitaine, ce qui explique que la table finale ait 96 départements.

## Table finale : `processed/departements.csv`

| Colonne | Contenu |
|---|---|
| `dep` | code du département (texte : `01`, `2A`, `75`...) |
| `region` | code INSEE de la région (texte) |
| `obesite`, `obesite_bas`, `obesite_haut` | obésité en % et bornes de l'intervalle de confiance à 95 % |
| `taux_pauvrete` | taux de pauvreté, en % |
| `niveau_vie_median` | niveau de vie médian, en euros par an |
| `population` | population en 2021 |
| `part_60_plus` | part des 60 ans et plus, en % |
| `densite` | habitants par km² |
| `apl` | accessibilité aux médecins généralistes (plus c'est haut, meilleur est l'accès) |
| `restauration`, `salles_sport`, `fastfoods` | nombre d'équipements |
| `restauration_10k`, `salles_sport_10k`, `fastfoods_10k` | équipements pour 10 000 habitants |

Il faut lire `dep` et `region` comme du texte (`dtype={"dep": str, "region": str}`), sinon `01` devient `1`.

## Reconstruire la table

Depuis la racine du projet :

```python
from src.nettoyage import table_finale

table_finale()
```

La fonction lit les fichiers de `raw/`, assemble toutes les sources et réécrit `processed/departements.csv`. Aucun téléchargement n'est fait tant que les fichiers sont présents.

Pour retélécharger une source, il suffit de supprimer son fichier de `raw/` : la fonction le télécharge de nouveau. Pour les fast-foods, ce n'est pas conseillé : le résultat changerait et le serveur est instable.
