from django.core.management.base import BaseCommand, CommandError
from django.db.models import ForeignKey
import sqlite3
from qmra.treatment.models import *
from qmra.source.models import *
from qmra.risk_assessment.models import *
import json
import pandas as pd

MODELS = {
    "qmratool.user": "user.user",
    "qmratool.treatment": "treatment.treatment",
    "qmratool.logremoval": "treatment.logremoval",
    "qmratool.inflow": "source.inflow",
    "qmratool.sourcewater": "source.watersource",
    "qmratool.exposure": "scenario.exposurescenario",
    "qmratool.comparison": "risk_assessment.comparison",
    "qmratool.riskassessment": "risk_assessment.riskassessment",
}

# assumes that someone did:
# python manage.py dumpdata qmratool > dump-prod.json
# on prod...


class Command(BaseCommand):
    help = "Create the public db qmra.db"

    def handle(self, *args, **options):
        data = json.loads(open("dump-prod.json", "rb").read())
        converted = []
        for d in data:
            if d["model"] in MODELS:
                d["model"] = MODELS[d["model"]]
                if d["model"] == "source.watersource":
                    d["fields"]["name"] = d["fields"].pop("water_source_name")
                    d["fields"]["description"] = d["fields"].pop("water_source_description")
                if d["fields"].get("reference", None) == 51:
                    d["fields"]["reference"] = None
                converted += [d]
        json.dump(converted, open("dump-prod-converted.json", "w"))

if __name__ == '__main__':
    Command().handle()