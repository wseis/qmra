from django.contrib import admin
from .models import Treatment, QA, Text, RiskAssessment, User, LogRemoval, Exposure, Reference, SourceWater, Pathogen, PathogenGroup, Health, Inflow, Guideline, DoseResponse
# Register your models here.

from import_export.admin import ImportExportModelAdmin
# Register your models here.

@admin.register(SourceWater)
class SourceWaterAdmin(ImportExportModelAdmin):
    pass


@admin.register(Treatment)
class TreatmentAdmin(ImportExportModelAdmin):
    list_display=("id", "name", "group", "category")
    pass

@admin.register(Reference)
class ReferenceAdmin(ImportExportModelAdmin):
    list_display=("id", "name", "link")
    pass

@admin.register(PathogenGroup)
class PathogenGroupAdmin(ImportExportModelAdmin):
    pass


@admin.register(Pathogen)
class PathogenAdmin(ImportExportModelAdmin):
    pass

@admin.register(LogRemoval)
class LogRemovalAdmin(ImportExportModelAdmin):
    list_display=("id", "treatment", "pathogen_group", "min", "max", "reference")
    pass

@admin.register(Exposure)
class ExposureAdmin(ImportExportModelAdmin):
    pass

@admin.register(Inflow)
class InflowAdmin(ImportExportModelAdmin):
    list_display=("id", "pathogen", "water_source", "min", "max")
    pass
@admin.register(Guideline)
class GuidelineAdmin(ImportExportModelAdmin):
    pass
@admin.register(Health)
class HealthAdmin(ImportExportModelAdmin):
    pass
@admin.register(DoseResponse)
class DoseResponseAdmin(ImportExportModelAdmin):
    pass

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    list_display=("id", "username")
    
  #  pass
#admin.site.register(Treatment)
admin.site.register(RiskAssessment)
#admin.site.register(User)
admin.site.register(Text)
admin.site.register(QA)
#admin.site.register(LogRemoval)
#admin.site.register(Exposure)
#admin.site.register(Reference)
#admin.site.register(SourceWater)
#admin.site.register(PathogenGroup)