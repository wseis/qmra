from django.core.management.base import BaseCommand, CommandError
from django.db.models import ForeignKey
import sqlite3
from qmra.treatment.models import *
from qmra.source.models import *
from qmra.risk_assessment.models import *
import re
import pandas as pd

pattern = re.compile(r'(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])')


def rename_column(name, model_name, model_fields):
    snake_name = pattern.sub('_', name).lower()
    if snake_name in model_fields:
        return snake_name
    elif snake_name + "_id" in model_fields:
        return snake_name + "_id"
    elif name.replace(model_name, "").lower() in model_fields:
        return name.replace(model_name, "").lower()
    return name


def logremoval_converter(r: dict):
    r.update({"reference": Reference.objects.get(id=r["reference"])})
    r.update({"reference": Treatment.objects.get(id=r["reference"])})
    r.update({"pathogen_group": PathogenGroup.objects.get(id=r["pathogen_group"])})
class Command(BaseCommand):
    help = "Create the public db qmra.db"

    def handle(self, *args, **options):
        # con = sqlite3.connect("qmra.db")
        for data in [
            dict(m=Reference, f="tbl_reference.csv"),
            dict(m=PathogenGroup, f="tbl_pathogenGroup.csv"),
            dict(m=Pathogen, f="tbl_pathogen.csv"),
            dict(m=Treatment, f="tbl_treatment.csv"),
            dict(m=LogRemoval, f="tbl_logRemoval.csv"),
            dict(m=WaterSource, f="tbl_waterSource.csv"),
            dict(m=Inflow, f="tbl_inflow.csv"),
            dict(m=Health, f="tbl_health.csv"),
            dict(m=DoseResponse, f="tbl_doseResponse.csv"),
            dict(m=ExposureScenario, f="tbl_ingestion.csv"),
        ]:
            model = data["m"]
            df = pd.read_csv(f"raw_public_data/{data['f']}", encoding="windows-1251")
            model_fields = {
                f"{f.name}_{f.field_name}" if f.is_relation and not isinstance(f, ForeignKey)
                else f.name if not isinstance(f, ForeignKey) else f.name + "_id"
                for f in model._meta.get_fields() if not f.is_relation or isinstance(f, ForeignKey)}
            df = df.rename(columns=lambda c: rename_column(c, model.__qualname__, model_fields))
            self.stdout.write(f"{model} -- {model_fields} -- {df.columns}")
            df = df[list(model_fields & set(df.columns))]
            # df.to_sql(model._meta.db_table, con, index=False, if_exists="append")
            model.objects.bulk_create([model(**{k: v for k, v in r.items() if not pd.isna(v)}) for r in df.to_dict('records')])
        # con.close()