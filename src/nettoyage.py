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
