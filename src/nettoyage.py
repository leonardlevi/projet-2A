import zipfile

import pandas as pd

from src.collecte import telecharger

URL_EPICOV_V2 = (
    "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/"
    "catalog/datasets/indicateurs-epicov/attachments/indicateurs_epicov_v2_csv"
)
URL_APL = (
    "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "530_l-accessibilite-potentielle-localisee-apl/attachments/"
    "indicateur_d_apl_aux_medecins_generalistes_xlsx"
)
URL_FILOSOFI = (
    "https://www.insee.fr/fr/statistiques/fichier/7756729/"
    "base-cc-filosofi-2021-geo2025_csv.zip"
)
URL_POPULATION = (
    "https://www.insee.fr/fr/statistiques/fichier/8331297/"
    "estim-pop-dep-sexe-gca-1975-2025.xlsx"
)
URL_COMMUNES = (
    "https://geo.api.gouv.fr/communes?fields=code,codeDepartement,population,surface&format=json"
)
URL_REGIONS = "https://geo.api.gouv.fr/departements?fields=code,nom,codeRegion"


def obesite_epicov():
    chemin = telecharger(URL_EPICOV_V2, "epicov_v2.csv")
    df = pd.read_csv(chemin, sep=";", decimal=",", dtype={"m_varX1": str})

    est_obese = df["m_varY"].str.startswith("Ob")
    est_imc = df["varY"].str.startswith("Indice de masse corporelle")
    est_dep = df["varX1"] == "Département de résidence"
    df = df[est_obese & est_imc & est_dep]

    return pd.DataFrame(
        {
            "dep": df["m_varX1"].str.zfill(2),
            "obesite": df["est"] * 100,
            "obesite_bas": df["est_inf"] * 100,
            "obesite_haut": df["est_sup"] * 100,
        }
    ).reset_index(drop=True)


def apl_departements():
    chemin = telecharger(URL_APL, "apl_medecins.xlsx")
    df = pd.read_excel(chemin, sheet_name="APL 2022", header=None, skiprows=10, dtype={0: str})
    df = df[[0, 2, 6]]
    df.columns = ["commune", "apl", "pop_standardisee"]
    df = df.dropna()
    df["apl"] = df["apl"].astype(float)
    df["pop_standardisee"] = df["pop_standardisee"].astype(float)

    df["dep"] = df["commune"].str[:2]
    df.loc[df["commune"].str.startswith("97"), "dep"] = df["commune"].str[:3]

    df["apl_x_pop"] = df["apl"] * df["pop_standardisee"]
    par_dep = df.groupby("dep")[["apl_x_pop", "pop_standardisee"]].sum()
    apl = par_dep["apl_x_pop"] / par_dep["pop_standardisee"]
    return apl.rename("apl").reset_index()


def pauvrete_filosofi():
    chemin = telecharger(URL_FILOSOFI, "filosofi_2021.zip")
    with zipfile.ZipFile(chemin) as archive:
        with archive.open("DS_FILOSOFI_CC_data.csv") as f:
            df = pd.read_csv(f, sep=";", dtype={"GEO": str})

    df = df[df["GEO_OBJECT"] == "DEP"]
    df = df[df["FILOSOFI_MEASURE"].isin(["PR_MD60", "MED_SL"])]
    df = df.pivot(index="GEO", columns="FILOSOFI_MEASURE", values="OBS_VALUE")

    return (
        df.rename(columns={"PR_MD60": "taux_pauvrete", "MED_SL": "niveau_vie_median"})
        .rename_axis(index="dep", columns=None)
        .reset_index()
    )


def population_insee():
    chemin = telecharger(URL_POPULATION, "population_dep_2025.xlsx")
    df = pd.read_excel(chemin, sheet_name="2021", header=None, dtype={0: str})
    df = df[df[1].notna() & df[0].notna()]
    df = df[~df[0].isin(["Départements"])]

    return pd.DataFrame(
        {
            "dep": df[0],
            "population": df[7].astype(float),
            "part_60_plus": (df[5] + df[6]).astype(float) / df[7].astype(float) * 100,
        }
    ).reset_index(drop=True)


def densite_departements():
    chemin = telecharger(URL_COMMUNES, "communes_geo_api.json")
    communes = pd.read_json(chemin, dtype={"code": str, "codeDepartement": str})
    par_dep = communes.groupby("codeDepartement")[["population", "surface"]].sum()
    densite = par_dep["population"] / (par_dep["surface"] / 100)
    return densite.rename("densite").rename_axis("dep").reset_index()


def regions_departements():
    chemin = telecharger(URL_REGIONS, "departements_regions.json")
    df = pd.read_json(chemin, dtype={"code": str, "codeRegion": str})
    return df.rename(columns={"code": "dep", "codeRegion": "region"})[["dep", "region"]]
