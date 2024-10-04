import json

from django.core.management.base import BaseCommand
import pandas as pd


def get_default_pathogens():
    pathogen = pd.read_csv("raw_public_data/tbl_pathogen.csv", encoding="windows-1251")
    health = pd.read_csv("raw_public_data/tbl_health.csv", encoding="windows-1251")
    # NOTE: HEALTH has been modified 'pathogen_id' is now 'pathogen_group'!!
    #       i.e. Rotavirus -> Viruses, jejuni -> Bacteria, parvum -> Protozoa
    #       this reflects the usage done until now and solve the problem of having too few data available...
    health = health.loc[:, ["group", "infection_to_illness", "dalys_per_case"]]
    dose_response = pd.read_csv("raw_public_data/tbl_doseResponse.csv", encoding="windows-1251")
    dose_response = dose_response.loc[:, ["pathogen_id", "best_fit_model", "k", "alpha", "n50"]]
    pathogen = pd.merge(pathogen, health, on="group", how="left")
    return pd.merge(pathogen, dose_response.rename(columns=dict(pathogen_id="id")), on="id", how="left")


def get_default_sources():
    return pd.read_csv("raw_public_data/tbl_waterSource.csv", encoding="windows-1251")


def get_default_inflows():
    inflows = pd.read_csv("raw_public_data/tbl_inflow.csv", encoding="windows-1251")
    pathogens = pd.read_csv("raw_public_data/tbl_pathogen.csv", encoding="windows-1251")
    sources = pd.read_csv("raw_public_data/tbl_waterSource.csv", encoding="windows-1251")
    inflows = pd.merge(inflows, sources, left_on="source_id", right_on="id", how="left").rename(columns={"name": "source_name"})
    inflows = pd.merge(inflows, pathogens, left_on="pathogen_id", right_on="id", how="left").rename(columns={"name": "pathogen_name"})
    return inflows.loc[:, ["source_name", "pathogen_name", "min", "max"]]


def get_default_treatments():
    treatments = pd.read_csv("raw_public_data/tbl_treatment.csv", encoding="windows-1251")
    logremovals = pd.read_csv("raw_public_data/tbl_logRemoval.csv", encoding="windows-1251")
    logremovals = logremovals.loc[:, ["treatment_id", "min", "max", "pathogen_group"]]
    for grp_name, grp in logremovals.groupby("pathogen_group"):
        grp = grp.loc[:, ["treatment_id", "min", "max"]].rename(
            columns=dict(treatment_id="id", min=f"{grp_name.lower()}_min", max=f"{grp_name.lower()}_max"))
        treatments = pd.merge(treatments, grp, on="id", how="outer")
    return treatments


def get_default_exposures():
    return pd.read_csv("raw_public_data/tbl_ingestion.csv", encoding="windows-1251")


def save_as_json(data: dict, destination: str):
    with open(destination, "w") as f:
        json.dump(data, f)


class Command(BaseCommand):
    help = "Create the default static data of qmra"

    def handle(self, *args, **options):
        default_pathogens = get_default_pathogens()
        default_pathogens = {d["name"]: d for d in default_pathogens.replace({float("nan"): None}).to_dict(orient="records")}
        save_as_json(default_pathogens, "qmra/static/data/default-pathogens.json")
        default_inflows = get_default_inflows()
        default_inflows = {k: d.to_dict(orient="records") for k, d in default_inflows.replace({float("nan"): None}).groupby("source_name")}
        save_as_json(default_inflows, "qmra/static/data/default-inflows.json")
        default_treatments = get_default_treatments()
        default_treatments = {d["name"]: d for d in default_treatments.replace({float("nan"): None}).to_dict(orient="records")}
        save_as_json(default_treatments, "qmra/static/data/default-treatments.json")
        default_sources = get_default_sources()
        default_sources = {d["name"]: d for d in default_sources.replace({float("nan"): None}).to_dict(orient="records")}
        save_as_json(default_sources, "qmra/static/data/default-sources.json")
        default_exposures = get_default_exposures()
        default_exposures = {d["name"]: d for d in default_exposures.replace({float("nan"): None}).to_dict(orient="records")}
        save_as_json(default_exposures, "qmra/static/data/default-exposures.json")


if __name__ == '__main__':
    Command().handle()